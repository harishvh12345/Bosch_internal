import logging
from uuid import UUID
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.curriculum_repo import goal_repo, module_repo, topic_repo, task_repo, progress_repo
from app.repositories.profile_repo import profile_repo
from app.repositories.simulation_repo import sim_repo
from app.repositories.quiz_repo import quiz_repo, quiz_question_repo
from app.models.curriculum import LearningGoal, LearningModule, CurriculumTopic, CurriculumTask, Progress
from app.models.simulation import Simulation
from app.models.quiz import Quiz, QuizQuestion
from app.services.gemini.client import ai_service
from app.core.exceptions import NotFoundException

logger = logging.getLogger(__name__)

class CurriculumService:
    async def create_learning_goal_path(
        self, db: AsyncSession, user_id: UUID, goal_text: str, context_docs: str = "", simulation_focus: str = ""
    ) -> LearningGoal:
        # Fetch user profile for context
        profile = await profile_repo.get_by_user_id(db, user_id)
        profile_dict = {}
        if profile:
            skills_list = [f"{assoc.skill.name} (Lvl {assoc.level})" for assoc in profile.skills_association]
            profile_dict = {
                "department": profile.department.name if profile.department else "Engineering",
                "role": profile.user.role.name if profile.user and profile.user.role else "Developer",
                "experience_years": profile.experience_years,
                "skills": skills_list,
                "learning_history": profile.learning_history
            }
            
        # 1. Trigger Gemini to analyze gap & modules roadmap
        analysis = await ai_service.analyze_skills_gap(profile_dict, goal_text, context_docs, simulation_focus)
        
        # Update user profile with learning history / goals if needed
        if profile:
            if not profile.learning_history:
                profile.learning_history = {}
            profile.learning_history["active_goal"] = goal_text
            profile.learning_history["skill_gap"] = analysis.get("skill_gap", [])
            db.add(profile)

        # 2. Save LearningGoal
        goal_data = {"user_id": user_id, "goal_text": goal_text, "simulation_focus": simulation_focus}
        goal = await goal_repo.create(db, obj_in=goal_data)


        # 3. Save high-level modules skeletons
        modules_list = analysis.get("roadmap_modules", [])
        for m_data in modules_list:
            module_obj = LearningModule(
                learning_goal_id=goal.id,
                title=m_data.get("title", "Untitled Module"),
                description=m_data.get("description", ""),
                difficulty=m_data.get("difficulty", "Medium"),
                estimated_hours=m_data.get("estimated_hours", 2.0),
                order_index=m_data.get("order_index", 1),
                status="NOT_STARTED"
            )
            db.add(module_obj)
            
        await db.flush()

        # Initialize progress tracker at 0%
        await progress_repo.calculate_and_update(db, user_id, goal.id)

        # Return full goal with module skeletons
        await db.refresh(goal)
        return goal

    async def get_module_detail(self, db: AsyncSession, user_id: UUID, module_id: UUID) -> LearningModule:
        """
        Loads the module. If it does not contain topics/tasks yet, 
        it triggers Gemini to lazy-generate them on-the-fly and saves them.
        """
        module = await module_repo.get(db, module_id)
        if not module:
            raise NotFoundException(detail="Learning module not found")

        # Load topics relationship
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        query = (
            select(LearningModule)
            .where(LearningModule.id == module_id)
            .options(
                selectinload(LearningModule.topics)
                .selectinload(CurriculumTopic.tasks)
            )
        )
        res = await db.execute(query)
        module = res.scalar_one()

        if len(module.topics) > 0:
            # Already generated, return directly
            return module

        # Topics are empty - trigger lazy-loading module curriculum generation
        logger.info(f"Topics empty. Lazy generating curriculum for module: {module.title}")
        goal = await goal_repo.get(db, module.learning_goal_id)
        
        # Profile context
        profile = await profile_repo.get_by_user_id(db, user_id)
        profile_dict = {
            "role": profile.user.role.name if profile and profile.user and profile.user.role else "Developer",
            "experience_years": profile.experience_years if profile else 0,
        }

        # Call AI curriculum builder
        detail = await ai_service.generate_module_curriculum(
            profile_dict, goal.goal_text, module.title, module.order_index, "", goal.simulation_focus or ""
        )

        # Save generated topics & tasks
        topics_data = detail.get("topics", [])
        for t_idx, topic_data in enumerate(topics_data):
            topic_obj = CurriculumTopic(
                module_id=module.id,
                title=topic_data.get("title", f"Topic {t_idx + 1}"),
                description=topic_data.get("description", ""),
                order_index=topic_data.get("order_index", t_idx + 1),
                status="NOT_STARTED"
            )
            db.add(topic_obj)
            await db.flush()  # get topic ID

            tasks_data = topic_data.get("tasks", [])
            for task_idx, task_data in enumerate(tasks_data):
                task_type = task_data.get("type", "READING")
                sim_id = None
                quiz_obj_id = None

                # Check if it maps to a simulation model
                if task_type == "SIMULATION":
                    model_name = task_data.get("simulation_model_name")
                    if model_name:
                        # Find simulation record in DB (ECU, CAN, PID)
                        sim = await sim_repo.get_by_name(db, model_name)
                        if sim:
                            sim_id = sim.id

                # Check if it is a quiz task - generate the quiz skeleton
                if task_type == "QUIZ":
                    quiz_skeleton = await quiz_repo.create(db, obj_in={
                        "title": f"Quiz: {topic_obj.title}",
                        "difficulty": module.difficulty
                    })
                    quiz_obj_id = quiz_skeleton.id
                    
                    # Generate quiz questions
                    quiz_data = await ai_service.generate_quiz(
                        module.title, 
                        [topic_obj.title], 
                        module.difficulty
                    )
                    questions = quiz_data.get("questions", [])
                    for q in questions:
                        q_obj = QuizQuestion(
                            quiz_id=quiz_obj_id,
                            question_text=q.get("question_text", ""),
                            question_type=q.get("question_type", "MCQ"),
                            options=q.get("options"),
                            correct_answer=str(q.get("correct_answer", "")),
                            explanation=q.get("explanation", "")
                        )
                        db.add(q_obj)

                task_obj = CurriculumTask(
                    topic_id=topic_obj.id,
                    title=task_data.get("title", f"Task {task_idx + 1}"),
                    type=task_type,
                    content=task_data.get("content", ""),
                    duration_minutes=task_data.get("duration_minutes", 30),
                    simulation_id=sim_id,
                    quiz_id=quiz_obj_id,
                    order_index=task_data.get("order_index", task_idx + 1),
                    status="NOT_STARTED"
                )
                db.add(task_obj)

        module.status = "IN_PROGRESS"
        db.add(module)
        await db.flush()

        # Re-fetch full hierarchy
        res = await db.execute(query)
        return res.scalar_one()

    async def update_task_status(
        self, db: AsyncSession, user_id: UUID, task_id: UUID, status: str
    ) -> CurriculumTask:
        task = await task_repo.get(db, task_id)
        if not task:
            raise NotFoundException(detail="Task not found")

        task.status = status
        db.add(task)
        await db.flush()

        # Update parent topic status if all tasks completed
        topic = await topic_repo.get(db, task.topic_id)
        if topic:
            # Check all tasks in topic
            from sqlalchemy import select
            tasks_query = select(CurriculumTask).where(CurriculumTask.topic_id == topic.id)
            res = await db.execute(tasks_query)
            all_tasks = res.scalars().all()
            
            if all(t.status == "COMPLETED" for t in all_tasks):
                topic.status = "COMPLETED"
            elif any(t.status in ["IN_PROGRESS", "COMPLETED"] for t in all_tasks):
                topic.status = "IN_PROGRESS"
            else:
                topic.status = "NOT_STARTED"
            db.add(topic)
            await db.flush()

            # Update parent module status
            module = await module_repo.get(db, topic.module_id)
            if module:
                topics_query = select(CurriculumTopic).where(CurriculumTopic.module_id == module.id)
                res = await db.execute(topics_query)
                all_topics = res.scalars().all()
                
                if all(top.status == "COMPLETED" for top in all_topics):
                    module.status = "COMPLETED"
                db.add(module)
                await db.flush()

                # Calculate progress score
                await progress_repo.calculate_and_update(db, user_id, module.learning_goal_id)

        return task

curriculum_service = CurriculumService()
