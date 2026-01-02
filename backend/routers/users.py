from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import uuid
from typing import List
from models.user import UserCreate, User, UserUpdate
from database import get_db
from utils.auth import get_password_hash
from utils.middleware import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["Users"])





@router.get("", response_model=List[User])
async def get_users(current_user: dict = Depends(get_current_user)):
    db = get_db()
    users = await db.users.find({}, {"_id": 0, "password": 0}).to_list(1000)
    return users

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, current_user: dict = Depends(require_admin)):
    db = get_db()
    existing_user = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = user_data.model_dump()
    user_dict["id"] = str(uuid.uuid4())
    user_dict["password"] = get_password_hash(user_data.password)
    user_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    user_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.users.insert_one(user_dict)
    user_dict.pop("password")
    return user_dict

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user_data: UserUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    # Users can update themselves, admins can update anyone
    if current_user["sub"] != user_id and current_user.get("role") != "Admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    
    update_dict = {k: v for k, v in user_data.model_dump().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    if "password" in update_dict:
        update_dict["password"] = get_password_hash(update_dict["password"])
    
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.users.update_one({"id": user_id}, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, current_user: dict = Depends(require_admin)):
    db = get_db()
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return None