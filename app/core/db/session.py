from sqlalchemy import Engine, create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def new_engine(uri: URL) -> Engine:
    return create_engine(
        uri,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30.0,
        pool_recycle=600,
    )


def get_sync_session() -> Session:
    engine = new_engine(settings.DB_URL)

    return sessionmaker(engine, expire_on_commit=False)()
