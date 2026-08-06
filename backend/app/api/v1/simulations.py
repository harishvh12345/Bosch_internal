from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.api.v1.auth import get_current_user, allow_manager, allow_all
from app.repositories.simulation_repo import sim_repo, sim_history_repo
from app.schemas.simulation import (
    SimulationResponse,
    SimulationHistoryResponse,
    SimulationRunRequest
)
from app.models.user import User
from app.models.simulation import SimulationHistory
from app.services.mcp.queue import add_simulation_to_queue
from typing import List

router = APIRouter()

@router.get("", response_model=List[SimulationResponse])
async def list_simulations(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(allow_all)
):
    return await sim_repo.get_multi(db, limit=100)

@router.post("/run/{simulation_id}", response_model=SimulationHistoryResponse)
async def run_simulation(
    simulation_id: UUID,
    run_req: SimulationRunRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify simulation exists
    sim = await sim_repo.get(db, simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation model not found")

    # Create simulation history record
    history_data = {
        "user_id": current_user.id,
        "simulation_id": sim.id,
        "parameters": run_req.parameters,
        "status": "PENDING",
        "logs": "Job queued. Waiting for background worker.",
        "result_images": [],
        "execution_time_seconds": 0.0
    }
    run = await sim_history_repo.create(db, obj_in=history_data)
    await db.commit() # Commit to persist history ID for queue

    # Push to async queue worker
    await add_simulation_to_queue(run.id, sim.model_file, run_req.parameters)

    # Re-query to include nested relations for response validation
    result = await sim_history_repo.get_with_simulation(db, run.id)
    return result

@router.get("/runs", response_model=List[SimulationHistoryResponse])
async def list_user_simulation_history(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await sim_history_repo.get_by_user(db, current_user.id)

@router.get("/runs/{run_id}", response_model=SimulationHistoryResponse)
async def get_simulation_run(
    run_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    run = await sim_history_repo.get_with_simulation(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found")
    return run

@router.post("/seed", status_code=status.HTTP_200_OK)
async def seed_simulations(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(allow_manager)
):
    defaults = [
        ("PID Control", "pid_model.slx", "Closed-loop feedback damping and overshoot control loop models."),
        ("CAN Bus", "can_model.slx", "Automotive communication packet scheduler and frame collision simulator."),
        ("ECU Engine", "ecu_model.slx", "Electronic Control Unit throttle angle speed actuator logging simulator.")
    ]
    for name, file, desc in defaults:
        exists = await sim_repo.get_by_name(db, name)
        if not exists:
            await sim_repo.create(db, obj_in={"name": name, "model_file": file, "description": desc})
    return {"message": "Simulation models seeded successfully."}

