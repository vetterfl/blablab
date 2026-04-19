from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth import get_current_user
from config import settings
from database import get_db
from models import User
from services.llm import refine_text
from services.presets import get_preset_by_slug

router = APIRouter()

MAX_TRANSCRIPT_CHARS = 2000


class RefineRequest(BaseModel):
    transcript: str = Field(..., min_length=1, max_length=MAX_TRANSCRIPT_CHARS)
    preset_id: str
    context: str = Field(default="", max_length=5000)


@router.post("/refine")
async def refine_endpoint(
    body: RefineRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not body.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript is empty")

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
        refined = await refine_text(user_content, preset.prompt, model)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {"refined": refined}
