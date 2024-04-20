import logging
import os
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config.models import UploadedFile
from app.core.config import MEDIA_ROOT
from app.core.exceptions import ObjectNotFoundException

from .string import base64

logger = logging.getLogger(__name__)


class FileNotFoundException(ObjectNotFoundException):
    error_code = "FILE_NOT_FOUND"
    message = "File not found"


def get_folder_path(root_folder):
    base64_month = base64(datetime.now().strftime("%Y%m"))
    return f"{root_folder}/{base64_month}"


def get_extension(filename: str):
    name_list = filename.split(".")

    if len(name_list) < 2:
        raise Exception("File is not valid")

    return name_list[-1]


def save_file(
    session: Session, user_id: int, upload_file: UploadFile, root_folder: str
) -> Optional[str]:
    if not upload_file:
        return None

    ext = get_extension(upload_file.filename)

    folder_path = get_folder_path(root_folder)
    folder_location = f"{MEDIA_ROOT}/{folder_path}"
    filename = f"{uuid4().hex}.{ext}"

    if not os.path.exists(folder_location):
        os.makedirs(folder_location)

    file_full_path = f"{folder_location}/{filename}"

    try:
        with open(file_full_path, "wb+") as file_object:
            file_object.write(upload_file.file.read())

        file_path = f"/{folder_path}/{filename}"

        file_instance = UploadedFile(
            user_id=user_id,
            name=upload_file.filename,
            file_path=file_path,
            extension=ext,
        )

        session.add(file_instance)
        session.commit()

        return file_path
    except Exception as e:
        logger.error(f"Error in save_file. Error {e}")

        return None


def get_media_full_path(file_path):
    return f"{MEDIA_ROOT}/{file_path}"
