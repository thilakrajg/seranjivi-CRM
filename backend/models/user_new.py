from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    SUPER_ADMIN = "Super Admin"
    ADMIN_FOUNDER = "Admin / Founder"
    PRESALES_CONSULTANT = "Presales Consultant"
    PRESALES_LEAD = "Presales Lead"
    PRESALES_MANAGER = "Presales Manager"
    SALES_HEAD = "Sales Head"
    DELIVERY_MANAGER = "Delivery Manager"

class UserStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"

class Region(str, Enum):
    ATLANTIC = "Atlantic"
    ASIA_PACIFIC = "Asia Pacific"
    EUROPE = "Europe"
    NORTH_AMERICA = "North America"
    SOUTH_AMERICA = "South America"
    MIDDLE_EAST = "Middle East"
    AFRICA = "Africa"
    OCEANIA = "Oceania"

class Permission(BaseModel):
    resource: str
    actions: List[str]

class Role(BaseModel):
    name: str
    description: str
    permissions: Dict[str, List[str]]
    
    model_config = ConfigDict(extra="ignore")

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    role: UserRole
    status: UserStatus = UserStatus.ACTIVE
    assigned_regions: List[Region] = []
    temporary_password: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    assigned_regions: Optional[List[Region]] = None

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    full_name: str
    email: EmailStr
    role: UserRole
    status: UserStatus
    assigned_regions: List[Region] = []
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    is_temp_password: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)
