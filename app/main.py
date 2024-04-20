import logging
import traceback

from fastapi import FastAPI, Request, status
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.routers import router as config_router
from app.core.config import settings
from app.core.exceptions import CustomException
from app.user.routers import router as user_router

logger = logging.getLogger(__name__)


def init_routers(fastapi_app: FastAPI) -> None:
    fastapi_app.include_router(config_router, tags=["Config"])
    fastapi_app.include_router(user_router, tags=["User"])


def init_listeners(fastapi_app: FastAPI) -> None:
    @fastapi_app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )

    @fastapi_app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        traceback_str = traceback.format_exc()
        logger.error(traceback_str)

        if settings.DEBUG:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "message": traceback_str,
                },
            )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "Internal Server Error",
            },
        )


def make_middleware() -> list[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    ]
    return middleware


def create_app() -> FastAPI:
    fastapi_app = FastAPI(
        title="FastAPI SQL Boilerplate",
        description="FastAPI SQL Boilerplate API",
        version="1.0.0",
        docs_url=None if settings.ENV == "prod" else "/docs",
        redoc_url=None if settings.ENV == "prod" else "/redoc",
        middleware=make_middleware(),
    )
    init_routers(fastapi_app=fastapi_app)
    init_listeners(fastapi_app=fastapi_app)
    return fastapi_app


app = create_app()
