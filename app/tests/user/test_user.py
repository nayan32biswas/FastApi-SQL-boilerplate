from uuid import uuid4

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.main import app
from app.user.models import User


async def test_get_profile(client: AsyncClient, default_user_headers: dict[str, str]) -> None:
    url = app.url_path_for("get_profile")

    response = await client.get(url, headers=default_user_headers)

    assert response.status_code == status.HTTP_200_OK


async def test_update_profile(
    client: AsyncClient,
    session: Session,
    default_user: User,
    default_user_headers: dict[str, str],
) -> None:
    url = app.url_path_for("update_profile")

    random_full_name = f"{uuid4().hex} {uuid4().hex}"
    payload = {"full_name": random_full_name, "image": ""}

    response = await client.put(url, json=payload, headers=default_user_headers)

    assert response.status_code == status.HTTP_200_OK

    session.refresh(default_user)

    assert default_user.full_name, random_full_name
