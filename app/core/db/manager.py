from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session


class BaseManager:
    def __init__(self, db: Session, model: DeclarativeMeta) -> None:
        self.db = db
        self.model = model
