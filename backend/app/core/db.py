from collections.abc import Generator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


@lru_cache
def session_factory():
    engine = create_engine(get_settings().database_url, pool_pre_ping=True)
    return sessionmaker(engine, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    # Commit/rollback antes de enviar la respuesta, incluso si falla el commit.
    with session_factory()() as session, session.begin():
        yield session


Db = Annotated[Session, Depends(get_db, scope="function")]
