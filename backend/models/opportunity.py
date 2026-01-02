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

class OpportunityBase(BaseModel):
    # Core Fields
    client_name: str  # Customer/Account
    opportunity_name: str
    
    # New Required Fields
    task_id: Optional[str] = None  # Shared Task ID from Lead (SAL0001)
    deal_value: Optional[float] = 0  # Alias for estimated_value
    probability_percent: Optional[int] = 0  # Probability %
    win_loss_reason: Optional[str] = None  # Win/Loss Reason
    last_interaction: Optional[Union[datetime, date, str]] = None  # Last Interaction date
    next_action: Optional[str] = None  # Next Action
    partner_org: Optional[str] = None  # Partner Organization
    partner_org_contact: Optional[str] = None  # Partner Organization Contact
    
    @field_validator('last_interaction', mode='before')
    @classmethod
    def parse_last_interaction(cls, v):
        if not v or v == '':
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
    
    # Existing Fields (KEEP ALL)
    industry: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    solution: Optional[str] = None
    estimated_value: Optional[float] = 0
    currency: str = "USD"
    probability: Optional[int] = 0
    stage: str = "Prospecting"  # Prospecting, Needs Analysis, Proposal, Negotiation, Closed
    expected_closure_date: Optional[Union[date, str]] = None
    
    @field_validator('expected_closure_date', mode='before')
    @classmethod
    def parse_expected_closure_date(cls, v):
        if not v or v == '':
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            if len(v) == 10:
                return datetime.strptime(v, '%Y-%m-%d').date()
        return v
    sales_owner: Optional[str] = None  # Assigned Salesperson
    technical_poc: Optional[str] = None
    presales_poc: Optional[str] = None
    key_stakeholders: Optional[str] = None
    competitors: Optional[str] = None
    next_steps: Optional[str] = None
    risks: Optional[str] = None
    status: str = "Active"  # Active, Completed, Lost
    attachments: Optional[List[AttachmentMetadata]] = []

class OpportunityCreate(OpportunityBase):
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
            # Handle date string "2025-12-25"
            if 'T' not in v and len(v) == 10:
                return datetime.strptime(v, '%Y-%m-%d')
            # Handle datetime string
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v

class OpportunityUpdate(BaseModel):
    client_name: Optional[str] = None
    opportunity_name: Optional[str] = None
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
            # Handle date string "2025-12-25"
            if 'T' not in v and len(v) == 10:
                return datetime.strptime(v, '%Y-%m-%d')
            # Handle datetime string
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v
    industry: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    solution: Optional[str] = None
    estimated_value: Optional[float] = None
    currency: Optional[str] = None
    probability: Optional[int] = None
    stage: Optional[str] = None
    expected_closure_date: Optional[date] = None
    sales_owner: Optional[str] = None
    technical_poc: Optional[str] = None
    presales_poc: Optional[str] = None
    key_stakeholders: Optional[str] = None
    competitors: Optional[str] = None
    next_steps: Optional[str] = None
    risks: Optional[str] = None
    status: Optional[str] = None
    partner_org: Optional[str] = None
    partner_org_contact: Optional[str] = None

class Opportunity(OpportunityBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    task_id: str  # Required - shared from Lead
    linked_lead_id: Optional[str] = None
    linked_sow_id: Optional[str] = None
    attachments: List[AttachmentMetadata] = []
    created_at: datetime
    updated_at: datetime