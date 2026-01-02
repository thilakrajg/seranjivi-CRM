from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid
from typing import List
from models.action_item import ActionItemCreate, ActionItem, ActionItemUpdate
from database import get_db
from utils.middleware import get_current_user
from utils.task_id_generator import generate_task_id

router = APIRouter(prefix="/action-items", tags=["Action Items"])

@router.get("", response_model=List[ActionItem])
async def get_action_items(current_user: dict = Depends(get_current_user)):
    db = get_db()
    action_items = await db.action_items.find({}, {"_id": 0}).to_list(1000)
    
    # Add task_id to existing action items if missing
    for item in action_items:
        if not item.get("task_id"):
            item["task_id"] = f"ACT-{item.get('id', 'UNKNOWN')[:8].upper()}"
    
    return action_items

@router.get("/{action_item_id}", response_model=ActionItem)
async def get_action_item(action_item_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    action_item = await db.action_items.find_one({"id": action_item_id}, {"_id": 0})
    if not action_item:
        raise HTTPException(status_code=404, detail="Action item not found")
    
    # Add task_id if missing
    if not action_item.get("task_id"):
        action_item["task_id"] = f"ACT-{action_item.get('id', 'UNKNOWN')[:8].upper()}"
    
    return action_item

@router.post("", response_model=ActionItem, status_code=status.HTTP_201_CREATED)
async def create_action_item(action_item_data: ActionItemCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    action_item_dict = action_item_data.model_dump()
    
    # Generate Task ID if not provided (for standalone tasks)
    if not action_item_dict.get("task_id"):
        action_item_dict["task_id"] = await generate_task_id(db)
    
    if "due_date" in action_item_dict and action_item_dict["due_date"]:
        action_item_dict["due_date"] = action_item_dict["due_date"].isoformat()
    if "completed_date" in action_item_dict and action_item_dict["completed_date"]:
        action_item_dict["completed_date"] = action_item_dict["completed_date"].isoformat()
    
    action_item_dict["id"] = str(uuid.uuid4())
    action_item_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    action_item_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.action_items.insert_one(action_item_dict)
    return action_item_dict

@router.put("/{action_item_id}", response_model=ActionItem)
async def update_action_item(action_item_id: str, action_item_data: ActionItemUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    action_item = await db.action_items.find_one({"id": action_item_id})
    if not action_item:
        raise HTTPException(status_code=404, detail="Action item not found")
    
    update_data = action_item_data.model_dump(exclude_unset=True)
    if "due_date" in update_data and update_data["due_date"]:
        update_data["due_date"] = update_data["due_date"].isoformat()
    if "completed_date" in update_data and update_data["completed_date"]:
        update_data["completed_date"] = update_data["completed_date"].isoformat()
    
    # Auto-set completed_date when status changes to Completed
    if update_data.get("status") == "Completed" and not update_data.get("completed_date"):
        update_data["completed_date"] = datetime.now(timezone.utc).isoformat()
    
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.action_items.update_one({"id": action_item_id}, {"$set": update_data})
    updated_item = await db.action_items.find_one({"id": action_item_id}, {"_id": 0})
    return updated_item

@router.delete("/{action_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action_item(action_item_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    result = await db.action_items.delete_one({"id": action_item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Action item not found")
    return None
