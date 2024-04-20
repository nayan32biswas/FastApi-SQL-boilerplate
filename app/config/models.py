from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import Base


class UploadedFile(Base):
    __tablename__ = "uploaded_file"

    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("user.id"))

    name: Mapped[Optional[str]] = mapped_column(sa.String(255), default=None)
    file_path: Mapped[Optional[str]] = mapped_column(sa.String(255), default=None)
    extension: Mapped[Optional[str]] = mapped_column(sa.String(10), default=None)
    size: Mapped[Optional[int]] = mapped_column(sa.Integer, default=None)

    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=sa.func.now(), nullable=False)

    user = relationship("User", back_populates="uploaded_files")
