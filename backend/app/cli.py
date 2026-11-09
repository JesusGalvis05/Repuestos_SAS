import argparse
from getpass import getpass

from pydantic import ValidationError

from app.core.config import get_settings
from app.core.db import session_factory
from app.core.errors import DomainError
from app.modules.identity.services import IdentityService


def main():
    parser = argparse.ArgumentParser(description="Administración local segura de JG Repuestos")
    parser.add_argument("command", choices=["create-admin"])
    args = parser.parse_args()
    if args.command == "create-admin":
        email = input("Correo del primer administrador: ").strip()
        name = input("Nombre completo: ").strip()
        password = getpass("Contraseña (mínimo 12 caracteres): ")
        if password != getpass("Repita la contraseña: "):
            parser.exit(1, "Las contraseñas no coinciden.\n")
        try:
            with session_factory()() as db, db.begin():
                user = IdentityService(db, get_settings()).bootstrap(email, name, password)
            print(f"Administrador creado: {user.email}")
        except ValidationError:
            parser.exit(1, "Datos inválidos: revise correo, nombre y longitud de contraseña.\n")
        except DomainError as exc:
            parser.exit(1, f"{exc.message}\n")


if __name__ == "__main__":
    main()
