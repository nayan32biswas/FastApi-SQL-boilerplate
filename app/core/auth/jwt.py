import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict

import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.core.config import settings
from app.core.constants import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS

logger = logging.getLogger(__name__)


class TokenType(str, Enum):
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"


class TokenData(BaseModel):
    id: int
    rstr: str


class JWTProvider:
    @classmethod
    def _create_token(cls, payload: Dict[str, Any], exp: timedelta) -> str:
        expire = datetime.now() + exp

        payload["exp"] = expire
        payload["iat"] = time.time()

        try:
            token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Token"
            ) from e

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
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Token")

        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        if "token_type" not in payload:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Token")

        return payload

    @classmethod
    def decode_access_token(cls, token: str):
        payload = cls._decode_token(token)

        if payload["token_type"] != TokenType.ACCESS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Access Token"
            )

        try:
            return TokenData(id=payload["id"], rstr=payload["rstr"])
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Access Token"
            ) from e

    @classmethod
    def decode_refresh_token(cls, token: str):
        payload = cls._decode_token(token)

        if payload["token_type"] != TokenType.REFRESH:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Refresh Token"
            )

        try:
            return TokenData(id=payload["id"], rstr=payload["rstr"])
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Refresh Token"
            ) from e
