from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.repositories.base import CRUDBase
from app.models.quiz import Quiz, QuizQuestion, QuizResult

class QuizRepository(CRUDBase[Quiz]):
    async def get_with_questions(self, db: AsyncSession, quiz_id: str) -> Optional[Quiz]:
        query = (
            select(Quiz)
            .where(Quiz.id == quiz_id)
            .options(selectinload(Quiz.questions))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

class QuizQuestionRepository(CRUDBase[QuizQuestion]):
    pass

class QuizResultRepository(CRUDBase[QuizResult]):
    async def get_by_user(self, db: AsyncSession, user_id: str) -> List[QuizResult]:
        query = (
            select(QuizResult)
            .where(QuizResult.user_id == user_id)
            .options(selectinload(QuizResult.quiz))
            .order_by(QuizResult.completed_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_user_and_quiz(self, db: AsyncSession, user_id: str, quiz_id: str) -> Optional[QuizResult]:
        query = (
            select(QuizResult)
            .where(QuizResult.user_id == user_id, QuizResult.quiz_id == quiz_id)
            .order_by(QuizResult.completed_at.desc())
        )
        result = await db.execute(query)
        return result.scalars().first()

quiz_repo = QuizRepository(Quiz)
quiz_question_repo = QuizQuestionRepository(QuizQuestion)
quiz_result_repo = QuizResultRepository(QuizResult)
