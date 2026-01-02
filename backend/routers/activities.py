from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import uuid
from typing import List
from models.activity import ActivityCreate, Activity, ActivityUpdate
from database import get_db
from utils.middleware import get_current_user

router = APIRouter(prefix="/activities", tags=["Activities"])





@router.get("", response_model=List[Activity])
async def get_activities(current_user: dict = Depends(get_current_user)):
    db = get_db()
    activities = await db.activities.find({}, {"_id": 0}).to_list(1000)
    return activities

@router.get("/{activity_id}", response_model=Activity)
async def get_activity(activity_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    activity = await db.activities.find_one({"id": activity_id}, {"_id": 0})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity

@router.post("", response_model=Activity, status_code=status.HTTP_201_CREATED)
async def create_activity(activity_data: ActivityCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    activity_dict = activity_data.model_dump()
    if "due_date" in activity_dict and activity_dict["due_date"]:
        activity_dict["due_date"] = activity_dict["due_date"].isoformat()
    
    activity_dict["id"] = str(uuid.uuid4())
    activity_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    activity_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.activities.insert_one(activity_dict)
    return activity_dict

@router.put("/{activity_id}", response_model=Activity)
async def update_activity(activity_id: str, activity_data: ActivityUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    update_dict = {k: v for k, v in activity_data.model_dump().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    if "due_date" in update_dict and update_dict["due_date"]:
        update_dict["due_date"] = update_dict["due_date"].isoformat()
    
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.activities.update_one({"id": activity_id}, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    activity = await db.activities.find_one({"id": activity_id}, {"_id": 0})
    return activity

@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(activity_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    result = await db.activities.delete_one({"id": activity_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Activity not found")
    return None