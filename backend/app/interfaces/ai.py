from abc import ABC, abstractmethod
from typing import Dict, Any, List

class AIService(ABC):
    @abstractmethod
    async def analyze_skills_gap(
        self, profile: Dict[str, Any], goal: str, context_docs: str = "", simulation_focus: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze employee skills gap against a goal and return structured analysis:
        Skill Gap, Prerequisites, Difficulty Level, Learning Objectives, Estimated Duration.
        """
        pass

    @abstractmethod
    async def generate_module_curriculum(
        self, profile: Dict[str, Any], goal: str, module_title: str, module_index: int, context_docs: str = "", simulation_focus: str = ""
    ) -> Dict[str, Any]:
        """
        Generate curriculum detail for a specific module:
        Topics, Subtopics, Hands-on labs (Simulink mapping), Exercises, Expected outputs.
        """
        pass


    @abstractmethod
    async def generate_quiz(self, module_title: str, topics: List[str], difficulty: str) -> Dict[str, Any]:
        """
        Generate questions (MCQ, scenario, coding) based on module topic content.
        """
        pass

    @abstractmethod
    async def generate_recommendations(
        self, profile: Dict[str, Any], quiz_results: List[Dict[str, Any]], simulation_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Recommend next modules, external courses, or specific simulation practicals.
        """
        pass

    @abstractmethod
    async def explain_simulation_output(
        self, model_name: str, parameters: Dict[str, Any], status: str, logs: str
    ) -> str:
        """
        Analyze simulation telemetry data / logs and return AI explanation of errors or behavior.
        """
        pass
