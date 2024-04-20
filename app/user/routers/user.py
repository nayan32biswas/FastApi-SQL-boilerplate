from fastapi import APIRouter

from app.core.deps.auth import CurrentUser
from app.core.deps.db import SessionDep
from app.core.utils.model import update_model

from ..schemas.user import UserProfileIn, UserProfileOut

router = APIRouter(prefix="/user")


@router.get("/profile", response_model=UserProfileOut)
async def get_profile(
    user: CurrentUser,
):
    return UserProfileOut.model_validate(user)


@router.put("/profile", response_model=UserProfileOut)
async def update_profile(
    user: CurrentUser,
    session: SessionDep,
    data: UserProfileIn,
):
    user = update_model(user, data)
    session.commit()

    session.refresh(user)

    return UserProfileOut.model_validate(user)
