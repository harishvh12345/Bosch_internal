import logging
from uuid import UUID
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.quiz_repo import quiz_repo, quiz_result_repo, quiz_question_repo
from app.repositories.profile_repo import profile_repo
from app.models.quiz import QuizResult, Quiz
from app.schemas.quiz import QuizSubmitRequest, QuizResultResponse
from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)

class QuizService:
    async def get_quiz(self, db: AsyncSession, quiz_id: UUID) -> Quiz:
        quiz = await quiz_repo.get_with_questions(db, quiz_id)
        if not quiz:
            raise NotFoundException(detail="Quiz not found")
        return quiz

    async def submit_answers(
        self, db: AsyncSession, user_id: UUID, quiz_id: UUID, submission: QuizSubmitRequest
    ) -> QuizResult:
        quiz = await quiz_repo.get_with_questions(db, quiz_id)
        if not quiz:
            raise NotFoundException(detail="Quiz not found")

        # Grade the answers
        correct_count = 0
        total_questions = len(quiz.questions)
        
        answers_graded = {}
        correct_answers_map = {}
        explanations_map = {}

        for q in quiz.questions:
            user_ans = submission.answers.get(q.id, "").strip()
            correct_ans = q.correct_answer.strip()
            
            # Save mapping
            answers_graded[str(q.id)] = user_ans
            correct_answers_map[q.id] = correct_ans
            explanations_map[q.id] = q.explanation

            # Simple string matching for MCQs and simple questions
            if q.question_type == "MCQ":
                if user_ans.lower() == correct_ans.lower():
                    correct_count += 1
            else:
                # Coding/Scenario questions: check substring or matching terms
                if correct_ans.lower() in user_ans.lower() or user_ans.lower() in correct_ans.lower():
                    correct_count += 1

        score = (correct_count / total_questions * 100.0) if total_questions > 0 else 0.0

        # Save result
        result_data = {
            "user_id": user_id,
            "quiz_id": quiz_id,
            "score": score,
            "answers": answers_graded
        }
        
        quiz_result = await quiz_result_repo.create(db, obj_in=result_data)
        await db.flush()

        # Update profile learning achievements or levels if they passed (score >= 70%)
        if score >= 70.0:
            profile = await profile_repo.get_by_user_id(db, user_id)
            if profile:
                if not profile.learning_history:
                    profile.learning_history = {}
                completed_quizzes = profile.learning_history.get("completed_quizzes", [])
                if str(quiz_id) not in completed_quizzes:
                    completed_quizzes.append(str(quiz_id))
                profile.learning_history["completed_quizzes"] = completed_quizzes
                
                # Check if we can increment a skill level
                # For example, mapping quiz keywords to profile skills
                for assoc in profile.skills_association:
                    if assoc.skill.name.lower() in quiz.title.lower() and assoc.level < 5:
                        assoc.level += 1
                        logger.info(f"Incremented skill {assoc.skill.name} to level {assoc.level} for user {user_id}")
                
                db.add(profile)
                await db.flush()

        return quiz_result

quiz_service = QuizService()
