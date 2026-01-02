from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import uuid
from typing import List
from models.settings import SettingCreate, Setting, SettingUpdate
from database import get_db
from utils.middleware import get_current_user, require_admin

router = APIRouter(prefix="/settings", tags=["Settings"])





@router.get("", response_model=List[Setting])
async def get_settings(current_user: dict = Depends(get_current_user)):
    db = get_db()
    settings = await db.settings.find({}, {"_id": 0}).to_list(1000)
    return settings

@router.get("/regions", response_model=List[dict])
async def get_regions(current_user: dict = Depends(get_current_user)):
    """Get regions from settings - used for dropdowns and filters"""
    db = get_db()
    regions_setting = await db.settings.find_one({"setting_type": "regions"}, {"_id": 0})
    
    if regions_setting and regions_setting.get("data"):
        return regions_setting["data"]
    
    # Fallback: return empty array if no regions are configured
    return []

@router.get("/{setting_type}", response_model=Setting)
async def get_setting(setting_type: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    setting = await db.settings.find_one({"setting_type": setting_type}, {"_id": 0})
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@router.post("", response_model=Setting, status_code=status.HTTP_201_CREATED)
async def create_setting(setting_data: SettingCreate, current_user: dict = Depends(require_admin)):
    db = get_db()
    # Check if setting already exists
    existing = await db.settings.find_one({"setting_type": setting_data.setting_type}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Setting already exists")
    
    setting_dict = setting_data.model_dump()
    setting_dict["id"] = str(uuid.uuid4())
    setting_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    setting_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.settings.insert_one(setting_dict)
    return setting_dict

@router.put("/{setting_type}", response_model=Setting)
async def update_setting(setting_type: str, setting_data: SettingUpdate, current_user: dict = Depends(require_admin)):
    db = get_db()
    update_dict = {k: v for k, v in setting_data.model_dump().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.settings.update_one({"setting_type": setting_type}, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    setting = await db.settings.find_one({"setting_type": setting_type}, {"_id": 0})
    return setting

@router.delete("/{setting_type}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_setting(setting_type: str, current_user: dict = Depends(require_admin)):
    db = get_db()
    result = await db.settings.delete_one({"setting_type": setting_type})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Setting not found")
    return None