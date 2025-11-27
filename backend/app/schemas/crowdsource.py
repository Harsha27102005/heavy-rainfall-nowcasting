from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReportCreate(BaseModel):
    location: str
    intensity: str
    description: Optional[str] = None

class ReportResponse(BaseModel):
    id: str
    location: str
    intensity: str
    description: Optional[str] = None
    timestamp: datetime
    status: str

    class Config:
        orm_mode = True
