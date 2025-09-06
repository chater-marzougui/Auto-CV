import os
import numpy as np
import pickle
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import faiss
from app.models.project import Project, JobDescription, MatchedProject

class EmbeddingService:
    def __init__(self):
        """
        Initialize embedding service with sentence transformer model
        """
        self.model_name = "all-MiniLM-L6-v2"  # Good balance of speed and quality
        self.model = SentenceTransformer(self.model_name)
        self.data_dir = "app/data"
        self.embeddings_file = os.path.join(self.data_dir, "embeddings.pkl")
        self.index_file = os.path.join(self.data_dir, "faiss_index.bin")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize or load FAISS index
        self.index = None
        self.project_mapping = {}  # Maps FAISS index positions to project names
        self.embeddings_cache = {}
    
    def generate_embeddings_for_projects(self, projects: List[Project]):
        """
        Generate embeddings for all projects and store them
        """
        print(f"Generating embeddings for {len(projects)} projects...")
        
        # Prepare texts for embedding
        project_texts = []
        project_names = []
        
        for project in projects:
            # Combine detailed paragraph with technologies for better matching
            combined_text = f"{project.detailed_paragraph} Technologies: {', '.join(project.technologies)}"
            project_texts.append(combined_text)
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
        
        # Cache embeddings and projects
        self.embeddings_cache = {
            'embeddings': embeddings,
            'projects': {project.name: project for project in projects},
            'project_names': project_names
        }
        
        # Save to disk
        self._save_embeddings()
        
        print(f"Successfully generated and saved embeddings for {len(projects)} projects")
    
    def find_matching_projects(self, job_description: JobDescription, top_k: int = 4) -> List[MatchedProject]:
        """
        Find projects that best match a job description
        """
        try:
            # Load embeddings if not in memory
            if not self.index or not self.embeddings_cache:
                self._load_embeddings()
            
            if not self.index:
                raise RuntimeError("No embeddings found. Please scrape GitHub repositories first.")
            
            # Prepare job description text
            job_text = f"{job_description.title} {job_description.company} {job_description.description}"
            if job_description.requirements:
                job_text += f" {job_description.requirements}"
            
            # Generate embedding for job description
            job_embedding = self.model.encode([job_text], convert_to_tensor=False)
            faiss.normalize_L2(job_embedding)
            
            # Search for similar projects
            scores, indices = self.index.search(job_embedding.astype('float32'), top_k)
            
            matched_projects = []
            
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx == -1:  # No more results
                    break
                
                project_name = self.project_mapping[idx]
                project = self.embeddings_cache['projects'][project_name]
                
                # Generate relevance reason
                relevance_reason = self._generate_relevance_reason(job_description, project)
                
                matched_project = MatchedProject(
                    project=project,
                    similarity_score=float(score),
                    relevance_reason=relevance_reason
                )
                
                matched_projects.append(matched_project)
            
            return matched_projects
            
        except Exception as e:
            print(f"Error finding matching projects: {str(e)}")
            raise e
    
    def _generate_relevance_reason(self, job_description: JobDescription, project: Project) -> str:
        """
        Generate a reason why this project is relevant to the job
        """
        try:
            # Extract key technologies from job description
            job_text = f"{job_description.description} {job_description.requirements or ''}".lower()
            
            # Find common technologies
            common_techs = []
            for tech in project.technologies:
                if tech.lower() in job_text:
                    common_techs.append(tech)
            
            if common_techs:
                tech_str = ", ".join(common_techs[:3])
                reason = f"Demonstrates experience with {tech_str}"
            else:
                # Fallback based on project type and job requirements
                if "web" in job_text and any(tech.lower() in ["javascript", "react", "html", "css"] for tech in project.technologies):
                    reason = "Shows web development expertise"
                elif "backend" in job_text and any(tech.lower() in ["python", "java", "node"] for tech in project.technologies):
                    reason = "Demonstrates backend development skills"
                elif "data" in job_text and any(tech.lower() in ["python", "pandas", "sql"] for tech in project.technologies):
                    reason = "Shows data processing capabilities"
                else:
                    reason = f"Relevant {project.language} project showcasing technical skills"
            
            return reason
            
        except Exception:
            return "Relevant technical project demonstrating software development skills"
    
    def _save_embeddings(self):
        """
        Save embeddings and FAISS index to disk
        """
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
            
            print("Embeddings and index saved successfully")
            
        except Exception as e:
            print(f"Error saving embeddings: {str(e)}")
    
    def _load_embeddings(self):
        """
        Load embeddings and FAISS index from disk
        """
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
            
            print(f"Loaded embeddings for {len(self.project_mapping)} projects")
            
        except Exception as e:
            print(f"Error loading embeddings: {str(e)}")
            self.index = None
            self.embeddings_cache = {}
            self.project_mapping = {}
    
    def get_project_similarities(self, project_names: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Get similarity scores between projects (useful for analysis)
        """
        try:
            if not self.embeddings_cache:
                self._load_embeddings()
            
            similarities = {}
            embeddings = self.embeddings_cache['embeddings']
            project_names_list = self.embeddings_cache['project_names']
            
            for i, name1 in enumerate(project_names):
                if name1 not in project_names_list:
                    continue
                    
                similarities[name1] = {}
                idx1 = project_names_list.index(name1)
                
                for j, name2 in enumerate(project_names):
                    if name2 not in project_names_list:
                        continue
                        
                    idx2 = project_names_list.index(name2)
                    
                    # Compute cosine similarity
                    similarity = np.dot(embeddings[idx1], embeddings[idx2])
                    similarities[name1][name2] = float(similarity)
            
            return similarities
            
        except Exception as e:
            print(f"Error computing similarities: {str(e)}")
            return {}