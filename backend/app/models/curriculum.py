import uuid
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base_class import Base

class LearningGoal(Base):
    __tablename__ = "learning_goals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_text = Column(Text, nullable=False)
    simulation_focus = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    
    user = relationship("User", back_populates="learning_goals")
    modules = relationship("LearningModule", back_populates="learning_goal", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="learning_goal", cascade="all, delete-orphan")

class LearningModule(Base):
    __tablename__ = "learning_modules"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learning_goal_id = Column(UUID(as_uuid=True), ForeignKey("learning_goals.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String, nullable=False)  # Easy, Medium, Hard
    estimated_hours = Column(Float, default=0.0)
    order_index = Column(Integer, nullable=False)
    status = Column(String, default="NOT_STARTED")  # NOT_STARTED, IN_PROGRESS, COMPLETED
    
    learning_goal = relationship("LearningGoal", back_populates="modules")
    topics = relationship("CurriculumTopic", back_populates="module", cascade="all, delete-orphan")

class CurriculumTopic(Base):
    __tablename__ = "curriculum_topics"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id = Column(UUID(as_uuid=True), ForeignKey("learning_modules.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False)
    status = Column(String, default="NOT_STARTED")  # NOT_STARTED, IN_PROGRESS, COMPLETED
    
    module = relationship("LearningModule", back_populates="topics")
    tasks = relationship("CurriculumTask", back_populates="topic", cascade="all, delete-orphan")

class CurriculumTask(Base):
    __tablename__ = "curriculum_tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("curriculum_topics.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)  # LAB, READING, SIMULATION, QUIZ
    content = Column(Text, nullable=True)  # Markdown text or instructions
    duration_minutes = Column(Integer, default=30)
    simulation_id = Column(UUID(as_uuid=True), ForeignKey("simulations.id"), nullable=True)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=True)
    order_index = Column(Integer, nullable=False)
    status = Column(String, default="NOT_STARTED")  # NOT_STARTED, IN_PROGRESS, COMPLETED
    
    topic = relationship("CurriculumTopic", back_populates="tasks")
    simulation = relationship("Simulation", back_populates="tasks")
    quiz = relationship("Quiz", back_populates="tasks")

class Progress(Base):
    __tablename__ = "progress"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    learning_goal_id = Column(UUID(as_uuid=True), ForeignKey("learning_goals.id", ondelete="CASCADE"), nullable=False)
    percent_completed = Column(Float, default=0.0)
    time_spent_hours = Column(Float, default=0.0)
    last_accessed = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="progress_records")
    learning_goal = relationship("LearningGoal", back_populates="progress")
