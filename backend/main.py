from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routes import jobs, generate
from app.services.github_scraper import GitHubScraper
from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Point directly to the backend/.env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

class ScrapeRequest(BaseModel):
    github_username: str

app = FastAPI(
    title="CV Generator API",
    description="Automatically generate CV and cover letters based on GitHub projects and job descriptions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(generate.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "CV Generator API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/scrape-github")
async def scrape_github_profile(req: ScrapeRequest):
    """
    Scrape all repositories from a GitHub profile and generate project summaries
    """
    try:
        github_username = req.github_username
        print(f"Starting to scrape GitHub profile: {github_username}")
        scraper = GitHubScraper()
        projects = await scraper.scrape_and_process_repos(github_username)
        return {"message": f"Successfully scraped {len(projects)} projects", "projects_count": len(projects)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)