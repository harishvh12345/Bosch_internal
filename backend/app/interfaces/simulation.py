from abc import ABC, abstractmethod
from typing import Dict, Any

class SimulationService(ABC):
    @abstractmethod
    async def execute_simulation(
        self, model_file: str, parameters: Dict[str, Any], history_id: str
    ) -> Dict[str, Any]:
        """
        Trigger an asynchronous simulation run.
        Returns simulation metrics: status, execution time, logs, and output file paths.
        """
        pass

    @abstractmethod
    async def get_simulation_status(self, history_id: str) -> Dict[str, Any]:
        """
        Get the current execution status and metrics for a triggered run.
        """
        pass
