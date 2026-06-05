from sqlalchemy.orm import Session

from config import settings
from models import AppSettings


def get_app_settings(db: Session) -> AppSettings:
    row = db.query(AppSettings).filter(AppSettings.id == 1).first()
    if row is None:
        row = AppSettings(
            id=1,
            transcription_model=settings.transcription_model,
            max_audio_bytes=settings.max_audio_bytes,
            max_recording_seconds=settings.max_recording_seconds,
            max_transcript_chars=settings.max_transcript_chars,
        )
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


def set_limits(
    db: Session,
    max_audio_bytes: int,
    max_recording_seconds: int,
    max_transcript_chars: int,
) -> AppSettings:
    row = get_app_settings(db)
    row.max_audio_bytes = max_audio_bytes
    row.max_recording_seconds = max_recording_seconds
    row.max_transcript_chars = max_transcript_chars
    db.commit()
    db.refresh(row)
    return row
