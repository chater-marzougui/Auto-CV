import os
import pickle
import re
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import faiss
from datetime import datetime, timezone
from app.models.project import Project, MatchedProject
from app.services.gemini_service import GeminiService

class EmbeddingService:
    def __init__(self):
        """
        Initialize embedding service with enhanced matching capabilities
        """
        self.model_name = "sentence-transformers/all-mpnet-base-v2"  # Better general performance
        self.model = SentenceTransformer(self.model_name)
        self.data_dir = "app/data"
        self.embeddings_file = os.path.join(self.data_dir, "embeddings.pkl")
        self.index_file = os.path.join(self.data_dir, "faiss_index.bin")
        
        # Initialize Gemini service for enhanced job description processing
        try:
            self.gemini_service = GeminiService()
        except Exception as e:
            print(f"Warning: Could not initialize Gemini service: {e}")
            print("Falling back to regex-based technology extraction")
            self.gemini_service = None
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize or load FAISS index
        self.index = None
        self.project_mapping = {}
        self.embeddings_cache = {}
        
        # Technology normalization mapping
        self.tech_normalize = {
            'react.js': 'react', 'reactjs': 'react', 'react js': 'react',
            'node.js': 'nodejs', 'node js': 'nodejs',
            'vue.js': 'vue', 'vuejs': 'vue',
            'angular.js': 'angular', 'angularjs': 'angular',
            'javascript': 'js', 'typescript': 'ts',
            'python3': 'python', 'py': 'python',
            'postgresql': 'postgres', 'postgressql': 'postgres',
            'mongodb': 'mongo', 'mongoose': 'mongo',
            'express.js': 'express', 'expressjs': 'express',
            'next.js': 'nextjs', 'nuxt.js': 'nuxtjs'
        }
    
    def _normalize_technologies(self, technologies: List[str]) -> List[str]:
        """Normalize technology names for better matching"""
        normalized = []
        for tech in technologies:
            tech_lower = tech.lower().strip()
            normalized_tech = self.tech_normalize.get(tech_lower, tech_lower)
            if normalized_tech and normalized_tech not in normalized:
                normalized.append(normalized_tech)
        return normalized
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text for better embedding"""
        if not text:
            return ""
        
        # Remove markdown formatting
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # Remove images
        text = re.sub(r'\[.*?\]\(.*?\)', '', text)   # Remove links
        text = re.sub(r'`{1,3}.*?`{1,3}', '', text, flags=re.DOTALL)  # Remove code blocks
        text = re.sub(r'#{1,6}\s+', '', text)       # Remove headers
        text = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', text)  # Remove bold/italic
        
        # Clean whitespace and normalize
        text = ' '.join(text.split())
        return text
    
    def _create_weighted_text(self, project: Project) -> str:
        """Create a weighted text representation focusing on key aspects"""
        components = []
        
        # Core description (high weight)
        if project.detailed_paragraph:
            clean_desc = self._clean_text(project.detailed_paragraph)
            components.extend([clean_desc] * 3)  # 3x weight
        
        # Technologies (very high weight for exact matching)
        if project.technologies:
            normalized_techs = self._normalize_technologies(project.technologies)
            tech_text = f"Technologies used: {' '.join(normalized_techs)}"
            components.extend([tech_text] * 4)  # 4x weight
        
        # Three-liner summary (medium weight)
        if project.three_liner:
            clean_summary = self._clean_text(project.three_liner)
            components.extend([clean_summary] * 2)  # 2x weight
        
        # Repository description (low weight)
        if project.description and project.description != "No description provided":
            clean_repo_desc = self._clean_text(project.description)
            components.append(clean_repo_desc)  # 1x weight
        
        # Primary language (medium weight)
        if project.language and project.language != "Unknown":
            lang_text = f"Primary language: {project.language.lower()}"
            components.extend([lang_text] * 2)  # 2x weight
        
        return " ".join(components)
    
    def _calculate_recency_score(self, project: Project) -> float:
        """Calculate recency score (0-1, where 1 is most recent)"""
        if not project.created_at:
            return 0.5  # Neutral score if date unknown
        
        now = datetime.now(timezone.utc)
        if project.created_at.tzinfo is None:
            project_date = project.created_at.replace(tzinfo=timezone.utc)
        else:
            project_date = project.created_at
        
        days_old = (now - project_date).days
        
        if days_old <= 30:
            return 1.0
        elif days_old <= 90:
            return 0.9
        elif days_old <= 180:
            return 0.8
        elif days_old <= 365:
            return 0.6
        elif days_old <= 730:  # 2 years
            return 0.4
        else:
            return 0.2
    
    def _calculate_quality_score(self, project: Project) -> float:
        """Calculate project quality score based on various indicators"""
        score = 1.0
        
        # README quality penalties
        if project.no_readme:
            score *= 0.5  # Heavy penalty
        elif project.bad_readme:
            score *= 0.8  # Moderate penalty
        
        # GitHub engagement bonuses
        if project.stars > 10:
            score *= 1.2
        elif project.stars > 50:
            score *= 1.4
        elif project.stars > 100:
            score *= 1.6
        
        if project.forks > 5:
            score *= 1.1
        elif project.forks > 20:
            score *= 1.3
        
        # Technology diversity bonus
        if len(project.technologies) > 3:
            score *= 1.1
        elif len(project.technologies) > 6:
            score *= 1.2
        
        return min(score, 2.0)  # Cap at 2.0
    
    def generate_embeddings_for_projects(self, projects: List[Project]):
        """Generate enhanced embeddings for all projects (excluding hidden ones)"""
        # Filter out hidden projects
        visible_projects = [p for p in projects if not getattr(p, 'hidden_from_search', False)]
        
        # Prepare enhanced texts for embedding
        project_texts = []
        project_names = []
        
        for project in visible_projects:
            weighted_text = self._create_weighted_text(project)
            project_texts.append(weighted_text)
            project_names.append(project.name)
        
        if not project_texts:
            print("No visible projects to generate embeddings for")
            return
        
        # Generate embeddings
        embeddings = self.model.encode(project_texts, convert_to_tensor=False)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add embeddings to index
        self.index.add(embeddings.astype('float32'))
        
        # Create mapping
        self.project_mapping = dict(enumerate(project_names))
        
        # Cache embeddings and projects with additional metadata
        self.embeddings_cache = {
            'embeddings': embeddings,
            'projects': {project.name: project for project in visible_projects},
            'project_names': project_names,
            'recency_scores': {project.name: self._calculate_recency_score(project) for project in visible_projects},
            'quality_scores': {project.name: self._calculate_quality_score(project) for project in visible_projects}
        }
        
        # Save to disk
        self._save_embeddings()
        
        print(f"Successfully generated and saved enhanced embeddings for {len(projects)} projects")
    
    def _extract_job_information_with_gemini(self, job_description: str) -> Dict:
        """Extract comprehensive job information using Gemini AI"""
        try:
            return self.gemini_service.extract_job_description_for_embeddings(job_description)
        except Exception as e:
            print(f"Error using Gemini for job extraction: {e}")
            return {
                'core_technologies': [],
                'secondary_technologies': [],
                'technical_keywords': [],
                'experience_level': 'Not specified',
                'domain_context': '',
                'key_responsibilities': [],
                'soft_skills': [],
                'weighted_description': job_description
            }
            
    def _calculate_technology_overlap_score(self, project_techs: List[str], job_techs: List[str]) -> float:
        """Calculate technology overlap score between project and job"""
        if not job_techs or not project_techs:
            return 0.0
        
        project_techs_norm = set(self._normalize_technologies(project_techs))
        job_techs_norm = set(job_techs)
        
        overlap = len(project_techs_norm.intersection(job_techs_norm))
        total_job_techs = len(job_techs_norm)
        
        if total_job_techs == 0:
            return 0.0
        
        # Calculate overlap percentage with bonus for exact matches
        overlap_score = overlap / total_job_techs
        
        # Bonus for having more technologies than required
        if overlap > 0 and len(project_techs_norm) >= total_job_techs:
            overlap_score *= 1.2
        
        return min(overlap_score, 1.5)  # Cap at 1.5 for exceptional matches
    
    def find_matching_projects(self, job_description: str, top_k: int = 4) -> List[MatchedProject]:
        """Enhanced project matching with AI-powered job analysis and multi-factor scoring"""
        try:
            # Load embeddings if not in memory
            if not self.index or not self.embeddings_cache:
                self._load_embeddings()
            
            if not self.index:
                raise RuntimeError("No embeddings found. Please scrape GitHub repositories first.")
            
            # Extract comprehensive job information using Gemini
            job_info = self._extract_job_information_with_gemini(job_description)
            
            # Combine all technologies for matching
            all_job_technologies = (
                job_info.get('core_technologies', []) + 
                job_info.get('secondary_technologies', [])
            )
            all_job_technologies = self._normalize_technologies(all_job_technologies)
            
            # Create enhanced job description for embedding using Gemini's weighted description
            weighted_desc = job_info.get('weighted_description', job_description)
            technical_keywords = ' '.join(job_info.get('technical_keywords', []))
            domain_context = job_info.get('domain_context', '')
            
            # Enhanced job text for better semantic matching
            job_text_components = [
                weighted_desc,
                f"Required technologies: {' '.join(job_info.get('core_technologies', []))}",
                f"Technical skills: {technical_keywords}",
                f"Domain: {domain_context}"
            ]
            job_text = ' '.join([comp for comp in job_text_components if comp.strip()])
            
            # Generate embedding for job description
            job_embedding = self.model.encode([job_text], convert_to_tensor=False)
            faiss.normalize_L2(job_embedding)
            
            # Search for similar projects (get more than needed for filtering)
            search_k = min(top_k * 3, len(self.project_mapping))
            scores, indices = self.index.search(job_embedding.astype('float32'), search_k)
            
            candidate_projects = []
            
            for i, (semantic_score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx == -1:  # No more results
                    break
                
                project_name = self.project_mapping[idx]
                project = self.embeddings_cache['projects'][project_name]
                
                # Skip hidden projects
                if getattr(project, 'hidden_from_search', False):
                    continue
                
                # Calculate component scores
                recency_score = self.embeddings_cache['recency_scores'][project_name]
                quality_score = self.embeddings_cache['quality_scores'][project_name]
                
                # Enhanced technology overlap scoring with core vs secondary weighting
                core_tech_overlap = self._calculate_technology_overlap_score(
                    project.technologies, job_info.get('core_technologies', [])
                )
                secondary_tech_overlap = self._calculate_technology_overlap_score(
                    project.technologies, job_info.get('secondary_technologies', [])
                )
                
                # Weighted technology score (core techs are more important)
                tech_overlap_score = (core_tech_overlap * 0.8 + secondary_tech_overlap * 0.2)
                
                # Enhanced scoring formula with improved weights
                # Weights: semantic(0.35) + tech_overlap(0.4) + recency(0.15) + quality(0.1)
                final_score = (
                    float(semantic_score) * 0.35 +
                    tech_overlap_score * 0.4 +
                    recency_score * 0.15 +
                    quality_score * 0.1
                )
                
                # Additional bonuses/penalties
                if project.no_readme:
                    final_score *= 0.5  # Significant penalty
                elif project.bad_readme:
                    final_score *= 0.7  # Moderate penalty
                
                # Enhanced bonus system
                if core_tech_overlap > 0.6:  # Strong core technology match
                    final_score *= 1.3
                elif core_tech_overlap > 0.3:  # Moderate core technology match
                    final_score *= 1.15
                
                # Domain relevance bonus (if available)
                domain_context = job_info.get('domain_context', '').lower()
                if domain_context and any(keyword in project.detailed_paragraph.lower() 
                                        for keyword in domain_context.split() if len(keyword) > 3):
                    final_score *= 1.1
                
                candidate_projects.append({
                    'project': project,
                    'final_score': final_score,
                    'semantic_score': float(semantic_score),
                    'tech_overlap_score': tech_overlap_score,
                    'core_tech_overlap': core_tech_overlap,
                    'secondary_tech_overlap': secondary_tech_overlap,
                    'recency_score': recency_score,
                    'quality_score': quality_score
                })
            
            # Sort by final score and take top k
            candidate_projects.sort(key=lambda x: x['final_score'], reverse=True)
            
            matched_projects = []
            for candidate in candidate_projects[:top_k]:
                matched_project = MatchedProject(
                    project=candidate['project'],
                    similarity_score=candidate['final_score']
                )
                matched_projects.append(matched_project)
            return matched_projects
            
        except Exception as e:
            print(f"Error finding matching projects: {str(e)}")
            raise e

    def _save_embeddings(self):
        """Save embeddings and FAISS index to disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, self.index_file)
            
            # Save embeddings cache and mapping
            save_data = {
                'embeddings_cache': self.embeddings_cache,
                'project_mapping': self.project_mapping,
                'model_name': self.model_name
            }
            with open(self.embeddings_file, 'wb') as f:
                f.write(pickle.dumps(save_data))
            
        except Exception as e:
            print(f"Error saving embeddings: {str(e)}")
    
    def _load_embeddings(self):
        """Load embeddings and FAISS index from disk"""
        try:
            if not os.path.exists(self.embeddings_file) or not os.path.exists(self.index_file):
                print("No saved embeddings found")
                return
            
            # Load FAISS index
            self.index = faiss.read_index(self.index_file)
            
            # Load embeddings cache and mapping
            with open(self.embeddings_file, 'rb') as f:
                save_data = pickle.load(f)
            
            self.embeddings_cache = save_data['embeddings_cache']
            self.project_mapping = save_data['project_mapping']
            
            print(f"Loaded enhanced embeddings for {len(self.project_mapping)} projects")
            
        except Exception as e:
            print(f"Error loading embeddings: {str(e)}")
            self.index = None
            self.embeddings_cache = {}
            self.project_mapping = {}