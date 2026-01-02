from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import uuid
from typing import List
from models.partner import PartnerCreate, Partner, PartnerUpdate
from database import get_db
from utils.middleware import get_current_user

router = APIRouter(prefix="/partners", tags=["Partners"])





@router.get("", response_model=List[Partner])
async def get_partners(current_user: dict = Depends(get_current_user)):
    db = get_db()
    partners = await db.partners.find({}, {"_id": 0}).to_list(1000)
    return partners

@router.get("/{partner_id}", response_model=Partner)
async def get_partner(partner_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    partner = await db.partners.find_one({"id": partner_id}, {"_id": 0})
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner

@router.post("", response_model=Partner, status_code=status.HTTP_201_CREATED)
async def create_partner(partner_data: PartnerCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    partner_dict = partner_data.model_dump()
    partner_dict["id"] = str(uuid.uuid4())
    partner_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    partner_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.partners.insert_one(partner_dict)
    return partner_dict

@router.put("/{partner_id}", response_model=Partner)
async def update_partner(partner_id: str, partner_data: PartnerUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    update_dict = {k: v for k, v in partner_data.model_dump().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.partners.update_one({"id": partner_id}, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    partner = await db.partners.find_one({"id": partner_id}, {"_id": 0})
    return partner

@router.delete("/{partner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_partner(partner_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    result = await db.partners.delete_one({"id": partner_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Partner not found")
    return None