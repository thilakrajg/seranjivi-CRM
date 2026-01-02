from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any
import os
from datetime import datetime
from database import get_db

router = APIRouter(prefix="/master", tags=["master"])

@router.get("/regions", response_model=List[Dict[str, Any]])
async def get_regions(db = Depends(get_db)):
    """Get all regions from master data"""
    try:
        regions_setting = await db.settings.find_one({"setting_type": "regions"}, {"_id": 0})
        
        if regions_setting and regions_setting.get("data"):
            return regions_setting["data"]
        
        # Fallback regions if no data exists
        fallback_regions = [
            {"id": "1", "name": "North America"},
            {"id": "2", "name": "Europe"},
            {"id": "3", "name": "Asia Pacific"},
            {"id": "4", "name": "Latin America"},
            {"id": "5", "name": "Middle East"},
            {"id": "6", "name": "Africa"}
        ]
        
        # Insert fallback regions as master data
        await db.settings.update_one(
            {"setting_type": "regions"},
            {
                "$set": {
                    "setting_type": "regions",
                    "data": fallback_regions,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return fallback_regions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching regions: {str(e)}")

@router.get("/countries", response_model=List[Dict[str, Any]])
async def get_countries(db = Depends(get_db)):
    """Get all countries from master data"""
    try:
        countries_setting = await db.settings.find_one({"setting_type": "countries"}, {"_id": 0})
        
        if countries_setting and countries_setting.get("data"):
            return countries_setting["data"]
        
        # Fallback countries if no data exists
        fallback_countries = [
            # North America
            {"id": "1", "name": "United States", "region": "North America"},
            {"id": "2", "name": "Canada", "region": "North America"},
            {"id": "3", "name": "Mexico", "region": "North America"},
            
            # Europe
            {"id": "4", "name": "Germany", "region": "Europe"},
            {"id": "5", "name": "France", "region": "Europe"},
            {"id": "6", "name": "United Kingdom", "region": "Europe"},
            {"id": "7", "name": "Italy", "region": "Europe"},
            {"id": "8", "name": "Spain", "region": "Europe"},
            {"id": "9", "name": "Netherlands", "region": "Europe"},
            {"id": "10", "name": "Sweden", "region": "Europe"},
            {"id": "11", "name": "Norway", "region": "Europe"},
            {"id": "12", "name": "Denmark", "region": "Europe"},
            {"id": "13", "name": "Poland", "region": "Europe"},
            
            # Asia Pacific
            {"id": "14", "name": "Singapore", "region": "Asia Pacific"},
            {"id": "15", "name": "Japan", "region": "Asia Pacific"},
            {"id": "16", "name": "China", "region": "Asia Pacific"},
            {"id": "17", "name": "India", "region": "Asia Pacific"},
            {"id": "18", "name": "Australia", "region": "Asia Pacific"},
            {"id": "19", "name": "South Korea", "region": "Asia Pacific"},
            {"id": "20", "name": "Malaysia", "region": "Asia Pacific"},
            {"id": "21", "name": "Thailand", "region": "Asia Pacific"},
            {"id": "22", "name": "Indonesia", "region": "Asia Pacific"},
            {"id": "23", "name": "Philippines", "region": "Asia Pacific"},
            
            # Latin America
            {"id": "24", "name": "Brazil", "region": "Latin America"},
            {"id": "25", "name": "Argentina", "region": "Latin America"},
            {"id": "26", "name": "Chile", "region": "Latin America"},
            {"id": "27", "name": "Colombia", "region": "Latin America"},
            {"id": "28", "name": "Peru", "region": "Latin America"},
            {"id": "29", "name": "Venezuela", "region": "Latin America"},
            
            # Middle East
            {"id": "30", "name": "United Arab Emirates", "region": "Middle East"},
            {"id": "31", "name": "Saudi Arabia", "region": "Middle East"},
            {"id": "32", "name": "Israel", "region": "Middle East"},
            {"id": "33", "name": "Qatar", "region": "Middle East"},
            {"id": "34", "name": "Kuwait", "region": "Middle East"},
            {"id": "35", "name": "Oman", "region": "Middle East"},
            
            # Africa
            {"id": "36", "name": "South Africa", "region": "Africa"},
            {"id": "37", "name": "Egypt", "region": "Africa"},
            {"id": "38", "name": "Nigeria", "region": "Africa"},
            {"id": "39", "name": "Kenya", "region": "Africa"},
            {"id": "40", "name": "Morocco", "region": "Africa"},
            {"id": "41", "name": "Ghana", "region": "Africa"}
        ]
        
        # Insert fallback countries as master data
        await db.settings.update_one(
            {"setting_type": "countries"},
            {
                "$set": {
                    "setting_type": "countries",
                    "data": fallback_countries,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return fallback_countries
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching countries: {str(e)}")

@router.get("/countries/by-region/{region_name}", response_model=List[Dict[str, Any]])
async def get_countries_by_region(region_name: str, db = Depends(get_db)):
    """Get countries filtered by region"""
    try:
        countries = await get_countries(db)
        filtered_countries = [country for country in countries if country.get("region") == region_name]
        return filtered_countries
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching countries by region: {str(e)}")

@router.post("/regions", response_model=Dict[str, Any])
async def create_or_update_regions(regions: List[Dict[str, Any]], db = Depends(get_db)):
    """Create or update regions master data"""
    try:
        await db.settings.update_one(
            {"setting_type": "regions"},
            {
                "$set": {
                    "setting_type": "regions",
                    "data": regions,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return {"message": "Regions updated successfully", "count": len(regions)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating regions: {str(e)}")

@router.post("/countries", response_model=Dict[str, Any])
async def create_or_update_countries(countries: List[Dict[str, Any]], db = Depends(get_db)):
    """Create or update countries master data"""
    try:
        await db.settings.update_one(
            {"setting_type": "countries"},
            {
                "$set": {
                    "setting_type": "countries",
                    "data": countries,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return {"message": "Countries updated successfully", "count": len(countries)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating countries: {str(e)}")
