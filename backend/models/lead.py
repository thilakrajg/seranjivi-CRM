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

class LeadBase(BaseModel):
    # Core Fields
    client_name: str
    opportunity_name: str
    
    # New Required Fields
    task_id: Optional[str] = None  # SAL0001 format - auto-generated
    lead_score: Optional[int] = 0  # 0-100 score
    sales_poc: Optional[str] = None  # Sales Point of Contact / Lead Owner
    next_followup: Optional[Union[date, str]] = None  # Next follow-up date
    
    # Contact Information
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    
    # Location and Classification
    industry: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    
    # Sales Information
    lead_source: Optional[str] = None
    solution: Optional[str] = None
    estimated_value: Optional[float] = 0
    currency: str = "USD"
    
    # Status and Stage
    lead_status: str = "New"  # New, Qualified, Dormant, Lost
    sales_stage: str = "Qualification"  # Qualification, Proposal, Negotiation, Closed Won, Closed Lost
    probability: Optional[int] = 0  # Auto-calculated based on sales_stage
    expected_closure_date: Optional[Union[date, str]] = None
    
    # Action and Notes
    next_action: Optional[str] = None
    sales_notes: Optional[str] = None  # Renamed from notes
    comments: Optional[str] = None
    
    # Metadata
    tracker: str = "Lead"  # Lead, Opportunity, Action Items
    last_updated: Optional[datetime] = None

    # Date validators
    @field_validator('next_followup', 'expected_closure_date', mode='before')
    @classmethod
    def parse_dates(cls, v):
        if not v or v == '':
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str) and len(v) == 10:
            return datetime.strptime(v, '%Y-%m-%d').date()
        return v
    
    # Auto-calculate probability based on sales stage
    @field_validator('probability', mode='before')
    @classmethod
    def calculate_probability(cls, v, info):
        if 'sales_stage' in info.data and info.data['sales_stage']:
            stage_probability_map = {
                'Qualification': 25,
                'Proposal': 50,
                'Negotiation': 75,
                'Closed Won': 100,
                'Closed Lost': 0
            }
            return stage_probability_map.get(info.data['sales_stage'], 0)
        return v

class LeadCreate(LeadBase):
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

class LeadUpdate(BaseModel):
    client_name: Optional[str] = None
    opportunity_name: Optional[str] = None
    lead_score: Optional[int] = None
    sales_poc: Optional[str] = None
    next_followup: Optional[date] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    lead_source: Optional[str] = None
    solution: Optional[str] = None
    estimated_value: Optional[float] = None
    currency: Optional[str] = None
    lead_status: Optional[str] = None
    sales_stage: Optional[str] = None
    probability: Optional[int] = None
    expected_closure_date: Optional[date] = None
    next_action: Optional[str] = None
    sales_notes: Optional[str] = None
    comments: Optional[str] = None
    tracker: Optional[str] = None

class Lead(LeadBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    task_id: str  # Required for existing records
    linked_opportunity_id: Optional[str] = None
    attachments: List[AttachmentMetadata] = []
    last_activity_date: Optional[datetime] = None  # Track last activity
    created_at: datetime
    updated_at: datetime