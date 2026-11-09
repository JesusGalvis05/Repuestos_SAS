"""Despliega el build React y FastAPI en este equipo con PostgreSQL dedicado.

Windows: python scripts/deploy_local.py
La contraseña del primer administrador se muestra una sola vez y no se guarda.
"""

import json
import os
import secrets
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import psycopg
from alembic import command
from alembic.config import Config
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".local"
DB_PORT = 55433
APP_PORT = 8080
CREATE_FLAGS = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


def pg_binary(name):
    custom = os.environ.get("JG_POSTGRES_BIN")
    if custom:
        return str(Path(custom) / name)
    candidates = sorted(
        Path(r"C:\Program Files\PostgreSQL").glob(f"*/bin/{name}"), reverse=True
    )
    if not candidates:
        raise RuntimeError("No se encontró PostgreSQL. Configure JG_POSTGRES_BIN.")
    return str(candidates[0])


def run_postgres(args):
    # Evitar pipes heredados por el servidor persistente en Windows.
    with (STATE / "pg-control.log").open("ab") as log:
        result = subprocess.run(args, stdout=log, stderr=log, creationflags=CREATE_FLAGS)
    if result.returncode:
        raise RuntimeError("Falló PostgreSQL. Consulte .local/pg-control.log")


def main():
    if not (ROOT / "frontend/dist/index.html").exists():
        raise RuntimeError(
            "Primero compile el frontend con npm.cmd run build en frontend/."
        )
    STATE.mkdir(exist_ok=True)
    # Comprobar el puerto antes de crear usuarios o modificar este despliegue.
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", APP_PORT))
        except OSError:
            raise RuntimeError(
                "El puerto 8080 está ocupado. No se modificó la cuenta existente."
            ) from None

    config_path = STATE / "application.env"
    if not config_path.exists():
        password = secrets.token_hex(24)
        config_path.write_text(
            f"DATABASE_URL=postgresql+psycopg://jg:{password}@127.0.0.1:{DB_PORT}/jg_repuestos\n"
            f"JWT_SECRET={secrets.token_hex(48)}\nAPP_ENV=development\nCOOKIE_SECURE=false\n"
            f"FRONTEND_DIST={(ROOT / 'frontend/dist').as_posix()}\n"
            'ALLOWED_ORIGINS=["http://localhost:8080","http://127.0.0.1:8080"]\n',
            encoding="utf-8",
        )
    values = {k: v for k, v in dotenv_values(config_path).items() if v is not None}
    os.environ.update(values)
    from sqlalchemy.engine import make_url

    url = make_url(values["DATABASE_URL"])
    pg_data = STATE / "pg-app"
    if not (pg_data / "PG_VERSION").exists():
        password_file = STATE / "pg-init-password.txt"
        try:
            password_file.write_text(url.password, encoding="utf-8")
            run_postgres(
                [
                    pg_binary("initdb.exe"),
                    "-D",
                    str(pg_data),
                    "-U",
                    "jg",
                    "--auth=scram-sha-256",
                    "--encoding=UTF8",
                    "--locale=C",
                    f"--pwfile={password_file}",
                ]
            )
        finally:
            password_file.unlink(missing_ok=True)
    status = subprocess.run(
        [pg_binary("pg_ctl.exe"), "-D", str(pg_data), "status"],
        capture_output=True,
        creationflags=CREATE_FLAGS,
    )
    if status.returncode:
        run_postgres(
            [
                pg_binary("pg_ctl.exe"),
                "-D",
                str(pg_data),
                "-l",
                str(STATE / "pg-app.log"),
                "-o",
                f"-h 127.0.0.1 -p {DB_PORT} -c timezone=UTC",
                "-w",
                "start",
            ]
        )
    with psycopg.connect(
        host=url.host,
        port=url.port,
        user=url.username,
        password=url.password,
        dbname="postgres",
        autocommit=True,
    ) as conn:
        if not conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", ("jg_repuestos",)
        ).fetchone():
            conn.execute("CREATE DATABASE jg_repuestos")

    from app.core.config import get_settings
    from app.core.db import session_factory
    from app.modules.identity.services import IdentityService

    get_settings.cache_clear()
    session_factory.cache_clear()
    command.upgrade(Config(str(ROOT / "backend/alembic.ini")), "head")
    admin_email = "admin@jgrepuestos.com"
    new_password = None
    with session_factory()() as db, db.begin():
        service = IdentityService(db, get_settings())
        if not service.repo.active_admins():
            new_password = secrets.token_urlsafe(18)
            service.bootstrap(admin_email, "Administrador JG Repuestos", new_password)
    session_factory().kw["bind"].dispose()
    with (STATE / "application.log").open("a", encoding="utf-8") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(APP_PORT),
                "--no-access-log",
            ],
            cwd=ROOT / "backend",
            env=os.environ.copy(),
            stdout=log,
            stderr=log,
            creationflags=CREATE_FLAGS,
        )
    (STATE / "application-process.json").write_text(
        json.dumps({"pid": process.pid, "port": APP_PORT}), encoding="utf-8"
    )
    with httpx.Client(
        base_url=f"http://127.0.0.1:{APP_PORT}",
        headers={"Origin": f"http://localhost:{APP_PORT}"},
    ) as client:
        for _ in range(60):
            try:
                if client.get("/api/v1/ready").status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            if process.poll() is not None:
                raise RuntimeError("FastAPI no inició. Consulte .local/application.log")
            time.sleep(0.25)
        else:
            raise RuntimeError(
                "No se pudo comprobar el inicio. Consulte .local/application.log"
            )
        assert client.get("/ingresar").status_code == 200
        if new_password:
            response = client.post(
                "/api/v1/auth/login",
                json={"email": admin_email, "password": new_password},
            )
            assert response.status_code == 200, "No se pudo validar la cuenta inicial"
            token = response.json()["access_token"]
            assert (
                client.get(
                    "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
                ).status_code
                == 200
            )
            assert client.post("/api/v1/auth/logout").status_code == 204
    print(
        json.dumps(
            {
                "url": f"http://localhost:{APP_PORT}/ingresar",
                "scope": "local",
                "email": admin_email,
                "password": new_password,
                "status": "verified",
                "pid": process.pid,
            }
        )
    )


if __name__ == "__main__":
    main()
