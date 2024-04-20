from typing import Annotated, Optional

import sqlalchemy as sa
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.auth.jwt import JWTProvider, TokenData, TokenException
from app.core.exceptions import CustomException, PermissionException
from app.user.models import User

from .db import SessionDep

tokenUrl = "api/v1/auth/swagger-login"


class UserException(CustomException):
    code = 400
    error_code = "USER_ERROR"
    message = "User error"


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=tokenUrl,
    auto_error=False,
)

TokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_user(session: Session, token_data: TokenData) -> Optional[User]:
    stmt = sa.select(User).where(User.id == token_data.id)
    user = session.scalars(stmt).first()

    return user


def get_authenticated_token_or_none(token: TokenDep):
    if token is None:
        return None

    return JWTProvider.decode_access_token(token)


AuthenticatedTokenDataOrNone = Annotated[
    Optional[TokenData], Depends(get_authenticated_token_or_none)
]


def get_authenticated_user_or_none(
    session: SessionDep, token_data: AuthenticatedTokenDataOrNone
) -> Optional[User]:
    if not token_data:
        return None

    user = get_user(session, token_data)

    if user and user.is_active is not True:
        raise UserException(message="User is inactive")

    return user


CurrentUserOrNone = Annotated[Optional[User], Depends(get_authenticated_user_or_none)]


def get_authenticated_token(token_data: AuthenticatedTokenDataOrNone):
    if token_data is None:
        raise TokenException(detail="Token is not provided")

    return token_data


AuthenticatedTokenData = Annotated[TokenData, Depends(get_authenticated_token)]


def get_authenticated_user(current_user: CurrentUserOrNone) -> User:
    if current_user is None:
        raise UserException(message="User not found")

    return current_user


CurrentUser = Annotated[User, Depends(get_authenticated_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_super_admin:
        raise PermissionException(message="The user doesn't have enough privileges")

    return current_user
