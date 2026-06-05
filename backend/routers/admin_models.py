from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth import get_current_user, require_admin
from database import get_db
from models import User
from services.available_models import (
    KIND_REFINE,
    KIND_TRANSCRIPTION,
    VALID_KINDS,
    add_model,
    delete_model,
    list_models,
)
from services.openrouter_catalog import catalog_slugs, slug_exists

router = APIRouter(prefix="/admin/models", tags=["admin-models"])


class ModelOut(BaseModel):
    id: int
    slug: str
    kind: str
    position: int

    class Config:
        from_attributes = True


class ModelCreate(BaseModel):
    slug: str = Field(..., min_length=1, max_length=200)
    kind: str = Field(..., pattern="^(refine|transcription)$")


def _check_kind(kind: str) -> None:
    if kind not in VALID_KINDS:
        raise HTTPException(status_code=400, detail=f"Invalid kind: {kind}")


@router.get("", response_model=list[ModelOut])
async def list_models_endpoint(
    kind: str = Query(...),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_kind(kind)
    return list_models(db, kind)


@router.post("", response_model=ModelOut, status_code=201)
async def add_model_endpoint(
    body: ModelCreate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    exists = await slug_exists(body.slug, kind=body.kind)
    if not exists:
        filter_note = (
            " (must be an audio-input model)" if body.kind == KIND_TRANSCRIPTION else ""
        )
        raise HTTPException(
            status_code=400,
            detail=f"Model '{body.slug}' not found in OpenRouter catalog{filter_note}",
        )
    return add_model(db, body.slug, body.kind)


@router.delete("/{model_id}", status_code=204)
async def delete_model_endpoint(
    model_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if not delete_model(db, model_id):
        raise HTTPException(status_code=404, detail="Model not found")


@router.get("/catalog")
async def get_catalog(
    kind: str | None = Query(None),
    _: User = Depends(require_admin),
):
    if kind is not None:
        _check_kind(kind)
    try:
        slugs = await catalog_slugs(kind)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return {"slugs": slugs}
