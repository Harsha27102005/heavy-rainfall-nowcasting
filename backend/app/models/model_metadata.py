from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from .common import PyObjectId
from bson import ObjectId

class ModelMetadata(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    model_type: str # 'ANN', 'RFR', 'CNN', etc.
    storm_type_trained_on: str # 'CC', 'MSL', 'All'
    nowcast_time: int # 30 or 60
    created_date: datetime = Field(default_factory=datetime.utcnow)
    created_by_user_id: Optional[PyObjectId] = None # Link to User

    # Additional metadata not in LLD table but useful
    status: str = "trained" # 'training', 'trained', 'failed'
    metrics: Optional[dict] = None # Store validation metrics

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
