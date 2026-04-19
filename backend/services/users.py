from sqlalchemy.orm import Session
from models import User, Preset
from config import load_presets


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.username).all()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def delete_user(db: Session, user_id: int) -> None:
    db.query(User).filter(User.id == user_id).delete()
    db.commit()


def update_user(db: Session, user_id: int, **kwargs) -> User | None:
    db.query(User).filter(User.id == user_id).update(kwargs)
    db.commit()
    return get_user_by_id(db, user_id)


def create_user(db: Session, username: str, hashed_password: str, is_admin: bool = False) -> User:
    user = User(username=username, hashed_password=hashed_password, is_admin=is_admin)
    db.add(user)
    db.flush()  # populate user.id before creating presets

    presets = load_presets()
    for position, preset in enumerate(presets):
        db.add(Preset(
            user_id=user.id,
            slug=preset["id"],
            label=preset["label"],
            prompt=preset["prompt"],
            position=position,
        ))

    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user_id: int, new_hashed_password: str) -> None:
    db.query(User).filter(User.id == user_id).update(
        {"hashed_password": new_hashed_password}
    )
    db.commit()


def update_default_model(db: Session, user_id: int, model: str | None) -> None:
    db.query(User).filter(User.id == user_id).update({"default_model": model})
    db.commit()
