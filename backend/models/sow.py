from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Union
from datetime import datetime, date

class AttachmentMetadata(BaseModel):
    id: str
    name: str
    originalName: str
    storedName: str
    size: int
    type: str
    path: str
    url: str
    uploadedAt: str

class SOWBase(BaseModel):
    client_name: str
    project_name: str
    sow_title: str
    sow_type: str = "New"  # New, Renewal, CO
    start_date: Optional[Union[date, str]] = None
    end_date: Optional[Union[date, str]] = None
    
    @field_validator('start_date', 'end_date', mode='before')
    @classmethod
    def parse_dates(cls, v):
        if not v or v == '':
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str) and len(v) == 10:
            return datetime.strptime(v, '%Y-%m-%d').date()
        return v
    value: Optional[float] = 0
    currency: str = "USD"
    billing_type: Optional[str] = None  # Fixed, T&M, Milestone
    status: str = "Active"  # Active, Completed, On Hold
    attachments: Optional[List[AttachmentMetadata]] = []
    owner: Optional[str] = None
    delivery_spoc: Optional[str] = None
    milestones: Optional[str] = None
    po_number: Optional[str] = None
    invoice_plan: Optional[str] = None
    documents_link: Optional[str] = None
    notes: Optional[str] = None

class SOWCreate(SOWBase):
    created_at: Optional[Union[datetime, date, str]] = None  # Allow custom creation date
    
    @field_validator('created_at', mode='before')
    @classmethod
    def parse_created_at(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, date):
            return datetime.combine(v, datetime.min.time())
        if isinstance(v, str):
            if 'T' not in v and len(v) == 10:
                return datetime.strptime(v, '%Y-%m-%d')
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v

class SOWUpdate(BaseModel):
    client_name: Optional[str] = None
    project_name: Optional[str] = None
    created_at: Optional[Union[datetime, date, str]] = None  # Allow updating creation date
    
    @field_validator('created_at', mode='before')
    @classmethod
    def parse_created_at(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, date):
            return datetime.combine(v, datetime.min.time())
        if isinstance(v, str):
            if 'T' not in v and len(v) == 10:
                return datetime.strptime(v, '%Y-%m-%d')
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v
    sow_title: Optional[str] = None
    sow_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    value: Optional[float] = None
    currency: Optional[str] = None
    billing_type: Optional[str] = None
    status: Optional[str] = None
    owner: Optional[str] = None
    delivery_spoc: Optional[str] = None
    milestones: Optional[str] = None
    po_number: Optional[str] = None
    invoice_plan: Optional[str] = None
    documents_link: Optional[str] = None
    notes: Optional[str] = None

class SOW(SOWBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    attachments: List[AttachmentMetadata] = []
    linked_opportunity_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime