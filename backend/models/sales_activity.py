from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class SalesActivityBase(BaseModel):
    task_id: str  # Shared Task ID (SAL0001)
    activity_type: str  # Call, Meeting, Email
    activity_owner: Optional[str] = None  # User who logged the activity
    activity_date: Optional[datetime] = None
    linked_account: Optional[str] = None  # Client/Account name
    linked_lead: Optional[str] = None  # Lead ID
    linked_opportunity: Optional[str] = None  # Opportunity ID
    summary: Optional[str] = None  # Activity summary
    outcome: Optional[str] = None  # Outcome of activity
    next_step: Optional[str] = None  # Next step planned

class SalesActivityCreate(SalesActivityBase):
    pass

class SalesActivityUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    activity_type: Optional[str] = None
    activity_owner: Optional[str] = None
    activity_date: Optional[datetime] = None
    linked_account: Optional[str] = None
    linked_lead: Optional[str] = None
    linked_opportunity: Optional[str] = None
    summary: Optional[str] = None
    outcome: Optional[str] = None
    next_step: Optional[str] = None

class SalesActivity(SalesActivityBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    task_id: str  # Required
    created_at: datetime
    updated_at: datetime
