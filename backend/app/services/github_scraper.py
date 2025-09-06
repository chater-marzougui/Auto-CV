import json
import os
import re
from typing import List, Optional
from github import Github
from datetime import datetime
from app.models.project import Project
from app.services.embeddings import EmbeddingService
import aiofiles

class GitHubScraper:
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub scraper
        Args:
            github_token: GitHub personal access token (optional but recommended for higher rate limits)
        """
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.github = Github(self.github_token) if self.github_token else Github()
        self.embedding_service = EmbeddingService()
        self.data_dir = "app/data"
        self.projects_file = os.path.join(self.data_dir, "projects.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
    
    async def scrape_and_process_repos(self, username: str) -> List[Project]:
        """
        Scrape all repositories from a GitHub user and process them
        """
        print(f"Scraping repositories for user: {username}")
        print("Using GitHub token:", "Yes" if self.github_token else "No")
        if not self.github_token:
            print("Warning: No GitHub token provided. You will hit rate limits.")
            return []
        try:
            user = self.github.get_user(username)
            repos = user.get_repos(type='owner')  # Only get owned repos, not forks
            
            projects = []
            print(f"Found {repos.totalCount} repositories")
            for repo in repos:
                if repo.fork:  # Skip forked repositories
                    continue
                    
                print(f"Processing repository: {repo.name}")
                project = self._process_repository(repo)
                if project:
                    projects.append(project)
                    break # For testing, process only the first repo
            
            # Save projects to JSON file
            await self._save_projects(projects)
            
            # Generate embeddings for all projects
            await self.embedding_service.generate_embeddings_for_projects(projects)

            print(f"Successfully processed {len(projects)} projects")
            return projects
            
        except Exception as e:
            print(f"Error scraping GitHub profile: {str(e)}")
            raise e
    
    def _process_repository(self, repo) -> Optional[Project]:
        """
        Process a single repository and extract information
        """
        try:
            # Get README content
            readme_content = self._get_readme_content(repo)
            
            # Extract technologies from various sources
            technologies = self._extract_technologies(repo, readme_content)
            
            # Generate AI summaries
            three_liner = self._generate_three_liner(repo, readme_content)
            detailed_paragraph = self._generate_detailed_paragraph(repo, readme_content, technologies)
            
            project = Project(
                name=repo.name,
                url=repo.html_url,
                description=repo.description or "No description provided",
                readme_content=readme_content,
                three_liner=three_liner,
                detailed_paragraph=detailed_paragraph,
                technologies=technologies,
                stars=repo.stargazers_count,
                forks=repo.forks_count,
                language=repo.language or "Unknown",
                created_at=repo.created_at,
                updated_at=repo.updated_at
            )
            
            return project
            
        except Exception as e:
            print(f"Error processing repository {repo.name}: {str(e)}")
            return None
    
    def _get_readme_content(self, repo) -> str:
        """
        Get README content from repository
        """
        try:
            # Try all common README file naming conventions
            readme_files = [
                'README.md', 'README.MD', 'readme.md', 'Readme.md',
                'README', 'ReadMe', 'readme'
            ]
            
            for readme_file in readme_files:
                try:
                    readme = repo.get_contents(readme_file)
                    return readme.decoded_content.decode('utf-8')
                except Exception:
                    continue
                    
            return "No README found"

        except Exception:
            return "Error reading README"
    
    def _extract_technologies(self, repo, readme_content: str) -> List[str]:
        """
        Extract technologies from repository language, README, and common files
        """
        technologies = set()
        
        # Add primary language
        if repo.language:
            technologies.add(repo.language)
        
        # Extract from README content
        tech_patterns = {
            'python': r'\b(python|django|flask|fastapi|pandas|numpy|tensorflow|pytorch)\b',
            'javascript': r'\b(javascript|node\.?js|react|vue|angular|express)\b',
            'java': r'\b(java|spring|maven|gradle)\b',
            'docker': r'\b(docker|dockerfile|container)\b',
            'kubernetes': r'\b(kubernetes|k8s|helm)\b',
            'aws': r'\b(aws|amazon web services|ec2|s3|lambda)\b',
            'database': r'\b(mysql|postgresql|mongodb|redis|sqlite)\b',
            'frontend': r'\b(html|css|scss|sass|bootstrap|tailwind)\b',
            'api': r'\b(rest api|graphql|api)\b',
            'testing': r'\b(pytest|jest|junit|testing|test)\b'
        }
        
        readme_lower = readme_content.lower()
        for tech_category, pattern in tech_patterns.items():
            if re.search(pattern, readme_lower, re.IGNORECASE):
                matches = re.findall(pattern, readme_lower, re.IGNORECASE)
                technologies.update([match.strip() for match in matches])
        
        # Try to get languages from GitHub API
        try:
            languages = repo.get_languages()
            technologies.update(languages.keys())
        except Exception as e:
            print(f"Error getting languages for repository {repo.name}: {str(e)}")
            
        return list(technologies)
    
    def _generate_three_liner(self, repo, readme_content: str) -> str:
        """
        Generate a 3-line summary of the project
        """
        try:
            # Simple heuristic-based summary for now
            # In production, you'd want to use a proper LLM here
            description = repo.description or "No description"
            
            # Extract first meaningful paragraph from README
            readme_lines = readme_content.split('\n')
            meaningful_lines = [line.strip() for line in readme_lines 
                              if line.strip() and not line.strip().startswith('#') 
                              and len(line.strip()) > 20]
            
            first_paragraph = meaningful_lines[0] if meaningful_lines else description
            
            three_liner = f"• {repo.name}: {description}\n"
            three_liner += f"• Built with {repo.language or 'multiple technologies'}\n"
            three_liner += f"• {first_paragraph[:100]}..." if len(first_paragraph) > 100 else f"• {first_paragraph}"
            
            return three_liner
            
        except Exception:
            return f"• {repo.name}: {repo.description or 'GitHub project'}\n• Technology project\n• See repository for details"
    
    def _generate_detailed_paragraph(self, repo, readme_content: str, technologies: List[str]) -> str:
        """
        Generate a detailed paragraph about the project
        """
        try:
            description = repo.description or ""
            tech_str = ", ".join(technologies[:5]) if technologies else "various technologies"
            
            # Extract meaningful content from README
            readme_lines = readme_content.split('\n')
            meaningful_content = []
            
            for line in readme_lines:
                line = line.strip()
                if (line and not line.startswith('#') and not line.startswith('![') 
                    and not line.startswith('[') and len(line) > 20):
                    meaningful_content.append(line)
                    if len(meaningful_content) >= 3:
                        break
            
            content_summary = " ".join(meaningful_content[:2]) if meaningful_content else description
            
            detailed = f"{repo.name} is a {repo.language or 'software'} project that {description.lower() if description else 'demonstrates technical expertise'}. "
            detailed += f"The project utilizes {tech_str} and showcases practical implementation skills. "
            
            if content_summary and content_summary != description:
                detailed += f"{content_summary[:200]}{'...' if len(content_summary) > 200 else ''} "
            
            return detailed
            
        except Exception:
            return f"{repo.name} is a technical project demonstrating software development skills and practical implementation experience."
    
    async def _save_projects(self, projects: List[Project]):
        """
        Save projects to JSON file
        """
        try:
            # Convert projects to dict format for JSON serialization
            projects_data = []
            for project in projects:
                project_dict = project.dict()
                # Convert datetime objects to ISO format strings
                project_dict['created_at'] = project.created_at.isoformat()
                project_dict['updated_at'] = project.updated_at.isoformat()
                projects_data.append(project_dict)
            
            async with aiofiles.open(self.projects_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(projects_data, indent=2, ensure_ascii=False))
                
            print(f"Saved {len(projects)} projects to {self.projects_file}")
            
        except Exception as e:
            print(f"Error saving projects: {str(e)}")
    
    async def load_projects(self) -> List[Project]:
        """
        Load projects from JSON file
        """
        try:
            if not os.path.exists(self.projects_file):
                return []
                
            async with aiofiles.open(self.projects_file, 'r', encoding='utf-8') as f:
                file_content = await f.read()
                projects_data = json.loads(file_content)
            
            projects = []
            for project_dict in projects_data:
                # Convert ISO format strings back to datetime objects
                project_dict['created_at'] = datetime.fromisoformat(project_dict['created_at'])
                project_dict['updated_at'] = datetime.fromisoformat(project_dict['updated_at'])
                projects.append(Project(**project_dict))
            
            return projects
            
        except Exception as e:
            print(f"Error loading projects: {str(e)}")
            return []