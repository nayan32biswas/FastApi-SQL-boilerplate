from typing import List, Optional

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from typing_extensions import Self

from app.core.exceptions import ObjectNotFoundException


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(sa.Integer(), primary_key=True, autoincrement=True)

    @classmethod
    def find(cls, session: Session, **kwargs) -> List[Self]:
        stmt = sa.select(cls).filter_by(**kwargs).order_by(sa.asc(cls.id))
        obj_list = session.scalars(stmt)

        return obj_list

    @classmethod
    def find_first(cls, session: Session, **kwargs) -> Optional[Self]:
        stmt = sa.select(cls).filter_by(**kwargs).order_by(sa.asc(cls.id))
        obj = session.scalars(stmt).first()

        return obj

    @classmethod
    def get_obj_or_404(cls, session: Session, **kwargs) -> Self:
        obj = cls.find_first(session, **kwargs)

        if not obj:
            raise ObjectNotFoundException(message="Object not found")

        return obj
