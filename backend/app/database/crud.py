"""CRUD operations for database models"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import models, schemas


class PersonalInfoCRUD:
    """CRUD operations for PersonalInfo"""
    
    @staticmethod
    def get(db: Session, personal_info_id: int) -> Optional[models.PersonalInfo]:
        """Get personal info by ID"""
        return db.query(models.PersonalInfo).filter(models.PersonalInfo.id == personal_info_id).first()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[models.PersonalInfo]:
        """Get personal info by email"""
        return db.query(models.PersonalInfo).filter(models.PersonalInfo.email == email).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[models.PersonalInfo]:
        """Get all personal info records"""
        return db.query(models.PersonalInfo).offset(skip).limit(limit).all()
    
    @staticmethod
    def create(db: Session, personal_info: schemas.PersonalInfoCreate) -> models.PersonalInfo:
        """Create new personal info"""
        db_personal_info = models.PersonalInfo(**personal_info.dict())
        db.add(db_personal_info)
        db.commit()
        db.refresh(db_personal_info)
        return db_personal_info
    
    @staticmethod
    def update(db: Session, personal_info_id: int, personal_info_update: schemas.PersonalInfoUpdate) -> Optional[models.PersonalInfo]:
        """Update personal info"""
        db_personal_info = db.query(models.PersonalInfo).filter(models.PersonalInfo.id == personal_info_id).first()
        if db_personal_info:
            update_data = personal_info_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_personal_info, field, value)
            db.commit()
            db.refresh(db_personal_info)
        return db_personal_info
    
    @staticmethod
    def delete(db: Session, personal_info_id: int) -> bool:
        """Delete personal info"""
        db_personal_info = db.query(models.PersonalInfo).filter(models.PersonalInfo.id == personal_info_id).first()
        if db_personal_info:
            db.delete(db_personal_info)
            db.commit()
            return True
        return False


class JobApplicationCRUD:
    """CRUD operations for JobApplication"""
    
    @staticmethod
    def get(db: Session, job_app_id: int) -> Optional[models.JobApplication]:
        """Get job application by ID"""
        return db.query(models.JobApplication).filter(models.JobApplication.id == job_app_id).first()
    
    @staticmethod
    def get_by_personal_info_id(db: Session, personal_info_id: int) -> List[models.JobApplication]:
        """Get job applications by personal info ID"""
        return db.query(models.JobApplication).filter(
            models.JobApplication.personal_info_id == personal_info_id
        ).order_by(desc(models.JobApplication.application_date)).all()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[models.JobApplication]:
        """Get all job applications"""
        return db.query(models.JobApplication).order_by(desc(models.JobApplication.application_date)).offset(skip).limit(limit).all()
    
    @staticmethod
    def create(db: Session, job_app: schemas.JobApplicationCreate) -> models.JobApplication:
        """Create new job application"""
        db_job_app = models.JobApplication(**job_app.dict())
        db.add(db_job_app)
        db.commit()
        db.refresh(db_job_app)
        return db_job_app
    
    @staticmethod
    def update(db: Session, job_app_id: int, job_app_update: schemas.JobApplicationUpdate) -> Optional[models.JobApplication]:
        """Update job application"""
        db_job_app = db.query(models.JobApplication).filter(models.JobApplication.id == job_app_id).first()
        if db_job_app:
            update_data = job_app_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_job_app, field, value)
            db.commit()
            db.refresh(db_job_app)
        return db_job_app
    
    @staticmethod
    def update_file_paths(db: Session, job_app_id: int, cv_path: Optional[str] = None, 
                         cover_letter_path: Optional[str] = None, cv_url: Optional[str] = None,
                         cover_letter_url: Optional[str] = None, matched_projects: Optional[List] = None) -> Optional[models.JobApplication]:
        """Update file paths and URLs for generated documents"""
        db_job_app = db.query(models.JobApplication).filter(models.JobApplication.id == job_app_id).first()
        if db_job_app:
            if cv_path:
                db_job_app.cv_file_path = cv_path
            if cover_letter_path:
                db_job_app.cover_letter_file_path = cover_letter_path
            if cv_url:
                db_job_app.cv_download_url = cv_url
            if cover_letter_url:
                db_job_app.cover_letter_download_url = cover_letter_url
            if matched_projects:
                db_job_app.matched_projects = matched_projects
            db.commit()
            db.refresh(db_job_app)
        return db_job_app
    
    @staticmethod
    def delete(db: Session, job_app_id: int) -> bool:
        """Delete job application"""
        db_job_app = db.query(models.JobApplication).filter(models.JobApplication.id == job_app_id).first()
        if db_job_app:
            db.delete(db_job_app)
            db.commit()
            return True
        return False