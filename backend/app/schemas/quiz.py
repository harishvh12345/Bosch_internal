from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Dict, Optional

class QuizQuestionResponse(BaseModel):
    id: UUID
    question_text: str
    question_type: str  # MCQ, CODING, SCENARIO
    options: Optional[List[str]] = None  # MCQ options

    class Config:
        from_attributes = True

class QuizResponse(BaseModel):
    id: UUID
    title: str
    difficulty: str
    questions: List[QuizQuestionResponse] = []

    class Config:
        from_attributes = True

class QuizSubmitRequest(BaseModel):
    answers: Dict[UUID, str]  # mapping of question_id (UUID string) to user answer text

class QuizResultResponse(BaseModel):
    id: UUID
    user_id: UUID
    quiz_id: UUID
    score: float
    answers: Dict[str, str]
    completed_at: datetime
    correct_answers: Dict[UUID, str] = {}  # returns correct answers for review
    explanations: Dict[UUID, str] = {}  # returns explanations for questions

    class Config:
        from_attributes = True
