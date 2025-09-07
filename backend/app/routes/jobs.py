from fastapi import APIRouter, HTTPException
from typing import List
from app.models.project import JobDescription, MatchedProject
from app.services.embeddings import EmbeddingService
from app.services.github_scraper import GitHubScraper
from app.services.gemini_service import GeminiService

router = APIRouter()

@router.post("/match-projects", response_model=List[MatchedProject])
def match_projects_to_job(job_description: str, top_k: int = 4):
    """
    Match projects to a job description and return the most relevant ones
    """
    try:
        embedding_service = EmbeddingService()
        matched_projects = embedding_service.find_matching_projects(job_description, top_k)
        
        if not matched_projects:
            raise HTTPException(
                status_code=404, 
                detail="No matching projects found. Please scrape GitHub repositories first."
            )
        
        return matched_projects
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error matching projects: {str(e)}")

@router.get("/projects")
def get_all_projects():
    """
    Get all scraped projects
    """
    try:
        scraper = GitHubScraper()
        projects = scraper.load_projects()
        
        return {
            "total_projects": len(projects),
            "projects": projects
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading projects: {str(e)}")

@router.get("/projects/{project_name}")
def get_project_details(project_name: str):
    """
    Get details for a specific project
    """
    try:
        scraper = GitHubScraper()
        projects = scraper.load_projects()
        
        project = next((p for p in projects if p.name == project_name), None)
        
        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        return project
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading project: {str(e)}")

@router.post("/analyze-job")
def analyze_job_description(job_description: JobDescription):
    """
    Analyze a job description and extract key requirements/technologies
    """
    try:
        gemini_service = GeminiService()
        analysis = gemini_service.job_description_parser(job_description.description)
        
        if not analysis:
            raise HTTPException(status_code=500, detail="Failed to analyze job description")

        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing job description: {str(e)}")

@router.post("/refresh-embeddings")
def refresh_embeddings():
    """
    Refresh embeddings for all projects (useful after adding new projects)
    """
    try:
        scraper = GitHubScraper()
        projects = scraper.load_projects()
        
        if not projects:
            raise HTTPException(status_code=404, detail="No projects found. Please scrape GitHub repositories first.")
        
        embedding_service = EmbeddingService()
        embedding_service.generate_embeddings_for_projects(projects)
        
        return {
            "message": f"Successfully refreshed embeddings for {len(projects)} projects"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing embeddings: {str(e)}")