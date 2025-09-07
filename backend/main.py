from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.routes import jobs, generate
from app.services.github_scraper import GitHubScraper
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import asyncio
import json
from typing import Dict, List
import uuid

# Point directly to the backend/.env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

class ScrapeRequest(BaseModel):
    github_username: str

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_progress(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception:
                # Connection might be closed, remove it
                self.disconnect(client_id)

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

# WebSocket manager instance
websocket_manager = WebSocketManager()

# Include routers
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(generate.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "CV Generator API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)

@app.post("/api/v1/scrape-github")
async def scrape_github_profile(req: ScrapeRequest):
    """
    Scrape all repositories from a GitHub profile and generate project summaries
    """
    try:
        github_username = req.github_username
        client_id = str(uuid.uuid4())
        print(f"Starting to scrape GitHub profile: {github_username}")
        
        # Create scraper with WebSocket support
        scraper = GitHubScraper(websocket_manager=websocket_manager, client_id=client_id)
        projects = await scraper.scrape_and_process_repos(github_username)
        
        return {
            "message": f"Successfully scraped {len(projects)} projects", 
            "projects_count": len(projects),
            "client_id": client_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)