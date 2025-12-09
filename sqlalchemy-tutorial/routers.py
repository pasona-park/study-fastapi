from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

import services


class UserCreate(BaseModel):
    name: str
    fullname: str


class UserUpdate(BaseModel):
    name: str | None = None
    fullname: str | None = None

router = APIRouter()


@router.get("/users", tags=["users"])
def read_users(db: Session = Depends(get_db)):
    return services.get_users(db)


@router.get("/users/{user_id}", tags=["users"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = services.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users", tags=["users"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return services.create_user(db, user.name, user.fullname)


@router.put("/users/{user_id}", tags=["users"])
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    updated = services.update_user(db, user_id, user.name, user.fullname)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@router.delete("/users/{user_id}", tags=["users"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted = services.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@router.get("/addresses")
def read_addresses(db: Session = Depends(get_db)):
    return services.get_addresses(db)
