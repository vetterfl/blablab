from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from models import AvailableModel

KIND_REFINE = "refine"
KIND_TRANSCRIPTION = "transcription"
VALID_KINDS = {KIND_REFINE, KIND_TRANSCRIPTION}

_YAML_FILES = {
    KIND_REFINE: "models.yaml",
    KIND_TRANSCRIPTION: "transcription_models.yaml",
}


def list_models(db: Session, kind: str) -> list[AvailableModel]:
    return (
        db.query(AvailableModel)
        .filter(AvailableModel.kind == kind)
        .order_by(AvailableModel.position, AvailableModel.id)
        .all()
    )


def list_slugs(db: Session, kind: str) -> list[str]:
    return [m.slug for m in list_models(db, kind)]


def add_model(db: Session, slug: str, kind: str) -> AvailableModel:
    existing = (
        db.query(AvailableModel)
        .filter(AvailableModel.slug == slug, AvailableModel.kind == kind)
        .first()
    )
    if existing:
        return existing
    next_pos = (
        db.query(AvailableModel)
        .filter(AvailableModel.kind == kind)
        .count()
    )
    row = AvailableModel(slug=slug, kind=kind, position=next_pos)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def delete_model(db: Session, model_id: int) -> bool:
    deleted = (
        db.query(AvailableModel)
        .filter(AvailableModel.id == model_id)
        .delete()
    )
    db.commit()
    return deleted > 0


def seed_from_yaml(db: Session) -> None:
    """Merge YAML slugs into DB: insert missing, leave existing untouched."""
    backend_dir = Path(__file__).resolve().parent.parent
    for kind, filename in _YAML_FILES.items():
        path = backend_dir / filename
        if not path.exists():
            continue
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        slugs = data.get("models") or []
        existing = {
            s for (s,) in db.query(AvailableModel.slug)
            .filter(AvailableModel.kind == kind)
            .all()
        }
        next_pos = (
            db.query(AvailableModel)
            .filter(AvailableModel.kind == kind)
            .count()
        )
        added = False
        for slug in slugs:
            if slug in existing:
                continue
            db.add(AvailableModel(slug=slug, kind=kind, position=next_pos))
            next_pos += 1
            added = True
        if added:
            db.commit()
