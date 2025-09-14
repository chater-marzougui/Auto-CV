"""Database models for personal info and job applications"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class PersonalInfo(Base):
    """Personal information model"""
    __tablename__ = "personal_info"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(50))
    address = Column(String(255))
    city = Column(String(100))
    postal_code = Column(String(20))
    title = Column(String(200))
    summary = Column(Text)
    skills = Column(JSON)  # Store skills as JSON
    experience = Column(JSON)  # Store experience as JSON
    education = Column(JSON)  # Store education as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to job applications
    job_applications = relationship("JobApplication", back_populates="personal_info")


class JobApplication(Base):
    """Job application tracking model"""
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    personal_info_id = Column(Integer, ForeignKey("personal_info.id"))
    job_title = Column(String(200), nullable=False)
    company_name = Column(String(200), nullable=False)
    job_description = Column(Text)
    job_requirements = Column(Text)
    cv_file_path = Column(String(500))
    cover_letter_file_path = Column(String(500))
    cv_download_url = Column(String(500))
    cover_letter_download_url = Column(String(500))
    matched_projects = Column(JSON)  # Store matched projects as JSON
    application_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="applied")  # applied, interview, rejected, accepted
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to personal info
    personal_info = relationship("PersonalInfo", back_populates="job_applications")