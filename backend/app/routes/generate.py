from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from typing import Dict, Any
import os
from pydantic import BaseModel
from app.models.project import CVGenerationRequest, CoverLetterRequest, GenerateFullApplicationRequest
from app.services.cv_generator import CVGenerator
from app.services.letter_generator import CoverLetterGenerator
from app.services.embeddings import EmbeddingService

router = APIRouter()

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
def generate_full_application(request: GenerateFullApplicationRequest):
    """
    Generate both CV and cover letter for a complete job application
    """
    try:
        # Step 1: Find matching projects
        embedding_service = EmbeddingService()
        jd = request.job_description
        if isinstance(jd, dict):
            job_description = ", ".join(str(v) for v in jd.values() if v)
        else:
            job_description = str(jd)
        matched_projects = embedding_service.find_matching_projects(job_description, request.top_k)
        
        if not matched_projects:
            raise HTTPException(
                status_code=404,
                detail="No matching projects found. Please scrape GitHub repositories first."
            )
        
        # Step 2: Generate CV
        cv_request = CVGenerationRequest(
            matched_projects=matched_projects,
            personal_info=request.personal_info
        )
        
        cv_generator = CVGenerator()
        cv_path = cv_generator.generate_cv(cv_request)
        print("CV generated at:", cv_path)
        
        # Step 3: Generate Cover Letter
        letter_request = CoverLetterRequest(
            job_description=job_description,
            matched_projects=matched_projects,
            personal_info=request.personal_info
        )
        
        letter_generator = CoverLetterGenerator()
        print("Before ")
        letter_path = letter_generator.generate_cover_letter(letter_request)
        print("Cover letter generated at:", letter_path)
        return {
            "message": "Full application generated successfully",
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