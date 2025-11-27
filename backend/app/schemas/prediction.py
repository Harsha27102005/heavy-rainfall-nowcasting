# backend/app/schemas/prediction.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List

# Base schemas for data storage
class RainfallPredictionBase(BaseModel):
    cell_id: str
    mcs_type: str
    forecast_time: int
    predicted_timestamp: datetime
    predicted_mean_rain_rate: float = Field(alias="predicted_mean_rr") # Allow alias for backward compat
    predicted_top_10_rain_rate: float = Field(alias="predicted_top10_mean_rr")

class RainfallPredictionCreate(RainfallPredictionBase):
    pass

class RainfallPrediction(RainfallPredictionBase):
    id: str
    prediction_made_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}

class StormCellLocationBase(BaseModel):
    cell_id: str
    mcs_type: str
    forecast_time: int
    predicted_timestamp: datetime
    predicted_location: Dict[str, Any] = Field(alias="predicted_location_geojson") # GeoJSON object
    predicted_mean_rain_rate: float = Field(alias="predicted_mean_rr")
    predicted_top_10_rain_rate: float = Field(alias="predicted_top10_mean_rr")
    impact_risk: Optional[str] = "Low"

class StormCellLocationCreate(StormCellLocationBase):
    pass

class StormCellLocation(StormCellLocationBase):
    id: str
    prediction_made_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}

class WarningBase(BaseModel):
    cell_id: str
    mcs_type: str
    forecast_time: int
    predicted_timestamp: datetime
    predicted_top_10_rain_rate: float = Field(alias="predicted_top10_mean_rr")
    message: str
    location_geojson: Dict[str, Any]
    is_active: bool = True

class WarningCreate(WarningBase):
    pass

class Warning(WarningBase):
    id: str
    issued_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}

# Schema for frontend consumption (e.g., combined nowcast data)
class NowcastResponse(BaseModel):
    timestamp: datetime
    selected_forecast_time: str
    predicted_storm_cells: List[StormCellLocation]