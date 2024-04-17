import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.core.auth import PasswordUtils
from app.core.utils.string import generate_rstr
from app.user.models import User

default_user_email = "pytest@example.com"
default_user_full_name = "Test User"
default_user_password = "test-pass"


async def get_or_create_default_user(session: Session):
    stmt = sa.select(User).where(User.email == default_user_email)
    default_user = session.scalars(stmt).first()

    if not default_user:
        default_user = User(
            email=default_user_email,
            full_name=default_user_full_name,
            is_active=True,
            hashed_password=PasswordUtils.get_hashed_password(default_user_password),
            rstr=generate_rstr(31),
        )

        session.add(default_user)
        session.commit()
        session.refresh(default_user)

    return default_user
