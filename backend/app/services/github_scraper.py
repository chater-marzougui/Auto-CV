import json
import os
import re
import asyncio
from typing import List, Optional
from github import Github
from datetime import datetime
from app.models.project import Project
from app.services.embeddings import EmbeddingService
from app.services.gemini_service import GeminiService
from github import Repository
from concurrent.futures import ThreadPoolExecutor
import functools
from app.utils.colored_logger import get_scraper_logger, log_progress, log_success, log_warning, log_error, log_debug

class GitHubScraper:
    def __init__(self, github_token: Optional[str] = None, websocket_manager=None, client_id: str = None):
        """
        Initialize GitHub scraper
        Args:
            github_token: GitHub personal access token (optional but recommended for higher rate limits)
            websocket_manager: WebSocket manager for progress updates
            client_id: Client ID for WebSocket connection
        """
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.github = Github(self.github_token) if self.github_token else Github()
        self.embedding_service = EmbeddingService()
        self.gemini_service = GeminiService()
        self.data_dir = "app/data"
        self.projects_file = os.path.join(self.data_dir, "projects.json")
        self.websocket_manager = websocket_manager
        self.client_id = client_id
        
        # Thread pool for blocking operations
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Setup logger
        self.logger = get_scraper_logger()
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        log_success(self.logger, "GitHubScraper initialized", f"client_id: {client_id}")
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
            log_success(self.logger, "Thread executor cleaned up", self.client_id or "unknown")
    
    async def send_progress(self, message: str, step: str, current: int = 0, total: int = 0, 
                          repo_name: str = "", alert_type: str = None, alert_message: str = ""):
        """Send progress update via WebSocket"""
        if self.websocket_manager and self.client_id:
            progress_data = {
                "type": "progress",
                "message": message,
                "step": step,
                "current": current,
                "total": total,
                "repo_name": repo_name,
                "timestamp": datetime.now().isoformat(),
                "alert": {
                    "type": alert_type,
                    "message": alert_message
                } if alert_type else None
            }
            await self.websocket_manager.send_progress(self.client_id, progress_data)
    
    def _run_in_executor(self, func, *args):
        """Run a synchronous function in a thread pool"""
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(self.executor, func, *args)
    
    async def scrape_and_process_repos(self, username: str) -> List[Project]:
        """
        Scrape all repositories from a GitHub user and process them
        """
        log_progress(self.logger, f"Starting GitHub scrape", repo=username)
        
        await self.send_progress(
            f"Starting GitHub scrape for user: {username}", 
            "initialization"
        )
        
        if not self.github_token:
            log_warning(self.logger, "No GitHub token provided - rate limits may apply", username)
            await self.send_progress(
                "No GitHub token provided - rate limits may apply", 
                "warning",
                alert_type="warning",
                alert_message="Consider adding a GitHub token for better performance"
            )
        
        try:
            # Run GitHub API calls in executor to avoid blocking
            log_progress(self.logger, "Fetching user repositories", step="API_CALL", repo=username)
            await self.send_progress("Fetching user repositories...", "fetching")
            
            user = await self._run_in_executor(self.github.get_user, username)
            repos_list = await self._run_in_executor(lambda: list(user.get_repos(type='owner')))
            owned_repos = [repo for repo in repos_list if not repo.fork]
            
            log_success(self.logger, f"Found {len(owned_repos)} repositories to process", username)
            await self.send_progress(
                f"Found {len(owned_repos)} repositories to process", 
                "discovery",
                total=len(owned_repos)
            )
            
            projects = []
            existing_projects = await self._run_in_executor(self.load_projects)
            
            repos_to_process = owned_repos[:9]
            
            for i, repo in enumerate(repos_to_process, 1):
                log_progress(self.logger, f"Processing repository: {repo.name} ({i}/{len(repos_to_process)})", repo=username)
                await self.send_progress(
                    f"Processing repository: {repo.name}", 
                    "processing",
                    current=i,
                    total=len(repos_to_process),
                    repo_name=repo.name
                )
                
                # Check if repo is already processed and up-to-date
                if any(p.name == repo.name and repo.updated_at <= p.updated_at for p in existing_projects):
                    log_warning(self.logger, f"Repository {repo.name} is already up-to-date, skipping", username)
                    await self.send_progress(
                        f"Repository {repo.name} is already up-to-date, skipping", 
                        "skipping",
                        current=i,
                        total=len(repos_to_process),
                        repo_name=repo.name,
                        alert_type="info",
                        alert_message=f"{repo.name} already processed"
                    )
                    continue

                project = await self._process_repository(repo, i, len(repos_to_process))
                if project:
                    projects.append(project)
                    log_success(self.logger, f"Successfully processed {repo.name}", username)
                    
                # Add a small delay between repositories to prevent overwhelming
                await asyncio.sleep(0.5)

            # Save projects to JSON file
            log_progress(self.logger, "Saving projects to database", step="SAVE", repo=username)
            await self.send_progress("Saving projects to database", "saving")
            await self._run_in_executor(self._save_projects, projects)
            
            # Generate embeddings for all projects
            log_progress(self.logger, "Generating embeddings for semantic search", step="EMBEDDINGS", repo=username)
            await self.send_progress("Generating embeddings for semantic search", "embeddings")
            await self._run_in_executor(self.embedding_service.generate_embeddings_for_projects, projects)

            log_success(self.logger, f"Successfully processed {len(projects)} projects", username)
            await self.send_progress(
                f"Successfully processed {len(projects)} projects", 
                "completed",
                current=len(projects),
                total=len(projects),
                alert_type="success",
                alert_message=f"✅ Completed processing {len(projects)} repositories"
            )
            return projects
            
        except Exception as e:
            log_error(self.logger, f"Error scraping GitHub profile: {str(e)}", username, exc_info=True)
            await self.send_progress(
                f"Error scraping GitHub profile: {str(e)}", 
                "error",
                alert_type="error",
                alert_message=str(e)
            )
            raise e
    
    async def _process_repository(self, repo: Repository, current: int, total: int) -> Optional[Project]:
        """
        Process a single repository and extract information
        """
        try:
            # Get README content
            await self.send_progress(
                f"Reading README for {repo.name}", 
                "readme",
                current=current,
                total=total,
                repo_name=repo.name
            )
            
            readme_content, success = await self._run_in_executor(self._get_readme_content, repo)
            
            if not success:
                await self.send_progress(
                    f"Repository {repo.name} has no readable README", 
                    "readme_missing",
                    current=current,
                    total=total,
                    repo_name=repo.name,
                    alert_type="warning",
                    alert_message=f"No README found in {repo.name}"
                )
                
                return Project(
                    name=repo.name,
                    url=repo.html_url,
                    description=repo.description or "No description provided",
                    readme_content="",
                    bad_readme=True,
                    no_readme=True,
                    three_liner="No README available to generate summary.",
                    detailed_paragraph="No README available to generate detailed paragraph.",
                    technologies=[],
                    tree=[],
                    stars=repo.stargazers_count,
                    forks=repo.forks_count,
                    language=repo.language or "Unknown",
                    created_at=repo.created_at,
                    updated_at=repo.updated_at
                )
            
            # Get repository file tree
            await self.send_progress(
                f"Analyzing file structure for {repo.name}", 
                "file_tree",
                current=current,
                total=total,
                repo_name=repo.name
            )
            tree = await self._run_in_executor(self._get_repo_trees, repo)
            
            # Generate AI summaries
            await self.send_progress(
                f"Generating AI summary with Gemini for {repo.name}", 
                "ai_processing",
                current=current,
                total=total,
                repo_name=repo.name
            )
            
            gemini_response = await self._run_in_executor(
                self.gemini_service.generate_project_summary, 
                repo.name, readme_content, tree
            )
            
            three_liner = gemini_response.get("three_liner", "")
            detailed_paragraph = gemini_response.get("detailed", "")
            technologies = gemini_response.get("technologies", "")
            bad_readme = gemini_response.get("bad_readme", False)
            
            if bad_readme:
                await self.send_progress(
                    f"README quality issues detected in {repo.name}", 
                    "readme_quality",
                    current=current,
                    total=total,
                    repo_name=repo.name,
                    alert_type="warning",
                    alert_message=f"Poor README quality in {repo.name}"
                )
            
            if not three_liner:
                three_liner = await self._run_in_executor(self._generate_three_liner, repo, readme_content)
            if not detailed_paragraph:
                detailed_paragraph = await self._run_in_executor(
                    self._generate_detailed_paragraph, repo, readme_content, technologies
                )
            if not technologies:
                technologies = await self._run_in_executor(self._extract_technologies, repo, readme_content)
            
            await self.send_progress(
                f"Creating project entry for {repo.name}", 
                "finalizing",
                current=current,
                total=total,
                repo_name=repo.name
            )
                
            project = Project(
                name=repo.name,
                url=repo.html_url,
                description=repo.description or "No description provided",
                readme_content=readme_content,
                three_liner=three_liner,
                detailed_paragraph=detailed_paragraph,
                technologies=technologies,
                tree=tree,
                stars=repo.stargazers_count,
                forks=repo.forks_count,
                language=repo.language or "Unknown",
                bad_readme=bad_readme,
                no_readme=False,
                created_at=repo.created_at,
                updated_at=repo.updated_at
            )
            
            await self.send_progress(
                f"Successfully processed {repo.name}", 
                "repo_completed",
                current=current,
                total=total,
                repo_name=repo.name,
                alert_type="success",
                alert_message=f"✅ {repo.name} processed successfully"
            )
            
            return project
            
        except Exception as e:
            await self.send_progress(
                f"Error processing repository {repo.name}: {str(e)}", 
                "error",
                current=current,
                total=total,
                repo_name=repo.name,
                alert_type="error",
                alert_message=f"Failed to process {repo.name}: {str(e)}"
            )
            return None
    
    def _get_readme_content(self, repo) -> tuple[str, bool]:
        """
        Get README content from repository (synchronous - run in executor)
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
                    return readme.decoded_content.decode('utf-8'), True
                except Exception:
                    continue

            return "No README found", False

        except Exception:
            return "Error reading README", False
    
    def _get_repo_trees(self, repo: Repository) -> List[str]:
        """
        Recursively get all files in the repository (synchronous - run in executor)
        """
        try:
            # First, try to get the default branch name
            default_branch = repo.default_branch
            tree = repo.get_git_tree(sha=default_branch, recursive=True).tree
            file_paths = [item.path for item in tree if item.type == 'blob']
            return file_paths
            
        except Exception as e:
            print(f"Error with default branch '{default_branch}': {e}")
            
            # Fallback: try common branch names
            common_branches = ['main', 'master']
            
            for branch in common_branches:
                if branch == default_branch:
                    continue  # Already tried this one
                    
                try:
                    tree = repo.get_git_tree(sha=branch, recursive=True).tree
                    file_paths = [item.path for item in tree if item.type == 'blob']
                    return file_paths
                    
                except Exception as fallback_e:
                    print(f"Failed with branch '{branch}': {fallback_e}")
                    continue
            
            print("All attempts to get repository tree failed")
            return []
    
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
    
    def _save_projects(self, projects: List[Project]):
        """
        Save projects to JSON file (synchronous - run in executor)
        """
        try:
            # Convert projects to dict format for JSON serialization
            projects_data = []
            existing_projects = self.load_projects()
            projects.extend(p for p in existing_projects if p.name not in {proj.name for proj in projects})
            
            for project in projects:
                project_dict = project.dict()
                # Convert datetime objects to ISO format strings
                project_dict['created_at'] = project.created_at.isoformat()
                project_dict['updated_at'] = project.updated_at.isoformat()
                projects_data.append(project_dict)
            
            with open(self.projects_file, 'w', encoding='utf-8') as f:
                f.write(json.dumps(projects_data, indent=2, ensure_ascii=False))
                
            print(f"Saved {len(projects)} projects to {self.projects_file}")
            
        except Exception as e:
            print(f"Error saving projects: {str(e)}")
    
    def load_projects(self) -> List[Project]:
        """
        Load projects from JSON file (synchronous - run in executor)
        """
        try:
            if not os.path.exists(self.projects_file):
                return []
                
            with open(self.projects_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
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
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)