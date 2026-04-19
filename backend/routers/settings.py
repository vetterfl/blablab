from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth import get_current_user, verify_password, hash_password
from config import AVAILABLE_MODELS
from database import get_db
from limiter import limiter
from models import User
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
):
    return SettingsOut(
        default_model=current_user.default_model,
        available_models=AVAILABLE_MODELS,
    )


@router.put("")
async def update_settings(
    body: UpdateDefaultModel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.default_model not in AVAILABLE_MODELS:
        raise HTTPException(status_code=400, detail=f"Unknown model: {body.default_model}")

    update_default_model(db, current_user.id, body.default_model)
    return {"default_model": body.default_model}


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
