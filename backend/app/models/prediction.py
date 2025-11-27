# backend/app/models/prediction.py

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Any, Dict
from bson import ObjectId
from .common import PyObjectId

# Unified Prediction model matching LLD
class Prediction(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    model_id: Optional[PyObjectId] = None # Link to ModelMetadata
    storm_cell_id: Optional[PyObjectId] = None # Link to StormCell
    
    # LLD fields
    predicted_mean_rain_rate: float
    predicted_top_10_rain_rate: float
    predicted_location: Optional[Dict[str, Any]] = None # JSON/GeoJSON
    is_warning: bool = False
    generated_by_user_id: Optional[PyObjectId] = None # Link to User
    
    # Extra fields from previous implementation that might be useful
    timestamp: datetime = Field(default_factory=datetime.utcnow) # created_at
    forecast_time: int # 30 or 60

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "model_id": "60c72b2f9b1d8e001f8e4a3c",
                "storm_cell_id": "60c72b2f9b1d8e001f8e4a3d",
                "predicted_mean_rain_rate": 5.5,
                "predicted_top_10_rain_rate": 15.2,
                "predicted_location": {"type": "Point", "coordinates": [12.97, 77.59]},
                "is_warning": True,
                "generated_by_user_id": "60c72b2f9b1d8e001f8e4a3e",
                "timestamp": "2025-08-03T12:30:00Z",
                "forecast_time": 60,
            }
        }
    )

# Warning and Notification models can stay as they are useful for the system
class Warning(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    prediction_id: Optional[PyObjectId] = None # Link to Prediction
    message: str
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "prediction_id": "60c72b2f9b1d8e001f8e4a3c",
                "message": "Heavy rainfall warning for the next 30 minutes.",
                "is_active": True
            }
        }
    )

class Notification(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    warning_id: Optional[PyObjectId] = None
    message: str
    channel: str
    recipient: Optional[str] = None
    status: str = "pending"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "warning_id": "60c72b2f9b1d8e001f8e4a3c",
                "message": "Heavy rainfall alert issued.",
                "channel": "email",
                "recipient": "user@example.com",
                "status": "sent"
            }
        }
    )
