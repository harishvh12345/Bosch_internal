import uuid
from sqlalchemy import Column, String, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base_class import Base

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rec_type = Column(String, nullable=False)  # MODULE, COURSE, SIMULATION
    reference_id = Column(UUID(as_uuid=True), nullable=True)  # ID of module, course, or simulation
    title = Column(String, nullable=False)
    reasoning = Column(Text, nullable=False)  # Gemini explanation why this was recommended
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="recommendations")
