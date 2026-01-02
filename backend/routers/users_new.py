from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
import uuid
import json
from typing import List, Dict, Any
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from models.user_new import UserCreate, User, UserUpdate, UserLogin, TokenResponse, PasswordChange, UserRole, UserStatus
from database import get_db
from utils.auth import get_password_hash, verify_password, create_access_token
from utils.middleware import get_current_user
from utils.email import send_email

router = APIRouter(prefix="/users", tags=["User Management"])

# Load roles configuration
def load_roles_config():
    try:
        with open('roles_config.json', 'r') as f:
                return json.load(f)
    except FileNotFoundError:
        # Fallback roles if config file not found
        return {
            "Super Admin": {
                "permissions": {
                    "users": ["create", "read", "update", "delete"],
                    "leads": ["create", "read", "update", "delete"],
                    "opportunities": ["create", "read", "update", "delete"],
                    "action_items": ["create", "read", "update", "delete"],
                    "contacts": ["create", "read", "update", "delete"],
                    "sales_activity": ["create", "read", "update", "delete"]
                }
            }
        }

ROLES_CONFIG = load_roles_config()

@router.get("", response_model=List[User])
async def get_users(current_user: dict = Depends(get_current_user)):
    """Get all users with ABAC filtering applied"""
    db = get_db()
    
    # Apply ABAC filtering based on current user's role and regions
    query = {}
    
    # Region-based filtering (ABAC)
    if current_user["role"] != UserRole.SUPER_ADMIN:
        # Non-super admins can only see users in their assigned regions
        if current_user.get("assigned_regions"):
            query["assigned_regions"] = {"$in": current_user["assigned_regions"]}
    
    users = await db.users.find(query, {"_id": 0, "password": 0}).to_list(1000)
    return users

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific user with ABAC filtering"""
    db = get_db()
    
    query = {"id": user_id}
    
    # Apply ABAC filtering
    if current_user["role"] != UserRole.SUPER_ADMIN:
        # Region-based filtering
        if current_user.get("assigned_regions"):
            query["assigned_regions"] = {"$in": current_user["assigned_regions"]}
    
    user = await db.users.find_one(query, {"_id": 0, "password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate, 
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Create new user with email invitation"""
    db = get_db()
    
    # Check if user has permission to create users
    user_role_config = ROLES_CONFIG.get(current_user["role"], {})
    user_permissions = user_role_config.get("permissions", {})
    
    if "users" not in user_permissions or "create" not in user_permissions["users"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to create users")
    
    # Check if email already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate temporary password
    temp_password = "ss@123"
    
    # Create user document
    user_dict = user_data.model_dump()
    user_dict["id"] = str(uuid.uuid4())
    user_dict["password"] = get_password_hash(temp_password)
    user_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    user_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    user_dict["is_temp_password"] = True
    user_dict["password_changed_at"] = None
    user_dict["last_login"] = None
    
    await db.users.insert_one(user_dict)
    
    # Send invitation email in background
    background_tasks.add_task(
        send_user_invitation_email,
        user_data.email,
        user_data.full_name,
        temp_password
    )
    
    # Remove password from response
    user_dict.pop("password")
    return user_dict

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str, 
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user with permission checks"""
    db = get_db()
    
    # Check permissions
    user_role_config = ROLES_CONFIG.get(current_user["role"], {})
    user_permissions = user_role_config.get("permissions", {})
    
    if "users" not in user_permissions or "update" not in user_permissions["users"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to update users")
    
    # Find existing user
    existing_user = await db.users.find_one({"id": user_id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Apply ABAC filtering for updates
    if current_user["role"] != UserRole.SUPER_ADMIN:
        # Region-based filtering
        if current_user.get("assigned_regions"):
            user_regions = existing_user.get("assigned_regions", [])
            if not any(region in current_user["assigned_regions"] for region in user_regions):
                raise HTTPException(status_code=403, detail="Cannot update user outside your regions")
    
    # Prepare update data
    update_dict = {k: v for k, v in user_data.model_dump().items() if v is not None}
    if update_dict:
        update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.users.update_one({"id": user_id}, {"$set": update_dict})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return updated user
    updated_user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Delete user with permission checks"""
    db = get_db()
    
    # Check permissions
    user_role_config = ROLES_CONFIG.get(current_user["role"], {})
    user_permissions = user_role_config.get("permissions", {})
    
    if "users" not in user_permissions or "delete" not in user_permissions["users"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to delete users")
    
    # Apply ABAC filtering
    if current_user["role"] != UserRole.SUPER_ADMIN:
        existing_user = await db.users.find_one({"id": user_id})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Region-based filtering
        if current_user.get("assigned_regions"):
            user_regions = existing_user.get("assigned_regions", [])
            if not any(region in current_user["assigned_regions"] for region in user_regions):
                raise HTTPException(status_code=403, detail="Cannot delete user outside your regions")
    
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

@router.post("/{user_id}/activate")
async def activate_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Activate user"""
    return await toggle_user_status(user_id, UserStatus.ACTIVE, current_user)

@router.post("/{user_id}/deactivate")
async def deactivate_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Deactivate user"""
    return await toggle_user_status(user_id, UserStatus.INACTIVE, current_user)

async def toggle_user_status(user_id: str, status: UserStatus, current_user: dict):
    """Helper function to toggle user status"""
    db = get_db()
    
    # Check permissions
    user_role_config = ROLES_CONFIG.get(current_user["role"], {})
    user_permissions = user_role_config.get("permissions", {})
    
    if "users" not in user_permissions or "update" not in user_permissions["users"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to update user status")
    
    # Apply ABAC filtering
    if current_user["role"] != UserRole.SUPER_ADMIN:
        existing_user = await db.users.find_one({"id": user_id})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Region-based filtering
        if current_user.get("assigned_regions"):
            user_regions = existing_user.get("assigned_regions", [])
            if not any(region in current_user["assigned_regions"] for region in user_regions):
                raise HTTPException(status_code=403, detail="Cannot modify user outside your regions")
    
    result = await db.users.update_one(
        {"id": user_id}, 
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"User {status.value}d successfully"}

@router.get("/roles/config")
async def get_roles_config(current_user: dict = Depends(get_current_user)):
    """Get roles and permissions configuration"""
    # Only Super Admin and Admin/Founder can view roles config
    if current_user["role"] not in [UserRole.SUPER_ADMIN, UserRole.ADMIN_FOUNDER]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to view roles configuration")
    
    return ROLES_CONFIG

async def send_user_invitation_email(email: str, full_name: str, temp_password: str):
    """Send invitation email to new user"""
    try:
        # This is a placeholder - implement actual email sending logic
        subject = "Welcome to Sales CRM - Your Account Details"
        
        body = f"""
        Dear {full_name},
        
        Your account has been created in the Sales CRM system.
        
        Login URL: http://localhost:3000/login
        Username: {email}
        Temporary Password: {temp_password}
        
        You will be required to change your password upon first login.
        
        Best regards,
        Sales CRM Team
        """
        
        # TODO: Implement actual email sending with your SMTP configuration
        print(f"Email would be sent to {email}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        
    except Exception as e:
        print(f"Failed to send invitation email: {str(e)}")
