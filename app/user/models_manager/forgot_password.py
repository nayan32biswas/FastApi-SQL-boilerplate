from datetime import datetime, timedelta
from secrets import token_hex

import sqlalchemy as sa
from sqlalchemy.orm import Session, joinedload

from app.core import constants
from app.core.db.manager import BaseManager
from app.user.models import ForgotPassword


class ForgotPasswordManager(BaseManager):
    def __init__(self, db: Session) -> None:
        super().__init__(db=db, model=ForgotPassword)

    def create(self, user_id: int, email: str):
        expire_at = datetime.now() + timedelta(minutes=constants.FORGOT_PASSWORD_EXPIRE_MINUTES)

        forgot_password_instance = ForgotPassword(
            user_id=user_id,
            email=email,
            expire_at=expire_at,
            token=token_hex(60),
        )
        self.db.add(forgot_password_instance)
        self.db.commit()

        return forgot_password_instance

    def get_forgot_password_and_user_from_token(self, token: str):
        stmt = (
            sa.select(ForgotPassword)
            .where(ForgotPassword.token == token)
            .options(joinedload(ForgotPassword.user))
        )
        forgot_password_instance = self.db.session.scalars(stmt).first()

        return forgot_password_instance, forgot_password_instance.user
