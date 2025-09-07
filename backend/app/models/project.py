from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Project(BaseModel):
    name: str
    url: str
    description: str  # Original GitHub description
    readme_content: str  # Full README content
    three_liner: str  # AI-generated 3-line summary
    detailed_paragraph: str  # AI-generated detailed paragraph
    technologies: List[str]  # Extracted technologies
    tree: List[str]
    stars: int
    forks: int
    language: str
    created_at: datetime
    updated_at: datetime
    
class JobDescription(BaseModel):
    title: str
    company: str
    description: str
    requirements: Optional[str] = None
    
class MatchedProject(BaseModel):
    project: Project
    similarity_score: float

class CVGenerationRequest(BaseModel):
    matched_projects: List[MatchedProject]
    personal_info: dict
    template_path: Optional[str] = None
    
class CoverLetterRequest(BaseModel):
    job_description: JobDescription
    matched_projects: List[MatchedProject]
    personal_info: dict
    template_path: Optional[str] = None