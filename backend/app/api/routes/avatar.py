import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, UserPublic

router = APIRouter(prefix="/users", tags=["users"])

# Directory to store avatars
AVATAR_DIR = Path("static/avatars")
AVATAR_DIR.mkdir(parents=True, exist_ok=True)

# Allowed image types
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB


@router.post("/me/avatar", response_model=UserPublic)
async def upload_avatar(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile = File(...),
) -> Any:
    """
    Upload avatar for current user.
    """
    # Validate content type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_TYPES)}",
        )

    # Read and validate file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    # Generate unique filename
    file_ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{file_ext}"
    file_path = AVATAR_DIR / filename

    # Delete old avatar if exists
    if current_user.avatar_url:
        old_filename = current_user.avatar_url.split("/")[-1]
        old_path = AVATAR_DIR / old_filename
        if old_path.exists():
            old_path.unlink()

    # Resize image to reasonable size (max 256x256)
    try:
        from io import BytesIO
        img = Image.open(BytesIO(content))
        img.thumbnail((256, 256), Image.Resampling.LANCZOS)

        # Convert to RGB if necessary (for PNG with transparency)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            file_ext = "jpg"
            filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{file_ext}"
            file_path = AVATAR_DIR / filename

        # Save the resized image
        img.save(file_path, quality=85, optimize=True)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process image: {str(e)}",
        )

    # Update user's avatar_url
    avatar_url = f"/static/avatars/{filename}"
    current_user.avatar_url = avatar_url
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete("/me/avatar", response_model=Message)
async def delete_avatar(
    *,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Delete avatar for current user.
    """
    if current_user.avatar_url:
        # Delete the file
        filename = current_user.avatar_url.split("/")[-1]
        file_path = AVATAR_DIR / filename
        if file_path.exists():
            file_path.unlink()

        # Clear the avatar_url
        current_user.avatar_url = None
        session.add(current_user)
        session.commit()

    return Message(message="Avatar deleted successfully")
