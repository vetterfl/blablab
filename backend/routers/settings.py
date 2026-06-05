from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth import get_current_user, require_admin, verify_password, hash_password
from database import get_db
from limiter import limiter
from models import User
from services.app_settings import get_app_settings, set_transcription_model
from services.available_models import KIND_REFINE, KIND_TRANSCRIPTION, list_slugs
from services.users import change_password, update_default_model

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingsOut(BaseModel):
    default_model: str | None
    available_models: list[str]


class UpdateDefaultModel(BaseModel):
    default_model: str = Field(..., min_length=1)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


@router.get("")
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SettingsOut(
        default_model=current_user.default_model,
        available_models=list_slugs(db, KIND_REFINE),
    )


@router.put("")
async def update_settings(
    body: UpdateDefaultModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.default_model not in list_slugs(db, KIND_REFINE):
        raise HTTPException(status_code=400, detail=f"Unknown model: {body.default_model}")

    update_default_model(db, current_user.id, body.default_model)
    return {"default_model": body.default_model}


class TranscriptionOut(BaseModel):
    transcription_model: str
    available_models: list[str]


class UpdateTranscription(BaseModel):
    transcription_model: str = Field(..., min_length=1)


@router.get("/transcription", response_model=TranscriptionOut)
async def get_transcription_settings(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = get_app_settings(db)
    return TranscriptionOut(
        transcription_model=row.transcription_model,
        available_models=list_slugs(db, KIND_TRANSCRIPTION),
    )


@router.put("/transcription", response_model=TranscriptionOut)
async def update_transcription_settings(
    body: UpdateTranscription,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if body.transcription_model not in list_slugs(db, KIND_TRANSCRIPTION):
        raise HTTPException(
            status_code=400,
            detail=f"Unknown transcription model: {body.transcription_model}",
        )
    row = set_transcription_model(db, body.transcription_model)
    return TranscriptionOut(
        transcription_model=row.transcription_model,
        available_models=list_slugs(db, KIND_TRANSCRIPTION),
    )


@router.post("/change-password")
@limiter.limit("5/minute")
async def change_password_endpoint(
    request: Request,
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    new_hashed = hash_password(body.new_password)
    change_password(db, current_user.id, new_hashed)
    return {"detail": "Password updated successfully"}
