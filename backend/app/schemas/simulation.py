from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Dict, Any, List, Optional

class SimulationBase(BaseModel):
    name: str
    model_file: str
    description: Optional[str] = None

class SimulationCreate(SimulationBase):
    pass

class SimulationResponse(SimulationBase):
    id: UUID

    class Config:
        from_attributes = True

class SimulationHistoryBase(BaseModel):
    parameters: Dict[str, Any] = {}
    status: str = "PENDING"
    logs: Optional[str] = None
    result_images: List[str] = []
    execution_time_seconds: float = 0.0

class SimulationHistoryCreate(BaseModel):
    simulation_id: UUID
    parameters: Dict[str, Any] = {}

class SimulationHistoryResponse(SimulationHistoryBase):
    id: UUID
    user_id: UUID
    simulation_id: UUID
    created_at: datetime
    simulation: SimulationResponse

    class Config:
        from_attributes = True

class SimulationRunRequest(BaseModel):
    parameters: Dict[str, Any] = {}  # e.g., {"Kp": 2.0, "Ki": 0.5, "Kd": 0.1}
