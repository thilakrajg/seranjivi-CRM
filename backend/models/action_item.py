from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date

class ActionItemBase(BaseModel):
    task_id: str  # Shared Task ID (SAL0001)
    task_title: str
    linked_to: Optional[str] = None  # Lead ID, Opportunity ID, or Partner ID
    linked_to_type: Optional[str] = None  # "Lead", "Opportunity", "Partner"
    assigned_to: Optional[str] = None  # User email or name
    due_date: Optional[date] = None
    priority: str = "Medium"  # Low, Medium, High
    status: str = "Not Started"  # Not Started, In Progress, Completed, Overdue
    notes: Optional[str] = None
    completed_date: Optional[datetime] = None

class ActionItemCreate(ActionItemBase):
    pass

class ActionItemUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    task_title: Optional[str] = None
    linked_to: Optional[str] = None
    linked_to_type: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    completed_date: Optional[datetime] = None

class ActionItem(ActionItemBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    task_id: str  # Required
    created_at: datetime
    updated_at: datetime
