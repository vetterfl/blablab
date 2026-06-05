from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth import get_current_user
from config import settings
from database import get_db
from limiter import limiter
from models import User
from services.app_settings import get_app_settings
from services.llm import refine_text
from services.presets import get_preset_by_slug

router = APIRouter()


class RefineRequest(BaseModel):
    transcript: str = Field(..., min_length=1)
    preset_id: str = Field(..., min_length=1, max_length=100)
    context: str = Field(default="", max_length=5000)


class AdhocRefineRequest(BaseModel):
    transcript: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1, max_length=2000)
    model: str | None = None


def _check_transcript_length(db: Session, transcript: str) -> None:
    limit = get_app_settings(db).max_transcript_chars
    if len(transcript) > limit:
        raise HTTPException(
            status_code=413,
            detail=f"Transcript too long (max {limit} chars)",
        )


@router.post("/refine")
@limiter.limit("30/minute")
async def refine_endpoint(
    request: Request,
    body: RefineRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not body.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript is empty")

    _check_transcript_length(db, body.transcript)

    preset = get_preset_by_slug(db, current_user.id, body.preset_id)
    if preset is None:
        raise HTTPException(
            status_code=400, detail=f"Unknown preset: {body.preset_id}"
        )

    model = preset.model or current_user.default_model or settings.openrouter_model

    user_content = body.transcript
    if body.context.strip():
        user_content = f"Context:\n{body.context}\n\n---\n\n{user_content}"

    try:
        result = await refine_text(user_content, preset.prompt, model)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {"refined": result["content"], "cost_usd": result.get("cost_usd")}


@router.post("/refine/adhoc")
@limiter.limit("30/minute")
async def refine_adhoc_endpoint(
    request: Request,
    body: AdhocRefineRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not body.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript is empty")

    _check_transcript_length(db, body.transcript)

    model = body.model or current_user.default_model or settings.openrouter_model

    try:
        result = await refine_text(body.transcript, body.prompt, model)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {"refined": result["content"], "cost_usd": result.get("cost_usd")}
