from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.api.v1.auth import get_current_user, allow_all
from app.services.curriculum_service import curriculum_service
from app.services.search.knowledge_base import knowledge_base
from app.repositories.curriculum_repo import goal_repo, progress_repo, module_repo
from app.schemas.curriculum import (
    LearningGoalCreate,
    LearningGoalResponse,
    LearningModuleResponse,
    LearningModuleSummaryResponse,
    CurriculumTaskResponse,
    CurriculumTaskStatusUpdate,
    ProgressResponse
)
from app.models.user import User
from typing import List

router = APIRouter()

@router.post("/goals", response_model=LearningGoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal_path(
    goal_in: LearningGoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Retrieve relevant internal Bosch manuals first
    context = await knowledge_base.get_relevant_context(db, query=goal_in.goal_text, top_k=3)
    
    return await curriculum_service.create_learning_goal_path(
        db,
        user_id=current_user.id,
        goal_text=goal_in.goal_text,
        context_docs=context,
        simulation_focus=goal_in.simulation_focus or ""
    )


@router.get("/goals", response_model=List[LearningGoalResponse])
async def list_goals(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await goal_repo.get_active_by_user(db, current_user.id)

@router.get("/goals/{goal_id}/modules", response_model=List[LearningModuleSummaryResponse])
async def list_goal_modules(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    goal = await goal_repo.get_with_modules(db, goal_id)
    if not goal:
        return []
    return goal.modules

@router.get("/modules/{module_id}", response_model=LearningModuleResponse)
async def get_module_detail(
    module_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # This call handles lazy generation of topics and tasks on first load
    return await curriculum_service.get_module_detail(db, current_user.id, module_id)

@router.put("/tasks/{task_id}/status", response_model=CurriculumTaskResponse)
async def update_task_status(
    task_id: UUID,
    status_update: CurriculumTaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await curriculum_service.update_task_status(
        db, user_id=current_user.id, task_id=task_id, status=status_update.status
    )

@router.get("/goals/{goal_id}/progress", response_model=ProgressResponse)
async def get_progress(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    progress = await progress_repo.get_by_goal(db, goal_id)
    if not progress:
        # Calculate now
        return await progress_repo.calculate_and_update(db, current_user.id, goal_id)
    return progress

