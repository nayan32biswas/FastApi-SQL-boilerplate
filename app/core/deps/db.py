from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db.session import get_sync_session


def get_session() -> Generator[Session, None, None]:
    with get_sync_session() as session:
        yield session


CurrentSession = Annotated[Session, Depends(get_session)]
