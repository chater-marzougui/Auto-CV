from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.database.schemas import PersonalInfoBase

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
    hidden_from_search: bool = False  # New field to hide project from similarity search
    
class JobDescription(BaseModel):
    description: str
    
class MatchedProject(BaseModel):
    project: Project
    similarity_score: float

class CVGenerationRequest(BaseModel):
    matched_projects: List[MatchedProject]
    personal_info: Optional[PersonalInfoBase] = None
    template_path: Optional[str] = None
    
class CoverLetterRequest(BaseModel):
    job_description: str
    matched_projects: List[MatchedProject]
    personal_info: PersonalInfoBase
    template_path: Optional[str] = None
    
class GenerateFullApplicationRequest(BaseModel):
    job_description: dict
    personal_info_id: Optional[int] = None
    top_k: int = 4
    selected_projects: Optional[List[MatchedProject]] = None