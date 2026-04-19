from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import User
from services.presets import (
    get_user_presets,
    get_preset_by_slug,
    create_preset,
    update_preset,
    delete_preset,
)

router = APIRouter(prefix="/presets", tags=["presets"])


class PresetOut(BaseModel):
    slug: str
    label: str
    prompt: str
    model: str | None = None
    subject_field: bool = False
    position: int

    class Config:
        from_attributes = True


class PresetCreate(BaseModel):
    slug: str = Field(..., min_length=1, max_length=100)
    label: str = Field(..., min_length=1, max_length=200)
    prompt: str = Field(..., min_length=1)
    model: str | None = None
    subject_field: bool = False


class PresetUpdate(BaseModel):
    label: str | None = None
    prompt: str | None = None
    model: str | None = None
    subject_field: bool | None = None


@router.get("")
async def list_presets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    presets = get_user_presets(db, current_user.id)
    return {
        "presets": [
            PresetOut.model_validate(p).model_dump() for p in presets
        ]
    }


@router.post("", status_code=201)
async def create_preset_endpoint(
    body: PresetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = get_preset_by_slug(db, current_user.id, body.slug)
    if existing:
        raise HTTPException(status_code=409, detail=f"Preset '{body.slug}' already exists")

    preset = create_preset(
        db,
        user_id=current_user.id,
        slug=body.slug,
        label=body.label,
        prompt=body.prompt,
        model=body.model,
        subject_field=body.subject_field,
    )
    return PresetOut.model_validate(preset).model_dump()


@router.put("/{slug}")
async def update_preset_endpoint(
    slug: str,
    body: PresetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    preset = get_preset_by_slug(db, current_user.id, slug)
    if preset is None:
        raise HTTPException(status_code=404, detail=f"Preset '{slug}' not found")

    updates = body.model_dump(exclude_unset=True)
    updated = update_preset(db, preset, **updates)
    return PresetOut.model_validate(updated).model_dump()


@router.delete("/{slug}", status_code=204)
async def delete_preset_endpoint(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    preset = get_preset_by_slug(db, current_user.id, slug)
    if preset is None:
        raise HTTPException(status_code=404, detail=f"Preset '{slug}' not found")

    delete_preset(db, preset)
