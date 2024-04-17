from fastapi import APIRouter

from app.user.routers.auth import router as auth_v1_router
from app.user.routers.user import router as user_v1_router

router = APIRouter()
router.include_router(auth_v1_router, prefix="/api/v1", tags=["Auth"])
router.include_router(user_v1_router, prefix="/api/v1", tags=["User"])


__all__ = ["router"]
