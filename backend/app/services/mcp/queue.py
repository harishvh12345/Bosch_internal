import asyncio
import logging
from uuid import UUID
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import AsyncSessionLocal
from app.repositories.simulation_repo import sim_history_repo
from app.services.mcp.client import mcp_client
from app.services.gemini.client import ai_service

logger = logging.getLogger(__name__)

# Queue to hold pending simulations: contains (history_id, model_file, parameters)
simulation_queue = asyncio.Queue()

async def add_simulation_to_queue(
    history_id: UUID, model_file: str, parameters: Dict[str, Any]
) -> None:
    """Adds a simulation job to the background processing queue."""
    await simulation_queue.put((history_id, model_file, parameters))
    logger.info(f"Simulation job {history_id} added to the execution queue.")

async def process_simulation_queue() -> None:
    """Background worker loops infinitely, executing simulation runs sequentially."""
    logger.info("Background simulation worker started.")
    while True:
        item_retrieved = False
        try:
            history_id, model_file, parameters = await simulation_queue.get()
            item_retrieved = True
            logger.info(f"Processing simulation job: {history_id}")
            
            # 1. Update status to RUNNING in database
            async with AsyncSessionLocal() as db:
                run = await sim_history_repo.get(db, history_id)
                if run:
                    run.status = "RUNNING"
                    db.add(run)
                    await db.commit()
            
            # 2. Run simulation via MCP Client
            status_data = {"status": "FAILED", "logs": "", "result_images": [], "execution_time_seconds": 0.0}
            try:
                status_data = await mcp_client.execute_simulation(model_file, parameters, str(history_id))
            except Exception as e:
                logger.error(f"Error executing simulation {history_id}: {e}")
                status_data["logs"] = f"Simulation execution failed with error: {e}"
            
            # 3. Request Gemini to analyze results/logs
            model_name = model_file.replace(".slx", "").upper()
            ai_explanation = ""
            try:
                ai_explanation = await ai_service.explain_simulation_output(
                    model_name=model_name,
                    parameters=parameters,
                    status=status_data["status"],
                    logs=status_data["logs"]
                )
                # Append AI analysis to the simulation log
                status_data["logs"] += f"\n\n--- AI COGNITIVE TELEMETRY ANALYSIS ---\n{ai_explanation}"
            except Exception as ae:
                logger.error(f"Failed to generate AI analysis: {ae}")

            # 4. Save results back to database
            async with AsyncSessionLocal() as db:
                run = await sim_history_repo.get(db, history_id)
                if run:
                    run.status = status_data["status"]
                    run.logs = status_data["logs"]
                    run.result_images = status_data["result_images"]
                    run.execution_time_seconds = status_data["execution_time_seconds"]
                    db.add(run)
                    await db.commit()
                    
            logger.info(f"Simulation job {history_id} completed successfully.")
            
        except asyncio.CancelledError:
            logger.info("Simulation queue processor cancelled.")
            break
        except Exception as e:
            logger.error(f"Critical error in simulation queue worker: {e}")
            await asyncio.sleep(5)  # Pause to avoid rapid loops on persistent issues
        finally:
            if item_retrieved:
                # Notify the queue that the item is processed
                simulation_queue.task_done()

