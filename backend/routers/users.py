from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth import hash_password, require_admin
from database import get_db
from models import User
from services.users import (
    create_user,
    delete_user,
    get_user_by_id,
    get_user_by_username,
    list_users,
    update_user,
)

router = APIRouter(prefix="/users", tags=["users"])


class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool

    class Config:
        from_attributes = True


class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=8)
    is_admin: bool = False


class UpdateUserRequest(BaseModel):
    username: str | None = Field(None, min_length=1, max_length=64)
    password: str | None = Field(None, min_length=8)
    is_admin: bool | None = None


@router.get("", response_model=list[UserOut])
async def list_users_endpoint(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return list_users(db)


@router.post("", response_model=UserOut, status_code=201)
async def create_user_endpoint(
    body: CreateUserRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if get_user_by_username(db, body.username):
        raise HTTPException(status_code=409, detail="Username already exists")
    return create_user(db, body.username, hash_password(body.password), body.is_admin)


@router.put("/{user_id}", response_model=UserOut)
async def update_user_endpoint(
    user_id: int,
    body: UpdateUserRequest,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updates = {}
    if body.username is not None:
        existing = get_user_by_username(db, body.username)
        if existing and existing.id != user_id:
            raise HTTPException(status_code=409, detail="Username already exists")
        updates["username"] = body.username
    if body.password is not None:
        updates["hashed_password"] = hash_password(body.password)
    if body.is_admin is not None:
        # Prevent admin from revoking their own admin
        if user_id == current_admin.id and not body.is_admin:
            raise HTTPException(status_code=400, detail="Cannot revoke your own admin role")
        updates["is_admin"] = body.is_admin

    if updates:
        update_user(db, user_id, **updates)

    return get_user_by_id(db, user_id)


@router.delete("/{user_id}", status_code=204)
async def delete_user_endpoint(
    user_id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    if not get_user_by_id(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    delete_user(db, user_id)
