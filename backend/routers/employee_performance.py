from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from dateutil import parser

router = APIRouter(prefix="/employees", tags=["employees"])

@router.get("/{user_id}/performance")
async def get_employee_performance(
    user_id: str,
    month: Optional[str] = Query(None, description="Filter by month (YYYY-MM format)"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get performance metrics and proposals for a specific employee
    """
    try:
        # Get employee details
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Build query filter for date range
        date_filter = {}
        if month and month != "all":
            try:
                year, month_num = map(int, month.split('-'))
                start_date = datetime(year, month_num, 1, tzinfo=timezone.utc)
                if month_num == 12:
                    end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
                else:
                    end_date = datetime(year, month_num + 1, 1, tzinfo=timezone.utc)
                date_filter = {
                    "updated_at": {
                        "$gte": start_date.isoformat(),
                        "$lt": end_date.isoformat()
                    }
                }
            except:
                pass
        
        # Get leads owned by this employee
        lead_query = {"owner": user["full_name"]}
        if date_filter:
            lead_query.update(date_filter)
        leads = await db.leads.find(lead_query, {"_id": 0}).to_list(1000)
        
        # Get opportunities owned by this employee
        opp_query = {"sales_owner": user["full_name"]}
        if date_filter:
            opp_query.update(date_filter)
        opportunities = await db.opportunities.find(opp_query, {"_id": 0}).to_list(1000)
        
        # Get SOWs owned by this employee
        sow_query = {"owner": user["full_name"]}
        if date_filter:
            sow_query.update(date_filter)
        sows = await db.sows.find(sow_query, {"_id": 0}).to_list(1000)
        
        # Calculate KPIs
        all_proposals = []
        
        # Process leads
        for lead in leads:
            all_proposals.append({
                "title": lead.get("opportunity_name", "Untitled Lead"),
                "customer": lead.get("client_name", "Unknown"),
                "type": "Lead",
                "status": "Won" if lead.get("stage") == "Won" else "Open" if lead.get("status") == "Active" else "Lost",
                "dealValue": lead.get("estimated_value", 0),
                "updated": lead.get("updated_at", "")[:10] if lead.get("updated_at") else "N/A",
                "stage": lead.get("stage", "Unknown")
            })
        
        # Process opportunities
        for opp in opportunities:
            status = "Won" if opp.get("stage") == "Closed Won" else "Open" if opp.get("status") == "Active" else "Lost"
            all_proposals.append({
                "title": opp.get("opportunity_name", "Untitled Opportunity"),
                "customer": opp.get("client_name", "Unknown"),
                "type": "RFP" if "proposal" in opp.get("opportunity_name", "").lower() else "RFQ",
                "status": status,
                "dealValue": opp.get("estimated_value", 0),
                "updated": opp.get("updated_at", "")[:10] if opp.get("updated_at") else "N/A",
                "stage": opp.get("stage", "Unknown")
            })
        
        # Process SOWs
        for sow in sows:
            status = "Won" if sow.get("status") == "Completed" else "On Hold" if sow.get("status") == "On Hold" else "Open"
            all_proposals.append({
                "title": sow.get("sow_title", "Untitled SOW"),
                "customer": sow.get("client_name", "Unknown"),
                "type": "SOW",
                "status": status,
                "dealValue": sow.get("value", 0),
                "updated": sow.get("updated_at", "")[:10] if sow.get("updated_at") else "N/A",
                "stage": sow.get("status", "Unknown")
            })
        
        # Sort by updated date (most recent first)
        all_proposals.sort(key=lambda x: x["updated"], reverse=True)
        
        # Calculate KPIs
        total_proposals = len(all_proposals)
        proposals_won = len([p for p in all_proposals if p["status"] == "Won"])
        open_proposals = len([p for p in all_proposals if p["status"] == "Open"])
        lost_proposals = len([p for p in all_proposals if p["status"] == "Lost"])
        on_hold_proposals = len([p for p in all_proposals if p["status"] == "On Hold"])
        
        total_deal_value = sum(p["dealValue"] for p in all_proposals if p["dealValue"])
        won_deal_value = sum(p["dealValue"] for p in all_proposals if p["status"] == "Won" and p["dealValue"])
        
        average_deal = round(total_deal_value / total_proposals) if total_proposals > 0 else 0
        win_rate = round((proposals_won / total_proposals) * 100) if total_proposals > 0 else 0
        
        # Format response
        response = {
            "employee": {
                "id": user["id"],
                "full_name": user["full_name"],
                "email": user["email"],
                "role": user["role"]
            },
            "kpis": {
                "totalProposals": total_proposals,
                "proposalsWon": proposals_won,
                "winRate": win_rate,
                "totalDealValue": round(total_deal_value),
                "averageDeal": average_deal,
                "open": open_proposals,
                "lost": lost_proposals,
                "onHold": on_hold_proposals
            },
            "proposals": all_proposals[:50]  # Limit to 50 most recent
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch performance data: {str(e)}")


@router.get("/proposal-counts")
async def get_all_employee_proposal_counts(
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get proposal counts for all employees
    """
    try:
        # Get all users
        users = await db.users.find({}, {"_id": 0}).to_list(1000)
        
        result = []
        for user in users:
            # Count leads
            lead_count = await db.leads.count_documents({"owner": user["full_name"]})
            
            # Count opportunities
            opp_count = await db.opportunities.count_documents({"sales_owner": user["full_name"]})
            
            # Count SOWs
            sow_count = await db.sows.count_documents({"owner": user["full_name"]})
            
            total_count = lead_count + opp_count + sow_count
            
            result.append({
                "id": user["id"],
                "full_name": user["full_name"],
                "email": user["email"],
                "role": user["role"],
                "proposalCount": total_count
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch proposal counts: {str(e)}")
