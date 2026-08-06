import uuid
from sqlalchemy import Column, String, Float, ForeignKey, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base_class import Base

class Simulation(Base):
    __tablename__ = "simulations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)  # PID Control, CAN Bus, ECU Engine
    model_file = Column(String, nullable=False, unique=True)  # pid_model.slx, can_model.slx, ecu_model.slx
    description = Column(Text, nullable=True)
    
    tasks = relationship("CurriculumTask", back_populates="simulation")
    history = relationship("SimulationHistory", back_populates="simulation", cascade="all, delete-orphan")

class SimulationHistory(Base):
    __tablename__ = "simulation_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    simulation_id = Column(UUID(as_uuid=True), ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False)
    parameters = Column(JSON, default=dict)  # Input signal parameters: { "Kp": 2.5, "Ki": 0.1 }
    status = Column(String, default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED
    logs = Column(Text, nullable=True)  # Raw terminal or MATLAB output logs
    result_images = Column(JSON, default=list)  # SVG/PNG paths for visual outputs/graphs
    execution_time_seconds = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="simulation_history")
    simulation = relationship("Simulation", back_populates="history")
