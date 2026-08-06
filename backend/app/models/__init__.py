from app.database.base_class import Base
from app.models.user import User, Role, Department
from app.models.profile import UserProfile, Skill, ProfileSkill
from app.models.curriculum import LearningGoal, LearningModule, CurriculumTopic, CurriculumTask, Progress
from app.models.simulation import Simulation, SimulationHistory
from app.models.quiz import Quiz, QuizQuestion, QuizResult
from app.models.document import Document, DocumentChunk
from app.models.recommendation import Recommendation

__all__ = [
    "Base",
    "User",
    "Role",
    "Department",
    "UserProfile",
    "Skill",
    "ProfileSkill",
    "LearningGoal",
    "LearningModule",
    "CurriculumTopic",
    "CurriculumTask",
    "Progress",
    "Simulation",
    "SimulationHistory",
    "Quiz",
    "QuizQuestion",
    "QuizResult",
    "Document",
    "DocumentChunk",
    "Recommendation"
]
