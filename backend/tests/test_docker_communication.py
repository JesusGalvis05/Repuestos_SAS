import os
from uuid import UUID

import pytest

from app.core.db import session_factory
from app.modules.identity.models import User


@pytest.mark.postgres
def test_write_read_cleanup_uses_api_database(environment):
    _client, factory, _config = environment
    from app.diagnostics import create_demo, delete_demo, read_demo

    identifier = create_demo()
    try:
        result = read_demo(identifier)
        assert result["status"] == "passed"
        assert result["id"] == str(identifier)
    finally:
        delete_demo(identifier)
    with factory() as db:
        assert db.get(User, identifier) is None


@pytest.mark.postgres
def test_cleanup_cannot_delete_a_normal_user(admin):
    _client, factory, user = admin
    from app.diagnostics import delete_demo

    with pytest.raises(ValueError):
        delete_demo(user.id)
    with factory() as db:
        assert db.get(User, user.id).active


@pytest.mark.skipif(
    os.environ.get("RUN_DOCKER_COMMUNICATION") != "1", reason="Sólo dentro de api con db:5432"
)
def test_docker_uses_service_hostname_and_cleans_its_record():
    from app.core.config import get_settings
    from app.diagnostics import roundtrip

    assert get_settings().docker_runtime
    result = roundtrip()
    assert result["host"] == "db" and result["server_port"] == 5432
    assert result["cleanup"] == "passed"
    with session_factory()() as db:
        assert db.get(User, UUID(result["id"])) is None
