import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class ProfileSkill(Base):
    __tablename__ = "profile_skills"
    profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    level = Column(Integer, default=1)  # Skill level (e.g. 1 to 5)

    profile = relationship("UserProfile", back_populates="skills_association")
    skill = relationship("Skill", back_populates="profiles_association")

class Skill(Base):
    __tablename__ = "skills"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True, index=True)
    category = Column(String, nullable=False)  # Control Systems, Backend Development, CAN/ECU, etc.
    
    profiles_association = relationship("ProfileSkill", back_populates="skill", cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    experience_years = Column(Integer, default=0)
    learning_history = Column(JSON, default=dict)  # Stores completed courses, certifications, general milestones
    
    user = relationship("User", back_populates="profile")
    department = relationship("Department", back_populates="profiles")
    skills_association = relationship("ProfileSkill", back_populates="profile", cascade="all, delete-orphan")
