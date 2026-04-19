from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from auth import create_access_token, get_user, verify_password
from limiter import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest):
    user = get_user(body.username)
    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}
