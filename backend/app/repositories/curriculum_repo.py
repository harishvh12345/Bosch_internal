from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.repositories.base import CRUDBase
from app.models.curriculum import LearningGoal, LearningModule, CurriculumTopic, CurriculumTask, Progress

class LearningGoalRepository(CRUDBase[LearningGoal]):
    async def get_with_modules(self, db: AsyncSession, goal_id: str) -> Optional[LearningGoal]:
        query = (
            select(LearningGoal)
            .where(LearningGoal.id == goal_id)
            .options(
                selectinload(LearningGoal.modules)
                .selectinload(LearningModule.topics)
                .selectinload(CurriculumTopic.tasks)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_active_by_user(self, db: AsyncSession, user_id: str) -> List[LearningGoal]:
        query = (
            select(LearningGoal)
            .where(LearningGoal.user_id == user_id)
            .order_by(LearningGoal.created_at.desc())
        )

        result = await db.execute(select(LearningGoal).where(LearningGoal.user_id == user_id))
        return list(result.scalars().all())

class LearningModuleRepository(CRUDBase[LearningModule]):
    async def get_by_goal_and_order(self, db: AsyncSession, goal_id: str, order: int) -> Optional[LearningModule]:
        query = (
            select(LearningModule)
            .where(LearningModule.learning_goal_id == goal_id, LearningModule.order_index == order)
            .options(
                selectinload(LearningModule.topics)
                .selectinload(CurriculumTopic.tasks)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

class CurriculumTopicRepository(CRUDBase[CurriculumTopic]):
    pass

class CurriculumTaskRepository(CRUDBase[CurriculumTask]):
    async def get_task_with_relations(self, db: AsyncSession, task_id: str) -> Optional[CurriculumTask]:
        query = (
            select(CurriculumTask)
            .where(CurriculumTask.id == task_id)
            .options(
                selectinload(CurriculumTask.simulation),
                selectinload(CurriculumTask.quiz)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

class ProgressRepository(CRUDBase[Progress]):
    async def get_by_goal(self, db: AsyncSession, goal_id: str) -> Optional[Progress]:
        query = select(Progress).where(Progress.learning_goal_id == goal_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def calculate_and_update(self, db: AsyncSession, user_id: str, goal_id: str) -> Progress:
        # Get count of total tasks for goal
        total_tasks_query = (
            select(func.count(CurriculumTask.id))
            .join(CurriculumTopic)
            .join(LearningModule)
            .where(LearningModule.learning_goal_id == goal_id)
        )
        total_result = await db.execute(total_tasks_query)
        total_count = total_result.scalar() or 0

        # Get count of completed tasks
        completed_tasks_query = (
            select(func.count(CurriculumTask.id))
            .join(CurriculumTopic)
            .join(LearningModule)
            .where(LearningModule.learning_goal_id == goal_id, CurriculumTask.status == "COMPLETED")
        )
        completed_result = await db.execute(completed_tasks_query)
        completed_count = completed_result.scalar() or 0

        percent = (completed_count / total_count * 100.0) if total_count > 0 else 0.0

        # Find or create Progress row
        progress = await self.get_by_goal(db, goal_id)
        if not progress:
            progress = Progress(
                user_id=user_id,
                learning_goal_id=goal_id,
                percent_completed=percent,
                time_spent_hours=0.0
            )
            db.add(progress)
        else:
            progress.percent_completed = percent
            
        await db.flush()
        return progress

goal_repo = LearningGoalRepository(LearningGoal)
module_repo = LearningModuleRepository(LearningModule)
topic_repo = CurriculumTopicRepository(CurriculumTopic)
task_repo = CurriculumTaskRepository(CurriculumTask)
progress_repo = ProgressRepository(Progress)
