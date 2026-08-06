from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.api.v1.auth import get_current_user
from app.services.quiz_service import quiz_service
from app.schemas.quiz import QuizResponse, QuizSubmitRequest, QuizResultResponse
from app.repositories.quiz_repo import quiz_result_repo
from app.models.user import User

router = APIRouter()

@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await quiz_service.get_quiz(db, quiz_id)

@router.post("/{quiz_id}/submit", response_model=QuizResultResponse)
async def submit_quiz(
    quiz_id: UUID,
    submission: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Process grading and profile updates
    result = await quiz_service.submit_answers(db, current_user.id, quiz_id, submission)
    
    # Format detailed response containing correct solutions and explanations for review
    quiz = await quiz_service.get_quiz(db, quiz_id)
    correct_answers = {q.id: q.correct_answer for q in quiz.questions}
    explanations = {q.id: q.explanation for q in quiz.questions}
    
    return QuizResultResponse(
        id=result.id,
        user_id=result.user_id,
        quiz_id=result.quiz_id,
        score=result.score,
        answers=result.answers,
        completed_at=result.completed_at,
        correct_answers=correct_answers,
        explanations=explanations
    )

