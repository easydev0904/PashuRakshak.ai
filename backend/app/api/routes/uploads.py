from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import get_current_user
from app.models.user import User
from app.services.upload_service import save_image_upload

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("", status_code=201)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> dict:
    url = await save_image_upload(file)
    return {"url": url}
