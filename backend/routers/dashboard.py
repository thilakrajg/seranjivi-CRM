from fastapi import APIRouter, HTTPException, status, Depends
from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Dict, List, Any
from utils.middleware import get_current_user
from database import get_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])





@router.get("/analytics")
async def get_dashboard_analytics(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    db = get_db()
    # Get counts
    total_clients = await db.clients.count_documents({})
    total_vendors = await db.vendors.count_documents({})
    total_leads = await db.leads.count_documents({})
    total_opportunities = await db.opportunities.count_documents({})
    total_sows = await db.sows.count_documents({})
    total_activities = await db.activities.count_documents({})
    
    # Lead metrics
    active_leads = await db.leads.count_documents({"status": "Active"})
    won_leads = await db.leads.count_documents({"stage": "Won"})
    lost_leads = await db.leads.count_documents({"stage": "Lost"})
    
    # Opportunity metrics
    active_opportunities = await db.opportunities.count_documents({"status": "Active"})
    closed_won = await db.opportunities.count_documents({"stage": "Closed Won"})
    
    # Calculate total pipeline value
    opportunities_list = await db.opportunities.find({"status": "Active"}, {"_id": 0, "estimated_value": 1}).to_list(1000)
    total_pipeline_value = sum([opp.get("estimated_value", 0) for opp in opportunities_list])
    
    # Calculate total SOW value
    sows_list = await db.sows.find({}, {"_id": 0, "value": 1}).to_list(1000)
    total_sow_value = sum([sow.get("value", 0) for sow in sows_list])
    
    # Opportunities by stage
    all_opportunities = await db.opportunities.find({}, {"_id": 0, "stage": 1}).to_list(1000)
    stage_counts = {}
    for opp in all_opportunities:
        stage = opp.get("stage", "Unknown")
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
    
    # Leads by source
    all_leads = await db.leads.find({}, {"_id": 0, "lead_source": 1}).to_list(1000)
    source_counts = {}
    for lead in all_leads:
        source = lead.get("lead_source", "Unknown")
        source_counts[source] = source_counts.get(source, 0) + 1
    
    # Recent activities
    pending_activities = await db.activities.count_documents({"status": "Pending"})
    completed_activities = await db.activities.count_documents({"status": "Completed"})
    
    # Win rate calculation
    total_closed_leads = won_leads + lost_leads
    win_rate = round((won_leads / total_closed_leads * 100), 2) if total_closed_leads > 0 else 0
    
    # Action Items metrics
    total_action_items = await db.action_items.count_documents({})
    pending_action_items = await db.action_items.count_documents({"status": {"$in": ["Not Started", "In Progress"]}})
    completed_action_items = await db.action_items.count_documents({"status": "Completed"})
    overdue_action_items = await db.action_items.count_documents({"status": "Overdue"})
    
    # Sales Activities metrics
    total_sales_activities = await db.sales_activities.count_documents({})
    sales_activities_by_type = {}
    activities = await db.sales_activities.find({}, {"_id": 0, "activity_type": 1}).to_list(1000)
    for activity in activities:
        act_type = activity.get("activity_type", "Other")
        sales_activities_by_type[act_type] = sales_activities_by_type.get(act_type, 0) + 1
    
    # Forecast metrics
    forecasts = await db.forecasts.find({}, {"_id": 0, "forecast_amount": 1, "deal_value": 1, "probability_percent": 1}).to_list(1000)
    total_forecast_amount = sum([f.get("forecast_amount", 0) for f in forecasts])
    total_deal_value = sum([f.get("deal_value", 0) for f in forecasts])
    avg_win_probability = round(sum([f.get("probability_percent", 0) for f in forecasts]) / len(forecasts), 2) if forecasts else 0
    
    # Partners metrics
    total_partners = await db.partners.count_documents({})
    
    return {
        "overview": {
            "total_clients": total_clients,
            "total_vendors": total_vendors,
            "total_leads": total_leads,
            "total_opportunities": total_opportunities,
            "total_sows": total_sows,
            "total_activities": total_activities
        },
        "pipeline": {
            "total_pipeline_value": total_pipeline_value,
            "active_opportunities": active_opportunities,
            "opportunities_by_stage": stage_counts
        },
        "sales_performance": {
            "total_sow_value": total_sow_value,
            "closed_won": closed_won,
            "win_rate": win_rate
        },
        "leads": {
            "active_leads": active_leads,
            "won_leads": won_leads,
            "lost_leads": lost_leads,
            "leads_by_source": source_counts,
            "conversion_rate": round((won_leads / total_leads * 100), 2) if total_leads > 0 else 0
        },
        "activities": {
            "pending_activities": pending_activities,
            "completed_activities": completed_activities
        },
        "sow_tracking": {
            "active_sows": await db.sows.count_documents({"status": "Active"}),
            "completed_sows": await db.sows.count_documents({"status": "Completed"}),
            "total_sow_value": total_sow_value
        },
        "action_items": {
            "total": total_action_items,
            "pending": pending_action_items,
            "completed": completed_action_items,
            "overdue": overdue_action_items
        },
        "sales_activities": {
            "total": total_sales_activities,
            "by_type": sales_activities_by_type
        },
        "forecasts": {
            "total_forecast_amount": total_forecast_amount,
            "total_deal_value": total_deal_value,
            "avg_win_probability": avg_win_probability,
            "total_forecasts": len(forecasts)
        },
        "partners": {
            "total_partners": total_partners
        }
    }