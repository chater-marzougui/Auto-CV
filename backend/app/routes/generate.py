from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
from app.models.project import CVGenerationRequest, CoverLetterRequest, GenerateFullApplicationRequest
from app.services.cv_generator import CVGenerator
from app.services.letter_generator import CoverLetterGenerator
from app.services.embeddings import EmbeddingService
from app.database.database import get_db
from app.database import crud, schemas
from app.database.schemas import PersonalInfoBase
from datetime import datetime

router = APIRouter()

# Global websocket manager - will be set from main.py
websocket_manager = None

async def send_websocket_progress(client_id: str, message: str, step: str, current: int = 0, total: int = 0):
    """Helper function to send websocket progress updates"""
    if websocket_manager and client_id:
        progress_data = {
            "type": "progress",
            "message": message,
            "step": step,
            "current": current,
            "total": total,
            "repo_name": "",
            "timestamp": datetime.now().isoformat(),
        }
        await websocket_manager.send_progress(client_id, progress_data)

@router.post("/generate-cv")
def generate_cv(request: CVGenerationRequest):
    """
    Generate a CV PDF based on matched projects and personal information
    """
    try:
        cv_generator = CVGenerator()
        
        # Generate CV
        pdf_path = cv_generator.generate_cv(request)
        
        return {
            "message": "CV generated successfully",
            "pdf_path": pdf_path,
            "download_url": f"/api/v1/download/{os.path.basename(pdf_path)}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating CV: {str(e)}")

@router.post("/generate-cover-letter")
def generate_cover_letter(request: CoverLetterRequest):
    """
    Generate a cover letter PDF based on job description and matched projects
    """
    try:
        letter_generator = CoverLetterGenerator()
        
        # Generate cover letter
        pdf_path = letter_generator.generate_cover_letter(request)
        
        return {
            "message": "Cover letter generated successfully",
            "pdf_path": pdf_path,
            "download_url": f"/api/v1/download/{os.path.basename(pdf_path)}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cover letter: {str(e)}")

@router.post("/generate-full-application")
async def generate_full_application(request: GenerateFullApplicationRequest, db: Session = Depends(get_db)):
    """
    Generate both CV and cover letter for a complete job application
    """
    if not request.personal_info_id:
        raise HTTPException(status_code=400, detail="Personal Info ID is required")
    
    try:
        client_id = request.client_id
        
        # Send websocket update
        if client_id:
            await send_websocket_progress(
                client_id, 
                "Starting application generation...", 
                "initializing", 
                0, 
                5
            )
        
        # Get personal info from database
        personal_info_sql = crud.PersonalInfoCRUD.get(db, request.personal_info_id)
        if not personal_info_sql:
            if client_id:
                await send_websocket_progress(
                    client_id, 
                    "Personal info not found in database", 
                    "error", 
                    0, 
                    5
                )
            raise HTTPException(status_code=404, detail="Personal info not found in database")

        personal_info_data = PersonalInfoBase.model_validate(personal_info_sql)

        if client_id:
            await send_websocket_progress(
                client_id, 
                "Personal information loaded successfully", 
                "processing", 
                1, 
                5
            )

        # Step 1: Get matching projects (use selected projects if provided, otherwise find them)
        if request.selected_projects:
            matched_projects = request.selected_projects
            if client_id:
                await send_websocket_progress(
                    client_id, 
                    f"Using {len(matched_projects)} selected projects", 
                    "processing", 
                    2, 
                    5
                )
        else:
            if client_id:
                await send_websocket_progress(
                    client_id, 
                    "Finding matching projects...", 
                    "matching", 
                    1, 
                    5
                )
            embedding_service = EmbeddingService()
            jd = request.job_description
            if isinstance(jd, dict):
                job_description = ", ".join(str(v) for v in jd.values() if v)
            else:
                job_description = str(jd)
            matched_projects = embedding_service.find_matching_projects(job_description, request.top_k)
            
            if client_id:
                await send_websocket_progress(
                    client_id, 
                    f"Found {len(matched_projects)} matching projects", 
                    "processing", 
                    2, 
                    5
                )
        
        if not matched_projects:
            if client_id:
                await send_websocket_progress(
                    client_id, 
                    "No matching projects found", 
                    "error", 
                    0, 
                    5
                )
            raise HTTPException(
                status_code=404,
                detail="No matching projects found. Please scrape GitHub repositories first."
            )
        
        # Prepare job description for cover letter
        jd = request.job_description
        if isinstance(jd, dict):
            job_description = ", ".join(str(v) for v in jd.values() if v)
            job_title = jd.get("title", "Unknown Position")
            company_name = jd.get("company", "Unknown Company")
            job_desc_text = jd.get("description", "")
            job_requirements = jd.get("requirements", "")
        
        # Step 2: Create job application record if personal_info_id is provided
        job_app_id = None
        if request.personal_info_id:
            job_app_create = schemas.JobApplicationCreate(
                personal_info_id=request.personal_info_id,
                job_title=job_title,
                company_name=company_name,
                job_description=job_desc_text,
                job_requirements=job_requirements
            )
            job_app = crud.JobApplicationCRUD.create(db, job_app_create)
            job_app_id = job_app.id
        
        # Step 3: Generate CV
        if client_id:
            await send_websocket_progress(
                client_id, 
                "Generating CV...", 
                "cv_generation", 
                3, 
                5
            )
            
        cv_request = CVGenerationRequest(
            matched_projects=matched_projects,
            personal_info=personal_info_data
        )
        
        cv_generator = CVGenerator()
        cv_path = cv_generator.generate_cv(cv_request)
        
        if client_id:
            await send_websocket_progress(
                client_id, 
                "CV generated successfully", 
                "processing", 
                4, 
                5
            )
        
        # Step 4: Generate Cover Letter
        if client_id:
            await send_websocket_progress(
                client_id, 
                "Generating cover letter...", 
                "cover_letter_generation", 
                4, 
                5
            )
            
        print("Generating cover letter...")
        letter_request = CoverLetterRequest(
            job_description=job_description,
            matched_projects=matched_projects,
            personal_info=personal_info_data
        )
        
        letter_generator = CoverLetterGenerator()
        letter_path = letter_generator.generate_cover_letter(letter_request)
        
        # Step 5: Update job application with file paths if we created one
        if job_app_id:
            cv_download_url = f"/api/v1/download/{os.path.basename(cv_path)}"
            letter_download_url = f"/api/v1/download/{os.path.basename(letter_path)}"
            
            # Serialize matched projects for storage
            matched_projects_data = [
                {
                    "name": mp.project.name,
                    "similarity_score": mp.similarity_score,
                    "url": mp.project.url,
                    "description": mp.project.description,
                    "three_liner": mp.project.three_liner,
                    "technologies": mp.project.technologies
                } for mp in matched_projects
            ]
            
            crud.JobApplicationCRUD.update_file_paths(
                db, job_app_id, cv_path, letter_path, 
                cv_download_url, letter_download_url,
                matched_projects_data
            )
        
        if client_id:
            await send_websocket_progress(
                client_id, 
                "Application generated successfully!", 
                "completed", 
                5, 
                5
            )
        
        return {
            "message": "Full application generated successfully",
            "job_application_id": job_app_id,
            "cv": {
                "path": cv_path,
                "download_url": f"/api/v1/download/{os.path.basename(cv_path)}"
            },
            "cover_letter": {
                "path": letter_path,
                "download_url": f"/api/v1/download/{os.path.basename(letter_path)}"
            },
            "matched_projects": [
                {
                    "name": mp.project.name,
                    "similarity_score": mp.similarity_score,
                } for mp in matched_projects
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if hasattr(request, 'client_id') and request.client_id:
            await send_websocket_progress(
                request.client_id, 
                f"Error generating application: {str(e)}", 
                "error", 
                0, 
                5
            )
        raise HTTPException(status_code=500, detail=f"Error generating full application: {str(e)}")

@router.get("/download/{filename}")
def download_file(filename: str):
    """
    Download generated PDF files
    """
    try:
        file_path = os.path.join("output", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/pdf'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

@router.post("/upload-cv-template")
def upload_cv_template(file: UploadFile = File(...)):
    """
    Upload a custom CV template
    """
    try:
        if not file.filename.endswith('.tex'):
            raise HTTPException(status_code=400, detail="Only .tex files are allowed")
        
        template_path = os.path.join("templates", file.filename)
        
        with open(template_path, "wb") as buffer:
            content = file.read()
            buffer.write(content)
        
        return {
            "message": "Template uploaded successfully",
            "template_path": template_path,
            "filename": file.filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading template: {str(e)}")

@router.post("/upload-cover-letter-template")
def upload_cover_letter_template(file: UploadFile = File(...)):
    """
    Upload a custom cover letter template
    """
    try:
        if not file.filename.endswith('.tex'):
            raise HTTPException(status_code=400, detail="Only .tex files are allowed")
        
        template_path = os.path.join("templates", file.filename)
        
        with open(template_path, "wb") as buffer:
            content = file.read()
            buffer.write(content)
        
        return {
            "message": "Cover letter template uploaded successfully",
            "template_path": template_path,
            "filename": file.filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading template: {str(e)}")

@router.get("/templates")
def list_templates():
    """
    List available templates
    """
    try:
        templates_dir = "templates"
        
        if not os.path.exists(templates_dir):
            return {"cv_templates": [], "cover_letter_templates": []}
        
        files = os.listdir(templates_dir)
        tex_files = [f for f in files if f.endswith('.tex')]
        
        cv_templates = [f for f in tex_files if 'cv' in f.lower()]
        letter_templates = [f for f in tex_files if 'cover' in f.lower() or 'letter' in f.lower()]
        
        return {
            "cv_templates": cv_templates,
            "cover_letter_templates": letter_templates,
            "all_templates": tex_files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing templates: {str(e)}")

@router.delete("/output/{filename}")
def delete_output_file(filename: str):
    """
    Delete generated files from output directory
    """
    try:
        file_path = os.path.join("output", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        os.remove(file_path)
        
        return {"message": f"File {filename} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@router.get("/output")
def list_output_files():
    """
    List all generated files in output directory
    """
    try:
        output_dir = "output"
        
        if not os.path.exists(output_dir):
            return {"files": []}
        
        files = os.listdir(output_dir)
        pdf_files = [f for f in files if f.endswith('.pdf')]
        
        file_info = []
        for filename in pdf_files:
            file_path = os.path.join(output_dir, filename)
            file_stats = os.stat(file_path)
            
            file_info.append({
                "filename": filename,
                "size_bytes": file_stats.st_size,
                "created_at": file_stats.st_ctime,
                "download_url": f"/api/v1/download/{filename}"
            })
        
        return {"files": file_info}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing output files: {str(e)}")