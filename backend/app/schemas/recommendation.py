from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class RecommendationResponse(BaseModel):
    id: UUID
    user_id: UUID
    rec_type: str  # MODULE, COURSE, SIMULATION
    reference_id: Optional[UUID] = None
    title: str
    reasoning: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
