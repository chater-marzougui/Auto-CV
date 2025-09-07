import os
import pickle
import re
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import faiss
from datetime import datetime, timezone
from app.models.project import Project, MatchedProject

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
        if not project.updated_at:
            return 0.1  # Very low score for unknown dates
        
        now = datetime.now(timezone.utc)
        if project.updated_at.tzinfo is None:
            project_date = project.updated_at.replace(tzinfo=timezone.utc)
        else:
            project_date = project.updated_at
        
        days_old = (now - project_date).days
        
        # Scoring: projects updated in last 30 days get full score
        # Score decreases exponentially after that
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
        """Generate enhanced embeddings for all projects"""
        print(f"Generating enhanced embeddings for {len(projects)} projects...")
        
        # Prepare enhanced texts for embedding
        project_texts = []
        project_names = []
        
        for project in projects:
            weighted_text = self._create_weighted_text(project)
            project_texts.append(weighted_text)
            project_names.append(project.name)
        
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
            'projects': {project.name: project for project in projects},
            'project_names': project_names,
            'recency_scores': {project.name: self._calculate_recency_score(project) for project in projects},
            'quality_scores': {project.name: self._calculate_quality_score(project) for project in projects}
        }
        
        # Save to disk
        self._save_embeddings()
        
        print(f"Successfully generated and saved enhanced embeddings for {len(projects)} projects")
    
    def _extract_job_technologies(self, job_description: str) -> List[str]:
        """Extract technologies mentioned in job description"""
        job_lower = job_description.lower()
        
        # Common technology patterns
        tech_patterns = {
            'python': r'\b(python|django|flask|fastapi|pandas|numpy)\b',
            'javascript': r'\b(javascript|js|node\.?js|react|vue|angular|express)\b',
            'typescript': r'\b(typescript|ts)\b',
            'java': r'\b(java|spring|maven|gradle)\b',
            'csharp': r'\b(c#|csharp|\.net|dotnet)\b',
            'php': r'\b(php|laravel|symfony)\b',
            'ruby': r'\b(ruby|rails|ruby on rails)\b',
            'go': r'\b(golang|go)\b',
            'rust': r'\b(rust)\b',
            'docker': r'\b(docker|dockerfile|container)\b',
            'kubernetes': r'\b(kubernetes|k8s|helm)\b',
            'aws': r'\b(aws|amazon web services|ec2|s3|lambda)\b',
            'azure': r'\b(azure|microsoft azure)\b',
            'gcp': r'\b(gcp|google cloud|cloud platform)\b',
            'postgres': r'\b(postgresql|postgres)\b',
            'mysql': r'\b(mysql)\b',
            'mongodb': r'\b(mongodb|mongo)\b',
            'redis': r'\b(redis)\b',
            'react': r'\b(react|reactjs|react\.js)\b',
            'vue': r'\b(vue|vuejs|vue\.js)\b',
            'angular': r'\b(angular|angularjs)\b',
            'nodejs': r'\b(node\.js|nodejs|node js)\b',
            'graphql': r'\b(graphql)\b',
            'rest': r'\b(rest api|restful|rest)\b',
            'microservices': r'\b(microservices|micro-services)\b',
            'machine learning': r'\b(machine learning|ml|ai|artificial intelligence)\b',
            'tensorflow': r'\b(tensorflow|tf)\b',
            'pytorch': r'\b(pytorch|torch)\b'
        }
        
        found_technologies = []
        for tech, pattern in tech_patterns.items():
            if re.search(pattern, job_lower):
                found_technologies.append(tech)
        
        return self._normalize_technologies(found_technologies)
    
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
        """Enhanced project matching with multi-factor scoring"""
        try:
            # Load embeddings if not in memory
            if not self.index or not self.embeddings_cache:
                self._load_embeddings()
            
            if not self.index:
                raise RuntimeError("No embeddings found. Please scrape GitHub repositories first.")
            
            # Extract technologies from job description
            job_technologies = self._extract_job_technologies(job_description)
            print(f"Extracted job technologies: {job_technologies}")
            
            # Create enhanced job description for embedding
            job_text = f"{job_description} Required technologies: {' '.join(job_technologies)}"
            
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
                
                # Calculate component scores
                recency_score = self.embeddings_cache['recency_scores'][project_name]
                quality_score = self.embeddings_cache['quality_scores'][project_name]
                tech_overlap_score = self._calculate_technology_overlap_score(
                    project.technologies, job_technologies
                )
                
                # Enhanced scoring formula
                # Weights: semantic(0.4) + tech_overlap(0.35) + recency(0.15) + quality(0.1)
                final_score = (
                    float(semantic_score) * 0.4 +
                    tech_overlap_score * 0.35 +
                    recency_score * 0.15 +
                    quality_score * 0.1
                )
                
                # Additional bonuses/penalties
                if project.no_readme:
                    final_score *= 0.5  # Significant penalty
                elif project.bad_readme:
                    final_score *= 0.7  # Moderate penalty
                
                # Bonus for projects with job-relevant technologies
                if tech_overlap_score > 0.5:
                    final_score *= 1.2
                
                candidate_projects.append({
                    'project': project,
                    'final_score': final_score,
                    'semantic_score': float(semantic_score),
                    'tech_overlap_score': tech_overlap_score,
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
                
                # Debug info
                print(f"Project: {candidate['project'].name}")
                print(f"  Final Score: {candidate['final_score']:.3f}")
                print(f"  Semantic: {candidate['semantic_score']:.3f}")
                print(f"  Tech Overlap: {candidate['tech_overlap_score']:.3f}")
                print(f"  Recency: {candidate['recency_score']:.3f}")
                print(f"  Quality: {candidate['quality_score']:.3f}")
                print(f"  Technologies: {candidate['project'].technologies}")
                print("---")
            
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
            
            print("Enhanced embeddings and index saved successfully")
            
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