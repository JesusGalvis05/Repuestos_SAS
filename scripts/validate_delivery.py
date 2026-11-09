"""Revisión estática de la entrega; no sustituye docker compose config ni un build."""

import json
from pathlib import Path
import re
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[1]


def validate():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    checks = []

    def check(name, condition):
        checks.append({"check": name, "status": "passed" if condition else "failed"})

    services = compose["services"]
    api, db = services["api"], services["db"]
    check("exactamente api y db", set(services) == {"api", "db"})
    check("sin Compose alternativo ambiguo", not (ROOT / "compose.yaml").exists())
    check(
        "DNS Docker y puerto interno",
        api["environment"]["POSTGRES_HOST"] == "db"
        and api["environment"]["POSTGRES_PORT"] == "5432",
    )
    check(
        "sin URL con credenciales en Compose", "DATABASE_URL" not in api["environment"]
    )
    check("PostgreSQL sin puertos publicados", not db.get("ports"))
    check(
        "red propia",
        compose["networks"]["jg-network"]["name"] == "jg-network"
        and all("jg-network" in service["networks"] for service in services.values()),
    )
    check(
        "espera healthcheck", api["depends_on"]["db"]["condition"] == "service_healthy"
    )
    check(
        "volumen persistente", "postgres_data:/var/lib/postgresql/data" in db["volumes"]
    )
    check(
        "PostgreSQL versión específica",
        re.fullmatch(r"postgres:\d+\.\d+-bookworm", db["image"]) is not None,
    )
    dockerfile = (ROOT / "backend/Dockerfile").read_text(encoding="utf-8")
    check(
        "Python oficial versión específica",
        re.search(r"FROM python:\d+\.\d+\.\d+-slim-bookworm", dockerfile) is not None,
    )
    check("usuario no privilegiado", "USER 10001:10001" in dockerfile)
    check(
        "puerto y migraciones",
        "EXPOSE 8000" in dockerfile and '"app.deploy"' in dockerfile,
    )
    workflow = yaml.load(
        (ROOT / ".github/workflows/docker-ci.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    check("eventos CI", set(workflow["on"]) == {"push", "pull_request"})
    workflow_text = (ROOT / ".github/workflows/docker-ci.yml").read_text(
        encoding="utf-8"
    )
    check(
        "Buildx y cierre garantizado",
        "docker/setup-buildx-action@" in workflow_text
        and "if: always()" in workflow_text
        and "docker compose down" in workflow_text,
    )
    check(
        "prueba real integrada",
        "scripts/docker_evidence.py" in workflow_text
        and "scripts/run_container_tests.py" in workflow_text,
    )
    tracked = (
        subprocess.run(
            ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
        )
        .stdout.decode()
        .split("\0")
    )
    check(
        "sin secretos versionados",
        not any(
            p
            and (
                p == ".env"
                or p.endswith("/.env")
                or p.startswith(".local/")
                or p.endswith((".pem", ".key", ".p12", ".pfx"))
            )
            for p in tracked
        ),
    )
    check(
        "ignore de secretos efectivo",
        subprocess.run(["git", "check-ignore", "-q", ".env"], cwd=ROOT).returncode == 0,
    )
    example = (ROOT / ".env.example").read_text(encoding="utf-8")
    check(
        "ejemplo sin secretos",
        "POSTGRES_PASSWORD=\n" in example and "JWT_SECRET=\n" in example,
    )
    return {
        "scope": "static-only",
        "status": "passed"
        if all(c["status"] == "passed" for c in checks)
        else "failed",
        "checks": checks,
    }


if __name__ == "__main__":
    report = validate()
    target = ROOT / "docs/entrega-1/evidencias/validacion-estatica.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["status"] == "passed" else 1)
