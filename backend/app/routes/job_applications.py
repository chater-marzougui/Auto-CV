"""API routes for job application tracking"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.database import crud, schemas

router = APIRouter(tags=["Job Applications"])


@router.post("/job-applications/", response_model=schemas.JobApplicationResponse)
def create_job_application(
    job_app: schemas.JobApplicationCreate,
    db: Session = Depends(get_db)
):
    """Create new job application"""
    try:
        # Verify that personal info exists
        personal_info = crud.PersonalInfoCRUD.get(db, job_app.personal_info_id)
        if not personal_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personal info not found"
            )
        
        return crud.JobApplicationCRUD.create(db, job_app)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating job application: {str(e)}"
        )


@router.get("/job-applications/", response_model=List[schemas.JobApplicationResponse])
def get_all_job_applications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all job applications"""
    try:
        return crud.JobApplicationCRUD.get_all(db, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching job applications: {str(e)}"
        )


@router.get("/job-applications/{job_app_id}", response_model=schemas.JobApplicationResponse)
def get_job_application(
    job_app_id: int,
    db: Session = Depends(get_db)
):
    """Get job application by ID"""
    try:
        job_app = crud.JobApplicationCRUD.get(db, job_app_id)
        if not job_app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found"
            )
        return job_app
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching job application: {str(e)}"
        )


@router.get("/personal-info/{personal_info_id}/job-applications", response_model=List[schemas.JobApplicationResponse])
def get_job_applications_by_personal_info(
    personal_info_id: int,
    db: Session = Depends(get_db)
):
    """Get all job applications for a specific person"""
    try:
        # Verify that personal info exists
        personal_info = crud.PersonalInfoCRUD.get(db, personal_info_id)
        if not personal_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personal info not found"
            )
        
        return crud.JobApplicationCRUD.get_by_personal_info_id(db, personal_info_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching job applications: {str(e)}"
        )


@router.put("/job-applications/{job_app_id}", response_model=schemas.JobApplicationResponse)
def update_job_application(
    job_app_id: int,
    job_app_update: schemas.JobApplicationUpdate,
    db: Session = Depends(get_db)
):
    """Update job application"""
    try:
        # Check if job application exists
        existing_app = crud.JobApplicationCRUD.get(db, job_app_id)
        if not existing_app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found"
            )
        
        updated_app = crud.JobApplicationCRUD.update(db, job_app_id, job_app_update)
        if not updated_app:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update job application"
            )
        
        return updated_app
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating job application: {str(e)}"
        )


@router.delete("/job-applications/{job_app_id}")
def delete_job_application(
    job_app_id: int,
    db: Session = Depends(get_db)
):
    """Delete job application"""
    try:
        success = crud.JobApplicationCRUD.delete(db, job_app_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found"
            )
        
        return {"message": "Job application deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting job application: {str(e)}"
        )