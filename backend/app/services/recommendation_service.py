import logging
from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.recommendation_repo import rec_repo
from app.repositories.profile_repo import profile_repo
from app.repositories.quiz_repo import quiz_result_repo
from app.repositories.simulation_repo import sim_history_repo
from app.models.recommendation import Recommendation
from app.services.gemini.client import ai_service

logger = logging.getLogger(__name__)

class RecommendationService:
    async def get_user_recommendations(self, db: AsyncSession, user_id: UUID) -> List[Recommendation]:
        # Return existing active recommendations
        return await rec_repo.get_active_by_user(db, user_id)

    async def refresh_user_recommendations(self, db: AsyncSession, user_id: UUID) -> List[Recommendation]:
        """Queries user data, gets recommendations from AI, and writes to database."""
        # 1. Fetch user context
        profile = await profile_repo.get_by_user_id(db, user_id)
        if not profile:
            return []

        quiz_results = await quiz_result_repo.get_by_user(db, user_id)
        sim_history = await sim_history_repo.get_by_user(db, user_id)

        # De-active old recommendations
        old_recs = await rec_repo.get_active_by_user(db, user_id)
        for r in old_recs:
            r.is_active = False
            db.add(r)
        await db.flush()

        # Format context for AI
        skills_list = [f"{assoc.skill.name} (Lvl {assoc.level})" for assoc in profile.skills_association]
        profile_dict = {
            "role": profile.user.role.name if profile.user and profile.user.role else "Developer",
            "experience_years": profile.experience_years,
            "skills": skills_list,
            "active_goal": profile.learning_history.get("active_goal", "Learn ECU Kit")
        }

        quizzes_summary = [{"title": r.quiz.title, "score": r.score} for r in quiz_results if r.quiz]
        sims_summary = [{"model": h.simulation.name, "status": h.status} for h in sim_history if h.simulation]

        # 2. Call AI advisor
        ai_recs = await ai_service.generate_recommendations(
            profile=profile_dict,
            quiz_results=quizzes_summary,
            simulation_results=sims_summary
        )

        # 3. Save new recommendations
        new_recs = []
        for r_data in ai_recs:
            rec = Recommendation(
                user_id=user_id,
                rec_type=r_data.get("rec_type", "COURSE"),
                title=r_data.get("title", "Recommended Training"),
                reasoning=r_data.get("reasoning", "Suggested based on current curriculum profile."),
                is_active=True
            )
            db.add(rec)
            new_recs.append(rec)
            
        await db.flush()
        return new_recs

recommendation_service = RecommendationService()
