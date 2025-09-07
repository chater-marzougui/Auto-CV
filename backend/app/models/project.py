from pydantic import BaseModel
from typing import Dict, List, Optional, Any
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
    bad_readme: bool
    no_readme: bool
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
    job_description: str
    matched_projects: List[MatchedProject]
    personal_info: dict
    template_path: Optional[str] = None
    
class GenerateFullApplicationRequest(BaseModel):
    job_description: dict | str
    personal_info: Dict[str, Any]
    top_k: int = 4