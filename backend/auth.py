import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt

from config import settings

logger = logging.getLogger(__name__)

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

USERS_FILE = Path(__file__).parent / "users.json"


def load_users() -> list[dict]:
    try:
        return json.loads(USERS_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning("users.json missing or malformed — no users loaded")
        return []


def get_user(username: str) -> dict | None:
    return next((u for u in load_users() if u["username"] == username), None)


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


async def get_current_user(token: str = Depends(_oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user
