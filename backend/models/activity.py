from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ActivityBase(BaseModel):
    activity_type: str = "Call"  # Call, Meeting, Email, Demo, Follow-up
    title: str
    description: Optional[str] = None
    related_to: Optional[str] = None  # Lead, Opportunity, SOW, Client
    related_id: Optional[str] = None
    assigned_to: Optional[str] = None
    status: str = "Pending"  # Pending, Completed, Cancelled
    due_date: Optional[datetime] = None
    notes: Optional[str] = None

class ActivityCreate(ActivityBase):
    pass

class ActivityUpdate(BaseModel):
    activity_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    related_to: Optional[str] = None
    related_id: Optional[str] = None
    assigned_to: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None

class Activity(ActivityBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    created_at: datetime
    updated_at: datetime