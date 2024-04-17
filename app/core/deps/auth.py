from typing import Annotated, Optional

import sqlalchemy as sa
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.auth.jwt import JWTProvider, TokenData
from app.user.models import User

from .db import CurrentSession

tokenUrl = "api/v1/auth/swagger-login"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=tokenUrl,
    auto_error=False,
)


def get_user(session: Session, token_data: TokenData) -> Optional[User]:
    stmt = sa.select(User).where(User.id == token_data.id)
    user = session.scalars(stmt).first()

    return user


def get_authenticated_token(token: Optional[str] = Depends(oauth2_scheme)):
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    return JWTProvider.decode_access_token(token)


def get_authenticated_token_or_none(token: Optional[str] = Depends(oauth2_scheme)):
    if token is None:
        return None

    return JWTProvider.decode_access_token(token)


def get_authenticated_user(
    session: CurrentSession,
    token_data: Annotated[TokenData, Depends(get_authenticated_token)],
) -> User:
    user = get_user(session, token_data)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if user.is_active is not True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not active")

    return user


def get_authenticated_user_or_none(
    session: CurrentSession,
    token_data: Annotated[Optional[TokenData], Depends(get_authenticated_token)],
) -> Optional[User]:
    if not token_data:
        return None

    user = get_user(session, token_data)

    if user and user.is_active is not True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not active")

    return user


AuthenticatedTokenData = Annotated[TokenData, Depends(get_authenticated_token)]
AuthenticatedTokenDataOrNone = Annotated[
    Optional[TokenData], Depends(get_authenticated_token_or_none)
]

CurrentUser = Annotated[User, Depends(get_authenticated_user)]
CurrentUserOrNone = Annotated[Optional[User], Depends(get_authenticated_user_or_none)]
