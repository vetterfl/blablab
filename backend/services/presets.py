from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from models import Preset


def get_user_presets(db: Session, user_id: int) -> list[Preset]:
    return (
        db.query(Preset)
        .filter(Preset.user_id == user_id)
        .order_by(Preset.position)
        .all()
    )


def get_preset_by_slug(db: Session, user_id: int, slug: str) -> Preset | None:
    return (
        db.query(Preset)
        .filter(Preset.user_id == user_id, Preset.slug == slug)
        .first()
    )


def create_preset(
    db: Session,
    user_id: int,
    slug: str,
    label: str,
    prompt: str,
    model: str | None = None,
    subject_field: bool = False,
) -> Preset:
    max_pos = (
        db.query(func.max(Preset.position))
        .filter(Preset.user_id == user_id)
        .scalar()
    )
    position = (max_pos or 0) + 1

    preset = Preset(
        user_id=user_id,
        slug=slug,
        label=label,
        prompt=prompt,
        model=model,
        subject_field=subject_field,
        position=position,
    )
    db.add(preset)
    db.commit()
    db.refresh(preset)
    return preset


def update_preset(db: Session, preset: Preset, **kwargs) -> Preset:
    for key, value in kwargs.items():
        setattr(preset, key, value)
    preset.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(preset)
    return preset


def delete_preset(db: Session, preset: Preset) -> None:
    db.delete(preset)
    db.commit()
