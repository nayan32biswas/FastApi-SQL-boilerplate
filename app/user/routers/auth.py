from datetime import datetime

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload

from app.core import constants
from app.core.auth import PasswordUtils
from app.core.auth.jwt import JWTProvider
from app.core.config import settings
from app.core.deps.auth import CurrentUser
from app.core.deps.db import CurrentSession
from app.core.utils.string import generate_rstr
from app.user.models import ForgotPassword, User
from app.user.models_manager.forgot_password import ForgotPasswordManager
from app.user.models_manager.user import UserManager
from app.user.schemas.auth import (
    ForgotPasswordRequestIn,
    ForgotPasswordResetIn,
    LoginIn,
    PasswordChangeIn,
    RefreshTokenIn,
    RegistrationIn,
)
from worker.tasks.email import send_email

router = APIRouter(
    prefix="/auth",
)


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def registration(
    data: RegistrationIn,
    session: CurrentSession,
):
    user_manager = UserManager(session)
    user = user_manager.get_user_by_email(data.email)

    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User exists")

    user_manager = UserManager(session)

    user = user_manager.create_public_user(
        email=data.email, full_name=data.full_name, text_password=data.password
    )

    return {"message": "User created"}


def handle_login(session: Session, email: str, password: str):
    user_manager = UserManager(session)

    user = user_manager.get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    if not PasswordUtils.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")

    access_token = JWTProvider.create_access_token(id=user.id, rstr="temp")
    refresh_token = JWTProvider.create_refresh_token(id=user.id, rstr="temp")

    user_manager.update_last_login(user.id)

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/swagger-login")
async def swagger_login(
    session: CurrentSession,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    return handle_login(session, form_data.username, form_data.password)


@router.post("/login")
async def token_login(
    data: LoginIn,
    session: CurrentSession,
):
    token = handle_login(session, data.email, data.password)

    return token


@router.post("/refresh-token")
async def refresh_token(
    session: CurrentSession,
    data: RefreshTokenIn,
):
    refresh_token_payload = JWTProvider.decode_refresh_token(data.refresh_token)

    user_manager = UserManager(session)

    user = user_manager.get_user_by_id(refresh_token_payload.id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token or user is not active",
        )

    access_token = JWTProvider.create_access_token(id=user.id, rstr="temp")

    return {"access_token": access_token}


@router.post("/change-password")
async def change_password(
    user: CurrentUser,
    session: CurrentSession,
    data: PasswordChangeIn,
):
    old_password = data.old_password
    new_password = data.new_password

    if not PasswordUtils.verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password")

    user.hashed_password = PasswordUtils.get_hashed_password(new_password)
    session.commit()

    return {"message": "Successfully change the password"}


@router.post("/forgot-password-request")
async def forgot_password_request(
    session: CurrentSession,
    data: ForgotPasswordRequestIn,
):
    user = User.get_obj_or_404(session=session, email=data.email)

    forgot_password_manager = ForgotPasswordManager(db=session)
    forgot_password_instance = forgot_password_manager.create(user_id=user.id, email=data.email)

    forgot_password_url = f"{settings.API_HOST}/{constants.FORGOT_PASSWORD_PATH}?token={forgot_password_instance.token}"

    send_email.delay(
        to=[user.email],
        subject="Forgot password request",
        data={
            "url": forgot_password_url,
        },
    )

    return {"message": "Check your email inbox to set new password"}


@router.post("/forgot-password-reset")
async def forgot_password_reset(
    session: CurrentSession,
    data: ForgotPasswordResetIn,
):
    stmt = (
        sa.select(ForgotPassword)
        .where(ForgotPassword.token == data.token)
        .options(joinedload(ForgotPassword.user))
    )
    forgot_password_instance = session.scalars(stmt).first()

    user = forgot_password_instance.user

    if forgot_password_instance.is_used:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token already used")

    if forgot_password_instance.expire_at < datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is expired")

    forgot_password_instance.is_used = True
    forgot_password_instance.used_at = datetime.now()

    user.hashed_password = PasswordUtils.get_hashed_password(data.new_password)

    if data.force_logout is True:
        user.rstr = generate_rstr(31)

    session.commit()

    send_email.delay(to=[user.email], subject="New password set")

    return {"message": "Successfully reset password"}
