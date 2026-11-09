"""Demostración privada de comunicación y persistencia; no agrega endpoints HTTP."""

import argparse
import json
import secrets
from uuid import UUID, uuid4

from sqlalchemy import delete, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.core.db import session_factory
from app.core.security import hash_password
from app.modules.identity.models import User

DEMO_NAME = "DEMOSTRACIÓN DOCKER - REGISTRO TEMPORAL INACTIVO"


def demo_email(identifier: UUID) -> str:
    return f"docker-demo-{identifier.hex}@example.com"


def create_demo() -> UUID:
    identifier = uuid4()
    with session_factory()() as db, db.begin():
        db.add(
            User(
                id=identifier,
                email=demo_email(identifier),
                full_name=DEMO_NAME,
                password_hash=hash_password(secrets.token_urlsafe(32)),
                active=False,
                roles=[],
            )
        )
    return identifier


def read_demo(identifier: UUID) -> dict:
    # Nueva sesión y transacción; no se verifica la caché de la inserción.
    with session_factory()() as db, db.begin():
        user = db.scalar(select(User).where(User.id == identifier))
        if (
            not user
            or user.email != demo_email(identifier)
            or user.full_name != DEMO_NAME
            or user.active
            or user.roles
        ):
            raise ValueError("El registro no corresponde a esta demostración")
        database, port = db.execute(text("SELECT current_database(), inet_server_port()")).one()
        address = make_url(get_settings().database_url)
        return {
            "status": "passed",
            "operation": "read",
            "id": str(identifier),
            "host": address.host,
            "configured_port": address.port,
            "server_port": port,
            "database": database,
            "verified": ["id", "email", "full_name", "inactive", "no_roles"],
        }


def delete_demo(identifier: UUID):
    with session_factory()() as db, db.begin():
        result = db.execute(
            delete(User).where(
                User.id == identifier,
                User.email == demo_email(identifier),
                User.full_name == DEMO_NAME,
                User.active.is_(False),
                ~User.roles.any(),
            )
        )
        if result.rowcount != 1:
            raise ValueError("No se eliminó ningún dato ajeno o inexistente")


def roundtrip() -> dict:
    identifier = create_demo()
    try:
        result = read_demo(identifier)
    finally:
        delete_demo(identifier)
    result.update(operation="write-read-cleanup", cleanup="passed")
    return result


def main():
    parser = argparse.ArgumentParser(description="Comunicación mediante la conexión de la API")
    parser.add_argument("operation", choices=["roundtrip", "create", "read", "delete"])
    parser.add_argument("--id", type=UUID)
    args = parser.parse_args()
    if args.operation in {"read", "delete"} and not args.id:
        parser.error("Esta operación requiere --id del registro temporal creado")
    try:
        if args.operation == "roundtrip":
            result = roundtrip()
        elif args.operation == "create":
            result = {"status": "passed", "operation": "create", "id": str(create_demo())}
        elif args.operation == "read":
            result = read_demo(args.id)
        else:
            delete_demo(args.id)
            result = {"status": "passed", "operation": "delete", "id": str(args.id)}
    except (SQLAlchemyError, ValueError):
        print(
            json.dumps(
                {"status": "failed", "operation": args.operation, "error": "DATABASE_CHECK_FAILED"}
            )
        )
        raise SystemExit(1) from None
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
