import os
import secrets
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


@pytest.fixture(scope="session")
def postgres_url():
    url = os.environ.get("TEST_DATABASE_URL")
    if url:
        yield url
    elif os.environ.get("USE_TESTCONTAINERS") == "1":
        from testcontainers.postgres import PostgresContainer

        with PostgresContainer("postgres:17", driver="psycopg") as postgres:
            yield postgres.get_connection_url()
    else:
        pytest.skip("Defina TEST_DATABASE_URL o USE_TESTCONTAINERS=1 para PostgreSQL real")


@pytest.fixture()
def environment(postgres_url, monkeypatch):
    # Sólo se crea/elimina un esquema de nombre aleatorio propiedad de esta prueba.
    schema = "test_" + uuid4().hex
    admin_engine = create_engine(postgres_url)
    with admin_engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA "{schema}"'))
    url = make_url(postgres_url).update_query_dict({"options": f"-csearch_path={schema}"})
    monkeypatch.setenv("DATABASE_URL", url.render_as_string(hide_password=False))
    monkeypatch.setenv("JWT_SECRET", secrets.token_hex(40))
    monkeypatch.setenv("COOKIE_SECURE", "false")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("ALLOWED_ORIGINS", '["http://localhost:5173"]')
    from app.core.config import get_settings
    from app.core.db import session_factory

    get_settings.cache_clear()
    session_factory.cache_clear()
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    command.upgrade(config, "head")
    from app.main import create_app

    app = create_app()
    with TestClient(app, headers={"Origin": "http://localhost:5173"}) as client:
        yield client, session_factory(), config
    session_factory().kw["bind"].dispose()
    session_factory.cache_clear()
    get_settings.cache_clear()
    with admin_engine.begin() as conn:
        conn.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
    admin_engine.dispose()


@pytest.fixture()
def admin(environment):
    client, factory, _config = environment
    from app.core.config import get_settings
    from app.modules.identity.services import IdentityService

    with factory() as db, db.begin():
        user = IdentityService(db, get_settings()).bootstrap(
            "admin@example.com", "Administradora de pruebas", "test-password-secure-123"
        )
    response = client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": "test-password-secure-123"}
    )
    assert response.status_code == 200, response.text
    client.headers["Authorization"] = "Bearer " + response.json()["access_token"]
    return client, factory, user
