from pydantic import BaseModel, ConfigDict
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    text: str
    created_date: datetime
    rubrics: list[str]
    
    model_config = ConfigDict(from_attributes=True)
