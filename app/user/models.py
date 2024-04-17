from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import Base
from app.core.db.models_mixin import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(sa.String(255), nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(sa.String(127), nullable=False)
    is_active: Mapped[bool] = mapped_column(sa.Boolean(), default=False)
    is_verified: Mapped[bool] = mapped_column(sa.Boolean(), default=False)
    is_super_admin: Mapped[bool] = mapped_column(sa.Boolean(), default=False)
    hashed_password: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    image: Mapped[Optional[str]] = mapped_column(sa.String(512), default=None, nullable=True)
    rstr: Mapped[str] = mapped_column(sa.String(31), nullable=False)
    last_login: Mapped[datetime] = mapped_column(
        sa.DateTime(), default=sa.func.now(), nullable=False
    )

    forgot_passwords = relationship("ForgotPassword", back_populates="user")


class ForgotPassword(Base, TimestampMixin):
    __tablename__ = "forgot_password"

    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("user.id"))
    email: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    is_used: Mapped[bool] = mapped_column(sa.Boolean(), default=False)
    expire_at: Mapped[datetime] = mapped_column(sa.DateTime(), nullable=False)
    used_at: Mapped[datetime] = mapped_column(sa.DateTime(), nullable=True, default=None)
    token: Mapped[str] = mapped_column(sa.String(255), nullable=False)

    user = relationship("User", back_populates="forgot_passwords")
