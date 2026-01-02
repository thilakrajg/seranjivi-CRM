from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid
from typing import List
from models.sales_activity import SalesActivityCreate, SalesActivity, SalesActivityUpdate
from database import get_db
from utils.middleware import get_current_user
from utils.task_id_generator import generate_task_id

router = APIRouter(prefix="/sales-activities", tags=["Sales Activities"])

@router.get("", response_model=List[SalesActivity])
async def get_sales_activities(current_user: dict = Depends(get_current_user)):
    db = get_db()
    activities = await db.sales_activities.find({}, {"_id": 0}).to_list(1000)
    
    # Add task_id to existing sales activities if missing
    for activity in activities:
        if not activity.get("task_id"):
            activity["task_id"] = f"SAL-{activity.get('id', 'UNKNOWN')[:8].upper()}"
    
    return activities

@router.get("/{activity_id}", response_model=SalesActivity)
async def get_sales_activity(activity_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    activity = await db.sales_activities.find_one({"id": activity_id}, {"_id": 0})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Add task_id if missing
    if not activity.get("task_id"):
        activity["task_id"] = f"SAL-{activity.get('id', 'UNKNOWN')[:8].upper()}"
    
    return activity

@router.post("", response_model=SalesActivity, status_code=status.HTTP_201_CREATED)
async def create_sales_activity(activity_data: SalesActivityCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    activity_dict = activity_data.model_dump()
    
    # Generate Task ID if not provided (for standalone activities)
    if not activity_dict.get("task_id"):
        activity_dict["task_id"] = await generate_task_id(db)
    
    if "activity_date" in activity_dict and activity_dict["activity_date"]:
        activity_dict["activity_date"] = activity_dict["activity_date"].isoformat()
    
    activity_dict["id"] = str(uuid.uuid4())
    activity_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    activity_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.sales_activities.insert_one(activity_dict)
    return activity_dict

@router.put("/{activity_id}", response_model=SalesActivity)
async def update_sales_activity(activity_id: str, activity_data: SalesActivityUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    activity = await db.sales_activities.find_one({"id": activity_id})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    update_data = activity_data.model_dump(exclude_unset=True)
    if "activity_date" in update_data and update_data["activity_date"]:
        update_data["activity_date"] = update_data["activity_date"].isoformat()
    
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.sales_activities.update_one({"id": activity_id}, {"$set": update_data})
    updated_activity = await db.sales_activities.find_one({"id": activity_id}, {"_id": 0})
    return updated_activity

@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sales_activity(activity_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    result = await db.sales_activities.delete_one({"id": activity_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Activity not found")
    return None
