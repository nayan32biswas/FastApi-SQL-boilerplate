import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict

import jwt
from pydantic import BaseModel

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    settings,
)
from app.core.exceptions import CustomException

logger = logging.getLogger(__name__)


class TokenType(str, Enum):
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"


class TokenData(BaseModel):
    id: int
    rstr: str


class TokenException(CustomException):
    code = 401
    error_code = "TOKEN_ERROR"
    message = "Invalid token"


class JWTProvider:
    @classmethod
    def _create_token(cls, payload: Dict[str, Any], exp: timedelta) -> str:
        expire = datetime.now() + exp

        payload["exp"] = expire
        payload["iat"] = time.time()

        try:
            token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        except Exception as e:
            raise TokenException(message="Invalid Token") from e

        return token

    @classmethod
    def create_access_token(cls, id: int, rstr: str) -> str:
        payload = {
            "id": id,
            "rstr": rstr,
            "token_type": TokenType.ACCESS,
        }

        return cls._create_token(payload, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    @classmethod
    def create_refresh_token(cls, id: int, rstr: str) -> str:
        payload = {
            "id": id,
            "rstr": rstr,
            "token_type": TokenType.REFRESH,
        }

        return cls._create_token(payload, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

    @classmethod
    def _decode_token(cls, token: str) -> Dict[str, Any]:
        if not token:
            raise TokenException(message="Invalid Token")

        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except jwt.exceptions.DecodeError as e:
            raise TokenException from e
        except jwt.exceptions.ExpiredSignatureError as e:
            raise TokenException(message="Expired token") from e

        if "token_type" not in payload:
            raise TokenException(message="Invalid Token")

        return payload

    @classmethod
    def decode_access_token(cls, token: str):
        payload = cls._decode_token(token)

        if payload["token_type"] != TokenType.ACCESS:
            raise TokenException(message="Invalid Access Token")

        try:
            return TokenData(id=payload["id"], rstr=payload["rstr"])
        except Exception as e:
            raise TokenException(message="Invalid Access Token") from e

    @classmethod
    def decode_refresh_token(cls, token: str):
        payload = cls._decode_token(token)

        if payload["token_type"] != TokenType.REFRESH:
            raise TokenException(message="Invalid Refresh Token")

        try:
            return TokenData(id=payload["id"], rstr=payload["rstr"])
        except Exception as e:
            raise TokenException(message="Invalid Refresh Token") from e
