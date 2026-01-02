from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class LeadStage(str, Enum):
    NEW = "New"
    IN_PROGRESS = "In Progress"
    QUALIFIED = "Qualified"
    UNQUALIFIED = "Unqualified"

class LeadStatus(str, Enum):
    ACTIVE = "Active"
    DELAYED = "Delayed"
    COMPLETED = "Completed"
    REJECTED = "Rejected"

class StatusChangeLog(BaseModel):
    lead_id: str
    previous_status: Optional[str]
    new_status: str
    reason: str
    changed_at: datetime
    changed_by_user_id: str
    changed_by_user_name: str
    system_generated: bool = True

class LeadBase(BaseModel):
    client_name: str
    opportunity_name: str
    lead_score: int = 0
    sales_poc: str = ""  # Lead Assignee
    lead_owner: str = ""  # System-controlled lead owner
    next_followup: Optional[str] = None
    lead_source: str = ""
    region: str = ""
    country: str = ""
    industry: str = ""
    contact_person: str = ""
    contact_details: str = ""
    solution: str = ""
    estimated_value: float = 0.0
    currency: str = "USD"
    stage: LeadStage = LeadStage.NEW
    probability: int = 0
    expected_closure_date: Optional[str] = None
    owner: str = ""
    next_action: str = ""
    notes: str = ""
    comments: str = ""

class LeadCreate(LeadBase):
    lead_status: Optional[LeadStatus] = None  # Will be calculated
    status_change_log: Optional[List[StatusChangeLog]] = None

class LeadUpdate(BaseModel):
    client_name: Optional[str] = None
    opportunity_name: Optional[str] = None
    lead_score: Optional[int] = None
    sales_poc: Optional[str] = None
    next_followup: Optional[str] = None
    lead_source: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    industry: Optional[str] = None
    contact_person: Optional[str] = None
    contact_details: Optional[str] = None
    solution: Optional[str] = None
    estimated_value: Optional[float] = None
    currency: Optional[str] = None
    stage: Optional[LeadStage] = None
    probability: Optional[int] = None
    expected_closure_date: Optional[str] = None
    owner: Optional[str] = None
    next_action: Optional[str] = None
    notes: Optional[str] = None
    comments: Optional[str] = None
    # Note: lead_status is NOT included here as it's system-calculated

class Lead(LeadBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    created_at: datetime
    updated_at: datetime
    lead_status: LeadStatus
    status_change_log: List[StatusChangeLog] = []
    task_id: Optional[str] = None
    attachments: List[Dict[str, Any]] = []
