"""Pydantic schemas for API request/response models"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr


class PersonalInfoBase(BaseModel):
    """Base personal info schema"""
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[Dict[str, List[str]]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None


class PersonalInfoCreate(PersonalInfoBase):
    """Schema for creating personal info"""
    pass


class PersonalInfoUpdate(BaseModel):
    """Schema for updating personal info"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[Dict[str, List[str]]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None


class PersonalInfoResponse(PersonalInfoBase):
    """Schema for personal info response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobApplicationBase(BaseModel):
    """Base job application schema"""
    job_title: str
    company_name: str
    job_description: Optional[str] = None
    job_requirements: Optional[str] = None
    status: Optional[str] = "applied"
    notes: Optional[str] = None


class JobApplicationCreate(JobApplicationBase):
    """Schema for creating job application"""
    personal_info_id: int


class JobApplicationUpdate(BaseModel):
    """Schema for updating job application"""
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_description: Optional[str] = None
    job_requirements: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class JobApplicationResponse(JobApplicationBase):
    """Schema for job application response"""
    id: int
    personal_info_id: int
    cv_file_path: Optional[str] = None
    cover_letter_file_path: Optional[str] = None
    cv_download_url: Optional[str] = None
    cover_letter_download_url: Optional[str] = None
    matched_projects: Optional[List[Dict[str, Any]]] = None
    application_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True