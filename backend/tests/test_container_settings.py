import pytest
from pydantic import ValidationError
from sqlalchemy.engine import make_url

from app.core.config import Settings


def test_postgres_url_encodes_password_without_changing_it():
    password = "special@:/%$chars"
    settings = Settings(
        _env_file=None,
        database_url="",
        postgres_host="db",
        postgres_port=5432,
        postgres_user="jg",
        postgres_password=password,
        postgres_db="jg_test",
        docker_runtime=True,
        jwt_secret="unit-test-random-key-at-least-32-characters",
    )
    url = make_url(settings.database_url)
    assert url.host == "db" and url.port == 5432
    assert url.password == password
    assert password not in repr(settings)


@pytest.mark.parametrize(
    "address", ["localhost:5432", "127.0.0.1:5432", "10.0.0.7:5432", "db:55433"]
)
def test_docker_rejects_other_database_addresses(address):
    with pytest.raises(ValidationError) as failure:
        Settings(
            _env_file=None,
            database_url=f"postgresql+psycopg://jg:secret-not-logged@{address}/jg",
            docker_runtime=True,
            jwt_secret="unit-test-random-key-at-least-32-characters",
        )
    assert "secret-not-logged" not in str(failure.value)
