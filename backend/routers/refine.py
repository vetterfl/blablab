from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.llm import refine_text
from config import load_presets

router = APIRouter()


class RefineRequest(BaseModel):
    transcript: str
    preset_id: str


@router.post("/refine")
async def refine_endpoint(body: RefineRequest):
    if not body.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript is empty")

    presets = {p["id"]: p for p in load_presets()}

    if body.preset_id not in presets:
        raise HTTPException(
            status_code=400, detail=f"Unknown preset: {body.preset_id}"
        )

    preset = presets[body.preset_id]

    try:
        refined = await refine_text(body.transcript, preset["prompt"])
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {"refined": refined}
