"""Etapas compartidas de Jenkins y Actions; solo opera sobre proyectos jg-ci-*.

Usa Python estandar en el coordinador; FastAPI y Pytest se ejecutan en Docker.
No monta carpetas del host: docker cp recupera los reportes del contenedor.
"""

import argparse
import json
import os
import re
import secrets
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate_run_id(value):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", value):
        raise ValueError("CI_RUN_ID requiere 1-48 letras minusculas, numeros o guiones")
    return value


def validate_report(path):
    suites = ET.parse(path).getroot()
    tests = sum(int(s.get("tests", 0)) for s in suites.iter("testsuite"))
    skipped = sum(int(s.get("skipped", 0)) for s in suites.iter("testsuite"))
    failures = sum(
        int(s.get("failures", 0)) + int(s.get("errors", 0))
        for s in suites.iter("testsuite")
    )
    if tests == 0 or skipped or failures:
        raise RuntimeError(
            "CI requiere pruebas ejecutadas sin fallos ni pruebas omitidas"
        )
    return tests


class Pipeline:
    def __init__(self, run_id):
        self.run_id = validate_run_id(run_id)
        self.project = f"jg-ci-{run_id}"
        self.directory = ROOT / ".local/ci" / run_id
        self.reports = ROOT / "ci-results" / run_id
        self.env_file = self.directory / "run.env"
        self.tests_name = f"{self.project}-tests"
        self.images = [
            f"jg-repuestos-ci:{run_id}-test",
            f"jg-repuestos-ci:{run_id}-runtime",
        ]
        self.values = {}
        if self.env_file.exists():
            self.values = dict(
                line.split("=", 1) for line in self.env_file.read_text().splitlines()
            )

    def prepare(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        self.reports.mkdir(parents=True, exist_ok=True)
        if not self.values:
            self.values = {
                "CI_POSTGRES_PASSWORD": secrets.token_hex(24),
                "CI_JWT_SECRET": secrets.token_hex(48),
                "CI_TEST_IMAGE": self.images[0],
                "CI_RUNTIME_IMAGE": self.images[1],
            }
            self.env_file.write_text(
                "".join(f"{k}={v}\n" for k, v in self.values.items())
            )

    def command(self, command, *, check=True, capture=False, log=None):
        environment = os.environ.copy()
        # No heredar variables Compose que puedan seleccionar otro proyecto o contexto.
        for key in list(environment):
            if key.startswith(("COMPOSE_", "CI_POSTGRES_", "CI_JWT_")):
                environment.pop(key)
        environment.update(self.values)
        result = subprocess.run(
            command,
            check=False,
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=1200,
        )
        output = result.stdout + result.stderr
        for key in ("CI_POSTGRES_PASSWORD", "CI_JWT_SECRET"):
            if self.values.get(key):
                output = output.replace(self.values[key], "[REDACTED]")
        if log:
            (self.reports / log).write_text(
                output + f"\nExit code: {result.returncode}\n", encoding="utf-8"
            )
        if not capture:
            print(output, end="", flush=True)
        if check and result.returncode:
            raise RuntimeError(
                f"Comando fallido (codigo {result.returncode}): {command[0:3]}"
            )
        return result, output

    def compose(self, *args, **kwargs):
        if not self.env_file.exists():
            raise RuntimeError("Primero ejecute la etapa test con el mismo CI_RUN_ID")
        command = [
            "docker",
            "compose",
            "--env-file",
            str(self.env_file),
            "--project-name",
            self.project,
            "--file",
            str(ROOT / "ci/compose.yaml"),
            *args,
        ]
        return self.command(command, **kwargs)

    def record(self, stage, status, **extra):
        self.reports.mkdir(parents=True, exist_ok=True)
        (self.reports / f"{stage}.json").write_text(
            json.dumps(
                {
                    "stage": stage,
                    "status": status,
                    "run_id": self.run_id,
                    "timestamp": datetime.now(UTC).isoformat(),
                    **extra,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def require_passed(self, stage):
        path = self.reports / f"{stage}.json"
        if not path.exists() or json.loads(path.read_text())["status"] != "passed":
            raise RuntimeError(f"La etapa {stage} debe aprobar antes de continuar")

    def test(self):
        self.prepare()
        # No aceptar aprobaciones ni XML de una invocacion anterior del mismo identificador.
        for name in ("test.json", "build.json", "smoke.json", "pytest.xml"):
            (self.reports / name).unlink(missing_ok=True)
        self.compose("build", "tests", log="01-build-tests.txt")
        self.compose(
            "up", "-d", "--wait", "--wait-timeout", "180", "db", log="02-db.txt"
        )
        result, _ = self.compose(
            "run",
            "--no-deps",
            "--name",
            self.tests_name,
            "tests",
            check=False,
            log="03-pytest.txt",
        )
        copied, _ = self.command(
            [
                "docker",
                "cp",
                f"{self.tests_name}:/tmp/pytest.xml",
                str(self.reports / "pytest.xml"),
            ],
            check=False,
        )
        if result.returncode or copied.returncode:
            raise RuntimeError("Pytest fallo o no produjo el reporte XML")
        tests = validate_report(self.reports / "pytest.xml")
        self.record("test", "passed", tests=tests, skipped=0)

    def build(self):
        self.require_passed("test")
        self.compose("build", "api", log="04-build-runtime.txt")
        _, image_id = self.command(
            ["docker", "image", "inspect", "--format", "{{.Id}}", self.images[1]],
            capture=True,
        )
        self.record("build", "passed", image=self.images[1], image_id=image_id.strip())

    def smoke(self):
        self.require_passed("test")
        self.require_passed("build")
        self.compose(
            "up",
            "-d",
            "--no-build",
            "--wait",
            "--wait-timeout",
            "180",
            "api",
            log="05-up-smoke.txt",
        )
        probe = (
            "import json,urllib.request; "
            "base='http://127.0.0.1:8000/api/v1/'; "
            "health=json.load(urllib.request.urlopen(base+'health',timeout=10)); "
            "ready=json.load(urllib.request.urlopen(base+'ready',timeout=10)); "
            "assert health['status']=='ok' and ready['status']=='ready'; "
            "print(json.dumps({'health':health,'ready':ready}))"
        )
        self.compose(
            "exec", "-T", "api", "python", "-c", probe, log="06-http-smoke.txt"
        )
        self.compose(
            "exec",
            "-T",
            "api",
            "python",
            "-m",
            "app.diagnostics",
            "roundtrip",
            log="07-roundtrip.txt",
        )
        self.record("smoke", "passed", endpoints=["/api/v1/health", "/api/v1/ready"])

    def cleanup(self):
        if not self.env_file.exists():
            return
        self.compose("logs", "--no-color", check=False, log="08-containers.txt")
        result, _ = self.compose(
            "down", "--volumes", "--remove-orphans", check=False, log="09-cleanup.txt"
        )
        # Nombres exclusivos de esta ejecucion; nunca prune ni imagenes de desarrollo.
        image_result, _ = self.command(
            ["docker", "image", "rm", *self.images], check=False
        )
        self.record(
            "cleanup",
            "passed" if result.returncode == 0 else "failed",
            compose_exit_code=result.returncode,
            image_cleanup_exit_code=image_result.returncode,
        )
        if result.returncode:
            raise RuntimeError("No se completó la limpieza de los contenedores de CI")
        self.env_file.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["test", "build", "smoke", "cleanup"])
    parser.add_argument("--run-id", default=os.environ.get("CI_RUN_ID"))
    args = parser.parse_args()
    if not args.run_id:
        parser.error(
            "Defina CI_RUN_ID o --run-id; use un identificador unico por ejecucion"
        )
    pipeline = Pipeline(args.run_id)
    try:
        getattr(pipeline, args.stage)()
    except (RuntimeError, subprocess.SubprocessError, OSError, ET.ParseError) as error:
        pipeline.record(args.stage, "failed", error=type(error).__name__)
        print(f"Etapa {args.stage} fallida: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
