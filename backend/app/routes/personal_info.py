"""API routes for personal information management"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.database import crud, schemas

router = APIRouter(tags=["Personal Information"])


@router.post("/personal-info/", response_model=schemas.PersonalInfoResponse)
def create_personal_info(
    personal_info: schemas.PersonalInfoCreate,
    db: Session = Depends(get_db)
):
    """Create new personal information"""
    try:
        # Check if email already exists
        existing_info = crud.PersonalInfoCRUD.get_by_email(db, personal_info.email)
        if existing_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        return crud.PersonalInfoCRUD.create(db, personal_info)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating personal info: {str(e)}"
        )


@router.get("/personal-info/", response_model=List[schemas.PersonalInfoResponse])
def get_all_personal_info(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all personal information records"""
    try:
        return crud.PersonalInfoCRUD.get_all(db, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching personal info: {str(e)}"
        )


@router.get("/personal-info/{personal_info_id}", response_model=schemas.PersonalInfoResponse)
def get_personal_info(
    personal_info_id: int,
    db: Session = Depends(get_db)
):
    """Get personal information by ID"""
    try:
        personal_info = crud.PersonalInfoCRUD.get(db, personal_info_id)
        if not personal_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personal info not found"
            )
        return personal_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching personal info: {str(e)}"
        )


@router.put("/personal-info/{personal_info_id}", response_model=schemas.PersonalInfoResponse)
def update_personal_info(
    personal_info_id: int,
    personal_info_update: schemas.PersonalInfoUpdate,
    db: Session = Depends(get_db)
):
    """Update personal information"""
    try:
        # Check if personal info exists
        existing_info = crud.PersonalInfoCRUD.get(db, personal_info_id)
        if not existing_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personal info not found"
            )
        
        # If email is being updated, check if new email is already in use
        if personal_info_update.email and personal_info_update.email != existing_info.email:
            email_exists = crud.PersonalInfoCRUD.get_by_email(db, personal_info_update.email)
            if email_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        updated_info = crud.PersonalInfoCRUD.update(db, personal_info_id, personal_info_update)
        if not updated_info:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update personal info"
            )
        
        return updated_info
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating personal info: {str(e)}"
        )


@router.delete("/personal-info/{personal_info_id}")
def delete_personal_info(
    personal_info_id: int,
    db: Session = Depends(get_db)
):
    """Delete personal information"""
    try:
        success = crud.PersonalInfoCRUD.delete(db, personal_info_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personal info not found"
            )
        
        return {"message": "Personal info deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting personal info: {str(e)}"
        )


@router.get("/personal-info/email/{email}", response_model=schemas.PersonalInfoResponse)
def get_personal_info_by_email(
    email: str,
    db: Session = Depends(get_db)
):
    """Get personal information by email"""
    try:
        personal_info = crud.PersonalInfoCRUD.get_by_email(db, email)
        if not personal_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personal info not found for this email"
            )
        return personal_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching personal info: {str(e)}"
        )