from fastapi import APIRouter

from .common import router as common_router
from .media import router as media_v1_router

router = APIRouter()

router.include_router(common_router)
router.include_router(media_v1_router)


__all__ = ["router"]
