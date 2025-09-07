from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from pydantic import BaseModel
from app.models.project import JobDescription, MatchedProject
from app.services.embeddings import EmbeddingService
from app.services.github_scraper import GitHubScraper
from app.services.gemini_service import GeminiService
import json
import os

router = APIRouter()
class JobDescriptionInput(BaseModel):
    job_description: dict | str

class ProjectVisibilityUpdate(BaseModel):
    hidden_from_search: bool


@router.post("/match-projects", response_model=List[MatchedProject])
def match_projects_to_job(job_description: JobDescriptionInput, top_k: int = 6):
    """
    Match projects to a job description and return the most relevant ones
    """
    try:
        embedding_service = EmbeddingService()
        jd = job_description.job_description

        # If it's a dict (structured JD), merge values into one string
        if isinstance(jd, dict):
            jd_text = ", ".join(str(v) for v in jd.values() if v)
        else:
            jd_text = str(jd)

        print(f"Finding top {top_k} matching projects for the job description: {jd_text[:50]}...")
        matched_projects = embedding_service.find_matching_projects(jd_text, top_k)
        matched_projects = sorted(matched_projects, key=lambda x: x.similarity_score, reverse=True)
        
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
        
        # Only initialize embedding service if we have projects
        embedding_service = EmbeddingService()
        embedding_service.generate_embeddings_for_projects(projects)
        
        return {
            "message": f"Successfully refreshed embeddings for {len(projects)} projects"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing embeddings: {str(e)}")

@router.patch("/projects/{project_name}/visibility")
def toggle_project_visibility(project_name: str, visibility_update: ProjectVisibilityUpdate):
    """
    Toggle project visibility for similarity search
    """
    try:
        scraper = GitHubScraper()
        projects = scraper.load_projects()
        
        # Find the project
        project_index = next((i for i, p in enumerate(projects) if p.name == project_name), None)
        
        if project_index is None:
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        # Update the visibility
        projects[project_index].hidden_from_search = visibility_update.hidden_from_search
        
        # Save the updated projects
        scraper.save_projects(projects)
        
        # Refresh embeddings to exclude/include the project (only if there are visible projects)
        visible_projects = [p for p in projects if not getattr(p, 'hidden_from_search', False)]
        if visible_projects:
            embedding_service = EmbeddingService()
            embedding_service.generate_embeddings_for_projects(projects)
        
        return {
            "message": f"Project '{project_name}' visibility updated successfully",
            "hidden_from_search": visibility_update.hidden_from_search
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating project visibility: {str(e)}")

@router.post("/projects/{project_name}/update")
async def update_single_project(project_name: str, background_tasks: BackgroundTasks):
    """
    Re-scrape and update a single project
    """
    try:
        scraper = GitHubScraper()
        projects = scraper.load_projects()
        
        # Find the project
        project = next((p for p in projects if p.name == project_name), None)
        
        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        # Extract GitHub username from URL
        github_url_parts = project.url.split("/")
        if len(github_url_parts) < 5:
            raise HTTPException(status_code=400, detail="Invalid GitHub URL format")
        
        github_username = github_url_parts[-2]
        repo_name = github_url_parts[-1]
        
        # Start background task to update the single project
        background_tasks.add_task(scraper.update_single_project, github_username, repo_name)
        
        return {
            "message": f"Project '{project_name}' update started",
            "status": "processing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting project update: {str(e)}")