from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime

class PartnerContactBase(BaseModel):
    name: str
    title: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_primary: bool = False

class PartnerBase(BaseModel):
    name: str
    partner_type: Optional[str] = "Vendor"  # Channel, Tech, Vendor
    category: Optional[str] = None
    region: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    status: str = "Active"  # Active, Inactive
    interaction_history: Optional[str] = None  # Notes on partner interactions
    notes: Optional[str] = None

class PartnerCreate(PartnerBase):
    contacts: Optional[List[PartnerContactBase]] = []

class PartnerUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    region: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    contacts: Optional[List[PartnerContactBase]] = None

class Partner(PartnerBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    contacts: List[PartnerContactBase] = []
    created_at: datetime
    updated_at: datetime