from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import uuid
from typing import List
from models.lead import LeadCreate, Lead, LeadUpdate
from database import get_db
from models.opportunity import OpportunityCreate
from utils.middleware import get_current_user
from utils.task_id_generator import generate_task_id

router = APIRouter(prefix="/leads", tags=["Leads"])





@router.get("", response_model=List[Lead])
async def get_leads(current_user: dict = Depends(get_current_user)):
    db = get_db()
    leads = await db.leads.find({}, {"_id": 0}).to_list(1000)
    
    # Add task_id to existing leads if missing
    for lead in leads:
        if not lead.get("task_id"):
            lead["task_id"] = f"LEAD-{lead.get('id', 'UNKNOWN')[:8].upper()}"
    
    return leads

@router.get("/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Add task_id if missing
    if not lead.get("task_id"):
        lead["task_id"] = f"LEAD-{lead.get('id', 'UNKNOWN')[:8].upper()}"
    
    return lead

@router.post("", response_model=Lead, status_code=status.HTTP_201_CREATED)
async def create_lead(lead_data: LeadCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    lead_dict = lead_data.model_dump()
    
    # Generate Task ID
    task_id = await generate_task_id(db)
    lead_dict["task_id"] = task_id
    
    # Auto-fill lead owner with current user if not provided
    if not lead_dict.get("sales_poc"):
        lead_dict["sales_poc"] = current_user.get("email", "Unknown")
    
    # Handle date fields
    if "expected_closure_date" in lead_dict and lead_dict["expected_closure_date"]:
        lead_dict["expected_closure_date"] = lead_dict["expected_closure_date"].isoformat()
    if "next_followup" in lead_dict and lead_dict["next_followup"]:
        lead_dict["next_followup"] = lead_dict["next_followup"].isoformat()
    
    lead_dict["id"] = str(uuid.uuid4())
    lead_dict["linked_opportunity_id"] = None
    lead_dict["last_activity_date"] = None
    lead_dict["last_updated"] = datetime.now(timezone.utc).isoformat()
    
    # Use provided created_at or default to now
    if lead_dict.get("created_at"):
        if isinstance(lead_dict["created_at"], str) and 'T' not in lead_dict["created_at"]:
            lead_dict["created_at"] = lead_dict["created_at"] + "T00:00:00+00:00"
        elif isinstance(lead_dict["created_at"], datetime):
            lead_dict["created_at"] = lead_dict["created_at"].isoformat()
    else:
        lead_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    
    lead_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.leads.insert_one(lead_dict)
    return lead_dict

@router.put("/{lead_id}", response_model=Lead)
async def update_lead(lead_id: str, lead_data: LeadUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    update_dict = {k: v for k, v in lead_data.model_dump().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Handle date fields
    if "expected_closure_date" in update_dict and update_dict["expected_closure_date"]:
        update_dict["expected_closure_date"] = update_dict["expected_closure_date"].isoformat()
    if "next_followup" in update_dict and update_dict["next_followup"]:
        update_dict["next_followup"] = update_dict["next_followup"].isoformat()
    
    # Handle created_at update if provided
    if "created_at" in update_dict and update_dict["created_at"]:
        if isinstance(update_dict["created_at"], str) and 'T' not in update_dict["created_at"]:
            update_dict["created_at"] = update_dict["created_at"] + "T00:00:00+00:00"
        elif isinstance(update_dict["created_at"], datetime):
            update_dict["created_at"] = update_dict["created_at"].isoformat()
    
    # Always update last_updated and updated_at
    update_dict["last_updated"] = datetime.now(timezone.utc).isoformat()
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Get current lead for conversion logic
    lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Auto-convert to Opportunity if sales_stage is "Closed Won"
    if update_dict.get("sales_stage") == "Closed Won" or lead.get("sales_stage") == "Closed Won":
        # Check if already converted
        if not lead.get("linked_opportunity_id") and not update_dict.get("linked_opportunity_id"):
            # Create Opportunity with SAME Task ID
            opportunity_dict = {
                "id": str(uuid.uuid4()),
                "task_id": lead["task_id"],  # SHARE the same Task ID
                "client_name": lead["client_name"],
                "opportunity_name": lead["opportunity_name"],
                "deal_value": lead.get("estimated_value", 0),
                "probability_percent": lead.get("probability", 100),  # Closed Won = 100%
                "win_loss_reason": None,
                "last_interaction": None,
                "next_action": lead.get("next_action"),
                "industry": lead.get("industry"),
                "region": lead.get("region"),
                "country": lead.get("country"),
                "solution": lead.get("solution"),
                "estimated_value": lead.get("estimated_value", 0),
                "currency": lead.get("currency", "USD"),
                "probability": 100,  # Closed Won = 100%
                "stage": "Closed Won",
                "expected_closure_date": lead.get("expected_closure_date"),
                "sales_owner": lead.get("sales_poc"),
                "technical_poc": None,
                "presales_poc": None,
                "key_stakeholders": None,
                "competitors": None,
                "next_steps": lead.get("next_action"),
                "risks": None,
                "status": "Won",
                "linked_lead_id": lead_id,
                "linked_sow_id": None,
                "attachments": lead.get("attachments", []),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await db.opportunities.insert_one(opportunity_dict)
            
            # Update lead with linked opportunity
            update_dict["linked_opportunity_id"] = opportunity_dict["id"]
            update_dict["lead_status"] = "Converted"
    
    result = await db.leads.update_one({"id": lead_id}, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
    return lead

@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(lead_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    result = await db.leads.delete_one({"id": lead_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    return None