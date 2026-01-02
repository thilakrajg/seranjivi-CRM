from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import uuid
from typing import List
from models.sow import SOWCreate, SOW, SOWUpdate
from database import get_db
from utils.middleware import get_current_user

router = APIRouter(prefix="/sows", tags=["SOWs"])





@router.get("", response_model=List[SOW])
async def get_sows(current_user: dict = Depends(get_current_user)):
    db = get_db()
    sows = await db.sows.find({}, {"_id": 0}).to_list(1000)
    return sows

@router.get("/{sow_id}", response_model=SOW)
async def get_sow(sow_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    sow = await db.sows.find_one({"id": sow_id}, {"_id": 0})
    if not sow:
        raise HTTPException(status_code=404, detail="SOW not found")
    return sow

@router.post("", response_model=SOW, status_code=status.HTTP_201_CREATED)
async def create_sow(sow_data: SOWCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    sow_dict = sow_data.model_dump()
    if "start_date" in sow_dict and sow_dict["start_date"]:
        sow_dict["start_date"] = sow_dict["start_date"].isoformat()
    if "end_date" in sow_dict and sow_dict["end_date"]:
        sow_dict["end_date"] = sow_dict["end_date"].isoformat()
    
    sow_dict["id"] = str(uuid.uuid4())
    sow_dict["linked_opportunity_id"] = None
    sow_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    sow_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.sows.insert_one(sow_dict)
    return sow_dict

@router.put("/{sow_id}", response_model=SOW)
async def update_sow(sow_id: str, sow_data: SOWUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    update_dict = {k: v for k, v in sow_data.model_dump().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    if "start_date" in update_dict and update_dict["start_date"]:
        update_dict["start_date"] = update_dict["start_date"].isoformat()
    if "end_date" in update_dict and update_dict["end_date"]:
        update_dict["end_date"] = update_dict["end_date"].isoformat()
    
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Auto-create Kickoff Activity if status is Completed
    if update_dict.get("status") == "Completed":
        sow = await db.sows.find_one({"id": sow_id}, {"_id": 0})
        if not sow:
            raise HTTPException(status_code=404, detail="SOW not found")
        
        # Create Kickoff Activity
        activity_dict = {
            "id": str(uuid.uuid4()),
            "activity_type": "Meeting",
            "title": f"Kickoff Meeting - {sow['project_name']}",
            "description": f"Project kickoff for {sow['project_name']}",
            "related_to": "SOW",
            "related_id": sow_id,
            "assigned_to": sow.get("delivery_spoc"),
            "status": "Pending",
            "due_date": datetime.now(timezone.utc).isoformat(),
            "notes": "Auto-generated kickoff activity",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.activities.insert_one(activity_dict)
    
    result = await db.sows.update_one({"id": sow_id}, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="SOW not found")
    
    sow = await db.sows.find_one({"id": sow_id}, {"_id": 0})
    return sow

@router.delete("/{sow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sow(sow_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    result = await db.sows.delete_one({"id": sow_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="SOW not found")
    return None