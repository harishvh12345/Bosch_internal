from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.repositories.base import CRUDBase
from app.models.simulation import Simulation, SimulationHistory

class SimulationRepository(CRUDBase[Simulation]):
    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Simulation]:
        query = select(Simulation).where(Simulation.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_model_file(self, db: AsyncSession, model_file: str) -> Optional[Simulation]:
        query = select(Simulation).where(Simulation.model_file == model_file)
        result = await db.execute(query)
        return result.scalar_one_or_none()

class SimulationHistoryRepository(CRUDBase[SimulationHistory]):
    async def get_by_user(self, db: AsyncSession, user_id: str) -> List[SimulationHistory]:
        query = (
            select(SimulationHistory)
            .where(SimulationHistory.user_id == user_id)
            .options(selectinload(SimulationHistory.simulation))
            .order_by(SimulationHistory.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_with_simulation(self, db: AsyncSession, history_id: str) -> Optional[SimulationHistory]:
        query = (
            select(SimulationHistory)
            .where(SimulationHistory.id == history_id)
            .options(selectinload(SimulationHistory.simulation))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

sim_repo = SimulationRepository(Simulation)
sim_history_repo = SimulationHistoryRepository(SimulationHistory)
