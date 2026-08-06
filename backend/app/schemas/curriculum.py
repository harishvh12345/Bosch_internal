from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class LearningGoalCreate(BaseModel):
    goal_text: str
    simulation_focus: Optional[str] = None

class LearningGoalResponse(BaseModel):
    id: UUID
    user_id: UUID
    goal_text: str
    simulation_focus: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CurriculumTaskBase(BaseModel):
    title: str
    type: str  # LAB, READING, SIMULATION, QUIZ
    content: Optional[str] = None
    duration_minutes: int = 30
    simulation_id: Optional[UUID] = None
    quiz_id: Optional[UUID] = None
    order_index: int
    status: str = "NOT_STARTED"

class CurriculumTaskResponse(CurriculumTaskBase):
    id: UUID
    topic_id: UUID

    class Config:
        from_attributes = True

class CurriculumTaskStatusUpdate(BaseModel):
    status: str  # NOT_STARTED, IN_PROGRESS, COMPLETED

class CurriculumTopicBase(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int
    status: str = "NOT_STARTED"

class CurriculumTopicResponse(CurriculumTopicBase):
    id: UUID
    module_id: UUID
    tasks: List[CurriculumTaskResponse] = []

    class Config:
        from_attributes = True

class LearningModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    difficulty: str
    estimated_hours: float
    order_index: int
    status: str = "NOT_STARTED"

class LearningModuleResponse(LearningModuleBase):
    id: UUID
    learning_goal_id: UUID
    topics: List[CurriculumTopicResponse] = []

    class Config:
        from_attributes = True

class LearningModuleSummaryResponse(LearningModuleBase):
    id: UUID
    learning_goal_id: UUID

    class Config:
        from_attributes = True

class ProgressResponse(BaseModel):
    id: UUID
    user_id: UUID
    learning_goal_id: UUID
    percent_completed: float
    time_spent_hours: float
    last_accessed: datetime

    class Config:
        from_attributes = True
