from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.core.auth import PasswordUtils
from app.core.db.manager import BaseManager
from app.core.utils.string import generate_rstr
from app.user.models import User


class UserManager(BaseManager):
    def __init__(self, db: Session) -> None:
        super().__init__(db=db, model=User)

    def _create(self, user: User):
        self.db.add(user)

        self.db.commit()
        self.db.refresh(user)

        return user

    def create_public_user(self, email: str, full_name: str, text_password: str):
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=PasswordUtils.get_hashed_password(text_password),
            is_active=True,
            rstr=generate_rstr(31),
        )
        user = self._create(user)

        return user

    def create_super_admin(self, email: str, full_name: str, text_password: str):
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=PasswordUtils.get_hashed_password(text_password),
            is_active=True,
            is_super_admin=True,
            rstr=generate_rstr(31),
        )
        user = self._create(user)

        return user

    def update_last_login(self, user_id: int):
        update_statement = (
            sa.update(User).where(User.id == user_id).values(last_login=datetime.now())
        )

        self.db.execute(update_statement)

    def get_user_by_id(self, id: int):
        user = User.find_first(self.db, id=id)

        return user

    def get_user_by_email(self, email: str):
        user = User.find_first(self.db, email=email)

        return user
