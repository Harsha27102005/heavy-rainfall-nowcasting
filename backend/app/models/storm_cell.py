from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from .common import PyObjectId
from bson import ObjectId

class StormCell(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    # cell_id in LLD is PK, here we use _id as PK, but we can keep an explicit cell_id if needed for external ref
    # LLD: cell_id | INT (PK)
    # If we use _id as the main ID, we can omit cell_id or keep it as a field if it comes from the data source.
    # I'll assume _id is the cell_id for internal use, but if there is an external ID, I'll add it.
    # The LLD description says "A unique identifier for each instance of a storm cell".
    
    timestamp: datetime
    storm_type: str # 'CC', 'SLD', etc.
    mean_rain_rate: float
    top_10_rain_rate: float
    mean_z: float
    volume: float
    max_vil: float
    
    # Additional variables mentioned in LLD (17 variables total)
    # Rmj, Rmn, Area, Top, Base, MaxZ, MaxZ.g, AvgVIL, U, V, Direction
    rmj: Optional[float] = None
    rmn: Optional[float] = None
    area: Optional[float] = None
    top: Optional[float] = None
    base: Optional[float] = None
    max_z: Optional[float] = None
    max_z_g: Optional[float] = None
    avg_vil: Optional[float] = None
    u: Optional[float] = None
    v: Optional[float] = None
    direction: Optional[float] = None
    
    # Topographic variables (5 variables)
    # distance to sea, elevation, aspect, roughness, slope
    dist_to_sea: Optional[float] = None
    elevation: Optional[float] = None
    aspect: Optional[float] = None
    roughness: Optional[float] = None
    slope: Optional[float] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
