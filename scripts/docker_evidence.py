"""Ejecuta Docker real y conserva salidas saneadas; no simula comandos ausentes."""

import argparse
from datetime import datetime
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.parse import quote
from urllib.request import urlopen
from uuid import UUID
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]


def secret_values():
    values = []
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition("=")
            if key in {"POSTGRES_PASSWORD", "JWT_SECRET"} and value.strip("\"'"):
                raw = value.strip("\"'")
                values.extend(
                    [
                        raw,
                        quote(raw, safe=""),
                        json.dumps(raw)[1:-1],
                        json.dumps(raw, ensure_ascii=False)[1:-1],
                    ]
                )
    return sorted(set(values), key=len, reverse=True)


def sanitize(value: str, secrets: list[str]) -> str:
    for secret in secrets:
        value = value.replace(secret, "[REDACTADO]")
    return re.sub(
        r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b",
        "[TOKEN_REDACTADO]",
        value,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    instant = datetime.now(ZoneInfo("America/Bogota"))
    timestamp = instant.isoformat()
    directory = (
        args.output
        or ROOT
        / "docs/entrega-1/evidencias/ejecuciones"
        / instant.strftime("%Y%m%d-%H%M%S")
    )
    directory.mkdir(parents=True, exist_ok=True)
    secrets = secret_values()
    report = {
        "started_at": timestamp,
        "status": "running",
        "commands": [],
        "communication": "pending",
        "persistence": "pending",
    }
    demo_id = None

    def run(label, command, timeout=180):
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        output = sanitize(result.stdout + result.stderr, secrets)
        (directory / f"{label}.txt").write_text(
            "$ "
            + " ".join(command)
            + "\n"
            + output
            + f"\nExit code: {result.returncode}\n",
            encoding="utf-8",
        )
        report["commands"].append(
            {
                "evidence": f"{label}.txt",
                "command": command,
                "exit_code": result.returncode,
            }
        )
        if result.returncode:
            raise RuntimeError(f"Falló {label}; consulte la evidencia saneada")
        print(f"PASS {label}", flush=True)
        return result.stdout

    def diagnostic(operation, identifier=None, label=None):
        command = [
            "docker",
            "compose",
            "exec",
            "-T",
            "api",
            "python",
            "-m",
            "app.diagnostics",
            operation,
        ]
        if identifier:
            command += ["--id", str(identifier)]
        return json.loads(run(label or operation, command))

    try:
        if not shutil.which("docker"):
            report.update(
                status="blocked",
                reason="Docker CLI/motor no disponibles en este equipo",
            )
            (directory / "00-entorno.txt").write_text(
                f"Fecha: {timestamp}\nBúsqueda real de docker en PATH: no encontrado.\nNo se ejecutaron ni simularon comandos Docker.\n",
                encoding="utf-8",
            )
            print("BLOCKED: Docker no está instalado; evidencia de entorno guardada.")
            return 2
        run("01-docker-version", ["docker", "version"])
        run("02-compose-version", ["docker", "compose", "version"])
        config = json.loads(
            run(
                "03-compose-config", ["docker", "compose", "config", "--format", "json"]
            )
        )
        assert set(config["services"]) == {"api", "db"}, (
            "Se requieren exactamente dos servicios"
        )
        assert not config["services"]["db"].get("ports"), "db no debe publicar puertos"
        run("04-postgres-pull", ["docker", "compose", "pull", "db"], timeout=600)
        run(
            "05-docker-build",
            [
                "docker",
                "build",
                "--target",
                "runtime",
                "--tag",
                "jg-repuestos-api:academic",
                "backend",
            ],
            timeout=900,
        )
        run("06-compose-build", ["docker", "compose", "build"], timeout=900)
        run(
            "07-compose-up",
            ["docker", "compose", "up", "-d", "--wait", "--wait-timeout", "180"],
            timeout=240,
        )
        run("08-compose-ps", ["docker", "compose", "ps"])
        run(
            "09-docker-ps",
            [
                "docker",
                "ps",
                "--filter",
                "label=com.docker.compose.project=jg-repuestos",
            ],
        )
        run("10-network-inspect", ["docker", "network", "inspect", "jg-network"])
        uid = run(
            "11-api-user", ["docker", "compose", "exec", "-T", "api", "id", "-u"]
        ).strip()
        assert uid == "10001", "api debe ejecutarse con usuario no privilegiado"
        run(
            "12-alembic-current",
            ["docker", "compose", "exec", "-T", "api", "alembic", "current"],
        )
        run(
            "13-alembic-check",
            ["docker", "compose", "exec", "-T", "api", "alembic", "check"],
        )
        with urlopen("http://127.0.0.1:8000/api/v1/ready", timeout=10) as response:
            assert response.status == 200
        result = diagnostic("roundtrip", label="14-escritura-lectura-limpieza")
        assert (
            result["host"] == "db"
            and result["server_port"] == 5432
            and result["cleanup"] == "passed"
        )
        report["communication"] = "passed"
        created = diagnostic("create", label="15-persistencia-crear")
        demo_id = UUID(created["id"])
        run("16-recrear-down", ["docker", "compose", "down"])
        run(
            "17-recrear-up",
            ["docker", "compose", "up", "-d", "--wait", "--wait-timeout", "180"],
            timeout=240,
        )
        persisted = diagnostic("read", demo_id, "18-persistencia-leer")
        assert persisted["id"] == str(demo_id) and persisted["host"] == "db"
        report["persistence"] = "passed"
        diagnostic("delete", demo_id, "19-persistencia-limpiar")
        demo_id = None
        run(
            "20-logs-api",
            ["docker", "compose", "logs", "--no-color", "--tail", "150", "api"],
        )
        run(
            "21-logs-db",
            ["docker", "compose", "logs", "--no-color", "--tail", "150", "db"],
        )
        report["status"] = "passed"
        return 0
    except (
        OSError,
        RuntimeError,
        AssertionError,
        ValueError,
        subprocess.TimeoutExpired,
    ) as exc:
        report.update(status="failed", reason=sanitize(str(exc), secrets))
        print("FAILED: revise el informe y los comandos que sí se ejecutaron.")
        return 1
    finally:
        if demo_id:
            report["pending_demo_id"] = str(demo_id)
            try:
                diagnostic("delete", demo_id, "99-limpieza-tras-error")
                report.pop("pending_demo_id")
            except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired):
                report["cleanup"] = "pending; sólo el usuario inactivo identificado"
        if report["status"] == "failed" and shutil.which("docker"):
            for service in ("api", "db"):
                try:
                    run(
                        f"99-diagnostico-{service}",
                        [
                            "docker",
                            "compose",
                            "logs",
                            "--no-color",
                            "--tail",
                            "150",
                            service,
                        ],
                    )
                except (OSError, RuntimeError, subprocess.TimeoutExpired):
                    pass
        report["finished_at"] = datetime.now(ZoneInfo("America/Bogota")).isoformat()
        (directory / "resultado.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Evidencias: {directory}")


if __name__ == "__main__":
    sys.exit(main())
