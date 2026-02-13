import os
import uuid

from fastapi import APIRouter, Depends, UploadFile, File

from app.config import settings
from app.core.deps import get_current_user
from app.core.response import AjaxResult

router = APIRouter(tags=["公共接口"])


@router.post("/common/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Common file upload endpoint."""
    upload_dir = os.path.join(settings.UPLOAD_PATH, "files")
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(file.filename)[1] if file.filename else ""
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, filename)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    file_url = f"/profile/files/{filename}"
    return AjaxResult.success(
        fileName=file_url,
        url=file_url,
        newFileName=filename,
        originalFilename=file.filename,
    )
