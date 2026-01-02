from datetime import datetime, timezone
from typing import Dict, Any, Optional
from enum import Enum

class LeadStatus(str, Enum):
    ACTIVE = "Active"
    DELAYED = "Delayed"
    COMPLETED = "Completed"
    REJECTED = "Rejected"

class LeadStage(str, Enum):
    NEW = "New"
    IN_PROGRESS = "In Progress"
    QUALIFIED = "Qualified"
    UNQUALIFIED = "Unqualified"

class StatusChangeReason(str, Enum):
    STAGE_CHANGE = "Stage change"
    DATE_EXCEEDED = "Date exceeded"
    DATE_UPDATED = "Date updated"
    LEAD_CREATED = "Lead created"

def calculate_lead_status(
    stage: str, 
    next_followup_date: Optional[str] = None,
    current_status: Optional[str] = None
) -> tuple[str, str]:
    """
    Calculate lead status based on stage and follow-up date.
    
    Returns:
        tuple: (new_status, reason_for_change)
    """
    # Priority 1: Check for Qualified stage
    if stage == LeadStage.QUALIFIED:
        return LeadStatus.COMPLETED.value, StatusChangeReason.STAGE_CHANGE.value
    
    # Priority 2: Check for Unqualified stage
    if stage == LeadStage.UNQUALIFIED:
        return LeadStatus.REJECTED.value, StatusChangeReason.STAGE_CHANGE.value
    
    # Priority 3: Check for delayed status
    if stage in [LeadStage.NEW, LeadStage.IN_PROGRESS] and next_followup_date:
        try:
            # Parse the followup date
            followup_date = datetime.fromisoformat(next_followup_date.replace('Z', '+00:00'))
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            followup_date_normalized = followup_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if followup_date_normalized < today:
                return LeadStatus.DELAYED.value, StatusChangeReason.DATE_EXCEEDED.value
            else:
                # If followup date is in future and was previously delayed
                if current_status == LeadStatus.DELAYED.value:
                    return LeadStatus.ACTIVE.value, StatusChangeReason.DATE_UPDATED.value
                    
        except (ValueError, AttributeError):
            # If date parsing fails, continue with Active status
            pass
    
    # Default: Active status
    return LeadStatus.ACTIVE.value, StatusChangeReason.STAGE_CHANGE.value

def create_status_change_log(
    lead_id: str,
    previous_status: str,
    new_status: str,
    reason: str,
    user_id: str,
    user_name: str
) -> Dict[str, Any]:
    """Create a status change log entry."""
    return {
        "lead_id": lead_id,
        "previous_status": previous_status,
        "new_status": new_status,
        "reason": reason,
        "changed_at": datetime.now(timezone.utc).isoformat(),
        "changed_by_user_id": user_id,
        "changed_by_user_name": user_name,
        "system_generated": True  # All status changes are system-generated
    }

def get_status_badge_color(status: str) -> str:
    """Get the color for status badge display."""
    colors = {
        LeadStatus.ACTIVE: "bg-blue-100 text-blue-700",
        LeadStatus.DELAYED: "bg-orange-100 text-orange-700",
        LeadStatus.COMPLETED: "bg-green-100 text-green-700",
        LeadStatus.REJECTED: "bg-gray-100 text-gray-700"
    }
    return colors.get(status, "bg-gray-100 text-gray-700")

def get_status_tooltip(status: str, stage: str, next_followup_date: Optional[str] = None) -> str:
    """Generate tooltip text explaining the current status."""
    if status == LeadStatus.ACTIVE:
        return f"Lead is active. Stage: {stage}"
    elif status == LeadStatus.DELAYED:
        return f"Follow-up date ({next_followup_date}) has passed. Follow-up required."
    elif status == LeadStatus.COMPLETED:
        return f"Lead qualified and moved to opportunities. Stage: {stage}"
    elif status == LeadStatus.REJECTED:
        return f"Lead unqualified. Stage: {stage}"
    else:
        return f"Status: {status}, Stage: {stage}"

def validate_status_transition(previous_status: str, new_status: str) -> bool:
    """Validate if a status transition is allowed."""
    # All transitions are allowed since status is system-calculated
    # This function can be used for future validation rules
    return True

def get_status_rules_config() -> Dict[str, Any]:
    """Get the current status rules configuration."""
    return {
        "stage_to_status_mapping": {
            LeadStage.NEW: LeadStatus.ACTIVE,
            LeadStage.IN_PROGRESS: LeadStatus.ACTIVE,
            LeadStage.QUALIFIED: LeadStatus.COMPLETED,
            LeadStage.UNQUALIFIED: LeadStatus.REJECTED
        },
        "delay_check_stages": [LeadStage.NEW, LeadStage.IN_PROGRESS],
        "status_values": [status.value for status in LeadStatus],
        "stage_values": [stage.value for stage in LeadStage],
        "priority_rules": [
            "Qualified → Completed",
            "Unqualified → Rejected", 
            "Date exceeded → Delayed",
            "Default → Active"
        ]
    }
