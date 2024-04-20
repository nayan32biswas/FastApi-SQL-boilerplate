from uuid import uuid4

import sqlalchemy as sa
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core.auth import PasswordUtils
from app.core.auth.jwt import JWTProvider
from app.core.utils.string import generate_rstr
from app.main import app
from app.tests.data import default_user_password
from app.user.models import ForgotPassword, User


async def test_registration(client: AsyncClient) -> None:
    url = app.url_path_for("registration")

    payload = {
        "email": f"testing-{uuid4().hex}@example.com",
        "password": default_user_password,
        "full_name": "User Name",
    }

    response = await client.post(url, json=payload)

    assert response.status_code == status.HTTP_201_CREATED


async def test_login(client: AsyncClient, default_user: User) -> None:
    url = app.url_path_for("token_login")

    payload = {
        "email": default_user.email,
        "password": default_user_password,
    }
    response = await client.post(url, json=payload)

    assert response.status_code == status.HTTP_200_OK


async def test_refresh_token(client: AsyncClient, default_user: User):
    url = app.url_path_for("refresh_token")

    refresh_token = JWTProvider.create_refresh_token(default_user.id, default_user.rstr)

    payload = {"refresh_token": refresh_token}
    response = await client.post(url, json=payload)
    assert response.status_code, status.HTTP_200_OK

    """Test With wrong token"""
    access_token = JWTProvider.create_access_token(default_user.id, default_user.rstr)

    payload = {"refresh_token": access_token}
    response = await client.post(url, json=payload)
    assert response.status_code, status.HTTP_403_FORBIDDEN


async def test_change_password(
    client: AsyncClient,
    session: Session,
    default_user: User,
    default_user_headers: dict[str, str],
):
    url = app.url_path_for("change_password")

    new_password = generate_rstr(10)

    payload = {"old_password": default_user_password, "new_password": new_password}
    response = await client.post(url, json=payload, headers=default_user_headers)

    assert response.status_code, status.HTTP_200_OK

    session.refresh(default_user)
    assert PasswordUtils.verify_password(new_password, default_user.hashed_password) is True

    """Set to default password"""
    default_user.hashed_password = PasswordUtils.get_hashed_password(default_user_password)
    session.commit()

    """Try with wrong old password"""
    payload = {"old_password": generate_rstr(10), "new_password": new_password}
    response = await client.post(url, json=payload, headers=default_user_headers)

    assert response.status_code, status.HTTP_403_FORBIDDEN


async def test_forgot_password(client: AsyncClient, session: Session, default_user: User):
    request_url = app.url_path_for("forgot_password_request")

    payload = {"email": default_user.email}
    response = await client.post(request_url, json=payload)

    assert response.status_code, status.HTTP_200_OK

    stmt = (
        sa.select(ForgotPassword)
        .where(
            ForgotPassword.user_id == default_user.id,
            ForgotPassword.is_used == False,  # noqa: E712
        )
        .order_by(sa.desc(ForgotPassword.id))
    )
    forgot_password_instance = session.scalars(stmt).first()

    payload = {
        "new_password": "new-pass",
        "token": forgot_password_instance.token,
    }

    reset_url = app.url_path_for("forgot_password_reset")

    response = await client.post(reset_url, json=payload)

    assert response.status_code, status.HTTP_200_OK

    session.refresh(default_user)

    assert PasswordUtils.verify_password(payload["new_password"], default_user.hashed_password)

    default_user.hashed_password = PasswordUtils.get_hashed_password(default_user_password)
    session.commit()
