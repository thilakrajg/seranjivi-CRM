from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid
from typing import List
from models.forecast import ForecastCreate, Forecast, ForecastUpdate
from database import get_db
from utils.middleware import get_current_user

router = APIRouter(prefix="/forecasts", tags=["Forecasts"])

@router.get("", response_model=List[Forecast])
async def get_forecasts(current_user: dict = Depends(get_current_user)):
    db = get_db()
    forecasts = await db.forecasts.find({}, {"_id": 0}).to_list(1000)
    return forecasts

@router.get("/{forecast_id}", response_model=Forecast)
async def get_forecast(forecast_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    forecast = await db.forecasts.find_one({"id": forecast_id}, {"_id": 0})
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return forecast

@router.post("", response_model=Forecast, status_code=status.HTTP_201_CREATED)
async def create_forecast(forecast_data: ForecastCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    forecast_dict = forecast_data.model_dump()
    
    # Auto-calculate forecast amount if not provided
    if not forecast_dict.get("forecast_amount"):
        deal_value = forecast_dict.get("deal_value", 0)
        probability = forecast_dict.get("probability_percent", 0)
        forecast_dict["forecast_amount"] = round((deal_value * probability) / 100, 2)
    
    if "expected_closure_date" in forecast_dict and forecast_dict["expected_closure_date"]:
        forecast_dict["expected_closure_date"] = forecast_dict["expected_closure_date"].isoformat()
    
    forecast_dict["id"] = str(uuid.uuid4())
    forecast_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    forecast_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.forecasts.insert_one(forecast_dict)
    return forecast_dict

@router.put("/{forecast_id}", response_model=Forecast)
async def update_forecast(forecast_id: str, forecast_data: ForecastUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    forecast = await db.forecasts.find_one({"id": forecast_id})
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    
    update_data = forecast_data.model_dump(exclude_unset=True)
    
    # Recalculate forecast amount if deal_value or probability changed
    if "deal_value" in update_data or "probability_percent" in update_data:
        deal_value = update_data.get("deal_value", forecast.get("deal_value", 0))
        probability = update_data.get("probability_percent", forecast.get("probability_percent", 0))
        update_data["forecast_amount"] = round((deal_value * probability) / 100, 2)
    
    if "expected_closure_date" in update_data and update_data["expected_closure_date"]:
        update_data["expected_closure_date"] = update_data["expected_closure_date"].isoformat()
    
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.forecasts.update_one({"id": forecast_id}, {"$set": update_data})
    updated_forecast = await db.forecasts.find_one({"id": forecast_id}, {"_id": 0})
    return updated_forecast

@router.delete("/{forecast_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_forecast(forecast_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    result = await db.forecasts.delete_one({"id": forecast_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return None
