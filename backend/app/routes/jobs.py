from fastapi import APIRouter, HTTPException
from typing import List
from app.models.project import JobDescription, MatchedProject
from app.services.embeddings import EmbeddingService
from app.services.github_scraper import GitHubScraper

router = APIRouter()

@router.post("/match-projects", response_model=List[MatchedProject])
def match_projects_to_job(job_description: JobDescription, top_k: int = 4):
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
        # Simple keyword extraction for now
        # In production, you'd want to use NLP techniques
        
        description_text = f"{job_description.description} {job_description.requirements or ''}".lower()
        
        # Common technology keywords
        tech_keywords = [
            'python', 'javascript', 'java', 'react', 'node.js', 'django', 'flask',
            'fastapi', 'sql', 'postgresql', 'mysql', 'mongodb', 'docker', 'kubernetes',
            'aws', 'azure', 'gcp', 'git', 'linux', 'html', 'css', 'typescript',
            'angular', 'vue', 'spring', 'microservices', 'rest api', 'graphql',
            'machine learning', 'data science', 'tensorflow', 'pytorch', 'pandas'
        ]
        
        found_technologies = [tech for tech in tech_keywords if tech in description_text]
        
        # Extract experience level keywords
        experience_keywords = ['junior', 'senior', 'mid-level', 'lead', 'principal', 'architect']
        experience_level = next((exp for exp in experience_keywords if exp in description_text), 'not specified')
        
        # Extract soft skills
        soft_skills = ['communication', 'teamwork', 'leadership', 'problem-solving', 'analytical']
        found_soft_skills = [skill for skill in soft_skills if skill in description_text]
        
        return {
            "job_title": job_description.title,
            "company": job_description.company,
            "required_technologies": found_technologies,
            "experience_level": experience_level,
            "soft_skills": found_soft_skills,
            "analysis_summary": f"This {experience_level} position requires experience with {', '.join(found_technologies[:5])} and emphasizes {', '.join(found_soft_skills[:3])}."
        }
        
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