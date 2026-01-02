from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class SettingBase(BaseModel):
    setting_type: str  # stage, region, industry, lead_source, currency
    values: List[str] = []

class SettingCreate(SettingBase):
    pass

class SettingUpdate(BaseModel):
    values: Optional[List[str]] = None

class Setting(SettingBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    created_at: datetime
    updated_at: datetime