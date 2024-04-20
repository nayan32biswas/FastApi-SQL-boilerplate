from datetime import datetime

import sqlalchemy as sa
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload

from app.core.auth import PasswordUtils
from app.core.auth.jwt import JWTProvider
from app.core.config import FORGOT_PASSWORD_PATH, settings
from app.core.deps.auth import CurrentUser
from app.core.deps.db import SessionDep
from app.core.exceptions import ObjectNotFoundException
from app.core.utils.string import generate_rstr
from worker.tasks.email import send_email

from ..exception import (
    EmailExistsException,
    ForgotPasswordTokenException,
    InvalidCredentialsException,
)
from ..models import ForgotPassword, User
from ..models_manager.forgot_password import ForgotPasswordManager
from ..models_manager.user import UserManager
from ..schemas.auth import (
    ForgotPasswordRequestIn,
    ForgotPasswordResetIn,
    LoginIn,
    PasswordChangeIn,
    RefreshTokenIn,
    RegistrationIn,
)

router = APIRouter(
    prefix="/auth",
)


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def registration(
    data: RegistrationIn,
    session: SessionDep,
):
    user_manager = UserManager(session)
    user = user_manager.get_user_by_email(data.email)

    if user:
        raise EmailExistsException(message="User with email exists")

    user_manager = UserManager(session)

    user = user_manager.create_public_user(
        email=data.email, full_name=data.full_name, text_password=data.password
    )

    return {"message": "User created"}


def handle_login(session: Session, email: str, password: str):
    user_manager = UserManager(session)

    user = user_manager.get_user_by_email(email)

    if not user:
        raise InvalidCredentialsException

    if not PasswordUtils.verify_password(password, user.hashed_password):
        raise InvalidCredentialsException

    access_token = JWTProvider.create_access_token(id=user.id, rstr="temp")
    refresh_token = JWTProvider.create_refresh_token(id=user.id, rstr="temp")

    user_manager.update_last_login(user.id)

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/swagger-login")
async def swagger_login(
    session: SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    return handle_login(session, form_data.username, form_data.password)


@router.post("/login")
async def token_login(
    data: LoginIn,
    session: SessionDep,
):
    token = handle_login(session, data.email, data.password)

    return token


@router.post("/refresh-token")
async def refresh_token(
    session: SessionDep,
    data: RefreshTokenIn,
):
    refresh_token_payload = JWTProvider.decode_refresh_token(data.refresh_token)

    user_manager = UserManager(session)

    user = user_manager.get_user_by_id(refresh_token_payload.id)

    if not user:
        raise ObjectNotFoundException(message="Invalid user token")

    access_token = JWTProvider.create_access_token(id=user.id, rstr="temp")

    return {"access_token": access_token}


@router.post("/change-password")
async def change_password(
    user: CurrentUser,
    session: SessionDep,
    data: PasswordChangeIn,
):
    old_password = data.old_password
    new_password = data.new_password

    if not PasswordUtils.verify_password(old_password, user.hashed_password):
        raise InvalidCredentialsException(message="Invalid password")

    user.hashed_password = PasswordUtils.get_hashed_password(new_password)
    session.commit()

    return {"message": "Successfully change the password"}


@router.post("/forgot-password-request")
async def forgot_password_request(
    session: SessionDep,
    data: ForgotPasswordRequestIn,
):
    user = User.get_obj_or_404(session=session, email=data.email)

    forgot_password_manager = ForgotPasswordManager(db=session)
    forgot_password_instance = forgot_password_manager.create(user_id=user.id, email=data.email)

    forgot_password_url = (
        f"{settings.API_HOST}/{FORGOT_PASSWORD_PATH}?token={forgot_password_instance.token}"
    )

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
    session: SessionDep,
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
        raise ForgotPasswordTokenException(message="Token already used")

    if forgot_password_instance.expire_at < datetime.now():
        raise ForgotPasswordTokenException(message="Token is expired")

    forgot_password_instance.is_used = True
    forgot_password_instance.used_at = datetime.now()

    user.hashed_password = PasswordUtils.get_hashed_password(data.new_password)

    if data.force_logout is True:
        user.rstr = generate_rstr(31)

    session.commit()

    send_email.delay(to=[user.email], subject="New password set")

    return {"message": "Successfully reset password"}
