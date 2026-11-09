"""Arranque del único backend desplegable: migraciones y servidor ASGI."""

import os

import uvicorn
from alembic import command
from alembic.config import Config


def main():
    command.upgrade(Config("alembic.ini"), "head")
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), access_log=False
    )


if __name__ == "__main__":
    main()
