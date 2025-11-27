from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from .common import PyObjectId
from bson import ObjectId

class VariableImportance(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    model_id: PyObjectId # Link to ModelMetadata
    variable_name: str
    importance_score: float
    is_pertinent: bool

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
