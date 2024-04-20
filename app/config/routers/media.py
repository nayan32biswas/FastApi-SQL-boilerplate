import os

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.deps.auth import CurrentUser
from app.core.deps.db import SessionDep
from app.core.utils.file import FileNotFoundException, get_media_full_path, save_file

router = APIRouter()


@router.post("/api/v1/upload-file")
async def create_upload_file(
    user: CurrentUser,
    session: SessionDep,
    file: UploadFile = File(...),
):
    file_path = save_file(session, user.id, file, root_folder="file")

    return file_path


def get_file_response(file_path):
    if settings.ENV == "prod":
        NotImplementedError("API is not implemented")

    full_path = get_media_full_path(file_path)

    if os.path.isfile(full_path):
        return FileResponse(full_path)
    else:
        raise FileNotFoundException(message="File not found")


@router.get("/media/{file_path:path}")
async def get_file(file_path: str):
    return get_file_response(file_path)
