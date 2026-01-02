"""
Task ID Generator Utility
Generates unique sequential Task IDs in format: SAL0001, SAL0002, etc.
Task IDs are shared across Leads → Opportunities → Action Items → Activities → Forecasts
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

async def generate_task_id(db: AsyncIOMotorDatabase) -> str:
    """
    Generate next sequential Task ID in format SAL0001
    Uses a counter collection to maintain sequence
    """
    # Get or create counter document
    counter_collection = db.counters
    
    result = await counter_collection.find_one_and_update(
        {"_id": "task_id"},
        {"$inc": {"sequence": 1}},
        upsert=True,
        return_document=True
    )
    
    # Format as SAL + 4 digits (padded with zeros)
    sequence_number = result.get("sequence", 1)
    task_id = f"SAL{sequence_number:04d}"
    
    return task_id

async def get_current_task_id_sequence(db: AsyncIOMotorDatabase) -> int:
    """
    Get current Task ID sequence number
    """
    counter = await db.counters.find_one({"_id": "task_id"})
    if counter:
        return counter.get("sequence", 0)
    return 0

async def initialize_task_id_counter(db: AsyncIOMotorDatabase, start_value: int = 0):
    """
    Initialize or reset the Task ID counter
    """
    await db.counters.update_one(
        {"_id": "task_id"},
        {"$set": {"sequence": start_value}},
        upsert=True
    )
