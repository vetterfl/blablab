from sqlalchemy.orm import Session

from config import settings
from models import AppSettings


def get_app_settings(db: Session) -> AppSettings:
    row = db.query(AppSettings).filter(AppSettings.id == 1).first()
    if row is None:
        row = AppSettings(id=1, transcription_model=settings.transcription_model)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def set_transcription_model(db: Session, model: str) -> AppSettings:
    row = get_app_settings(db)
    row.transcription_model = model
    db.commit()
    db.refresh(row)
    return row
