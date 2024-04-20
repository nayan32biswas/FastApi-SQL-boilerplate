import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

JWT_ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 3600
REFRESH_TOKEN_EXPIRE_DAYS: int = 30

FORGOT_PASSWORD_PATH = "forgot-password-set"
FORGOT_PASSWORD_EXPIRE_MINUTES: int = 100

DOTENV = os.path.join(BASE_DIR, ".env")


class Settings(BaseSettings):
    DEBUG: bool = True
    ENV: str = ""
    APP_HOST: str = ""
    API_HOST: str = ""
    JWT_SECRET_KEY: str = ""
    ALLOWED_HOSTS: str = "*"

    DB_URL: str = ""

    CELERY_BROKER_URL: str = ""
    CELERY_BACKEND_URL: str = ""
    CELERY_CONCURRENCY: int = 2

    model_config = SettingsConfigDict(env_file=DOTENV)


class TestSettings(Settings):
    ENV: str = "test"


class DevSettings(Settings):
    ENV: str = "dev"


class ProductionSettings(Settings):
    DEBUG: bool = False
    ENV: str = "prod"


def get_settings():
    env = os.getenv("ENV", "dev")
    config_type = {
        "test": TestSettings(),
        "dev": DevSettings(),
        "prod": ProductionSettings(),
    }
    return config_type[env]


settings: Settings = get_settings()
