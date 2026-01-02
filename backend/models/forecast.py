from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date

class ForecastBase(BaseModel):
    task_id: str  # Shared Task ID from Opportunity
    opportunity_name: str
    opportunity_id: Optional[str] = None  # Linked Opportunity ID
    deal_value: float  # Deal Value
    probability_percent: int  # Probability %
    forecast_amount: Optional[float] = None  # deal_value * probability / 100
    salesperson: Optional[str] = None  # Assigned Salesperson
    stage: Optional[str] = None  # Current stage
    forecast_month: Optional[str] = None  # YYYY-MM format
    forecast_quarter: Optional[str] = None  # Q1 2025, Q2 2025, etc.
    expected_closure_date: Optional[date] = None
    notes: Optional[str] = None

class ForecastCreate(ForecastBase):
    pass

class ForecastUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    opportunity_name: Optional[str] = None
    deal_value: Optional[float] = None
    probability_percent: Optional[int] = None
    forecast_amount: Optional[float] = None
    salesperson: Optional[str] = None
    stage: Optional[str] = None
    forecast_month: Optional[str] = None
    forecast_quarter: Optional[str] = None
    expected_closure_date: Optional[date] = None
    notes: Optional[str] = None

class Forecast(ForecastBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    task_id: str  # Required
    created_at: datetime
    updated_at: datetime
