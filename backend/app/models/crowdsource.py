from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CrowdsourceReport(BaseModel):
    location: str
    intensity: str
    description: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None  # Optional if we allow anonymous reports
    status: str = "pending" # pending, verified, rejected

    class Config:
        schema_extra = {
            "example": {
                "location": "Mumbai, India",
                "intensity": "heavy",
                "description": "Flooding in the streets",
                "timestamp": "2023-10-27T10:00:00",
                "status": "pending"
            }
        }
