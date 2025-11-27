# backend/app/api/warnings.py
from fastapi import APIRouter, Depends, HTTPException
from app.database import sync_warnings_collection
from app.schemas.prediction import Warning as WarningSchema
from datetime import datetime, timedelta
from typing import List

router = APIRouter()

@router.get("/active", response_model=List[WarningSchema])
async def get_active_warnings():
    """
    Retrieves all active heavy rainfall warnings.
    """
    # Define an expiry window for warnings (e.g., 60 minutes after predicted_timestamp)
    # This means a warning is active if its predicted_timestamp + forecast_time is in the near future
    # or it's recently passed but hasn't been explicitly marked inactive.

    # A simple check: active if it was issued within the last, say, 2 hours
    # and its predicted end time hasn't passed too long ago (e.g., 30 mins)
    # For a more robust system, warnings would be explicitly expired by a background task.

    active_warnings = list(sync_warnings_collection.find({
        "is_active": True,
        "issued_at": {"$gte": datetime.utcnow() - timedelta(hours=2)}  # Issued recently
    }).sort("issued_at", -1))

    # Convert ObjectIds to strings for JSON serialization
    for warning in active_warnings:
        warning["id"] = str(warning["_id"])

    return active_warnings