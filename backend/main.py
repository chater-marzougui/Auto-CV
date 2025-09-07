from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
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
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Point directly to the backend/.env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

class ScrapeRequest(BaseModel):
    github_username: str

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        async with self.connection_lock:
            self.active_connections[client_id] = websocket
        logger.info(f"WebSocket connected for client: {client_id}")
    
    async def disconnect(self, client_id: str):
        async with self.connection_lock:
            if client_id in self.active_connections:
                logger.info(f"WebSocket disconnected for client: {client_id}")
                del self.active_connections[client_id]
    
    async def send_progress(self, client_id: str, message: dict):
        async with self.connection_lock:
            if client_id in self.active_connections:
                try:
                    logger.info(f"Sending progress to client {client_id}: {message['message']}")
                    await self.active_connections[client_id].send_text(json.dumps(message))
                    return True
                except Exception as e:
                    logger.error(f"Error sending message to client {client_id}: {e}")
                    # Connection might be closed, remove it
                    if client_id in self.active_connections:
                        del self.active_connections[client_id]
                    return False
            else:
                logger.warning(f"No active connection found for client: {client_id}")
                return False

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
            try:
                # Wait for any client message or timeout after 30 seconds
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_text(json.dumps({
                    "type": "heartbeat",
                    "message": "Connection alive",
                    "timestamp": "2024-01-01T00:00:00"
                }))
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket client {client_id} disconnected")
    finally:
        await websocket_manager.disconnect(client_id)

async def perform_github_scraping(github_username: str, client_id: str):
    """Background task to perform GitHub scraping with proper async handling"""
    scraper = None
    try:
        logger.info(f"Starting GitHub scraping task for: {github_username}")
        
        # Create scraper with WebSocket support
        scraper = GitHubScraper(websocket_manager=websocket_manager, client_id=client_id)
        
        # Send initial connection test
        await websocket_manager.send_progress(client_id, {
            "type": "progress",
            "message": f"Initializing GitHub scraping for {github_username}",
            "step": "starting",
            "current": 0,
            "total": 0,
            "repo_name": "",
            "timestamp": "2024-01-01T00:00:00",
            "alert": {
                "type": "info",
                "message": f"Starting scraping process for {github_username}"
            }
        })
        
        # Add a small delay to ensure WebSocket connection is stable
        await asyncio.sleep(1)
        
        # Perform the actual scraping
        projects = await scraper.scrape_and_process_repos(github_username)
        
        # Send completion message
        await websocket_manager.send_progress(client_id, {
            "type": "progress",
            "message": f"GitHub scraping completed! Processed {len(projects)} projects.",
            "step": "finished",
            "current": len(projects),
            "total": len(projects),
            "repo_name": "",
            "timestamp": "2024-01-01T00:00:00",
            "alert": {
                "type": "success",
                "message": f"Successfully processed {len(projects)} repositories"
            }
        })
        
        logger.info(f"Completed scraping {len(projects)} projects")
        
    except Exception as e:
        logger.error(f"Error in GitHub scraping task: {e}")
        
        # Send error message via WebSocket
        try:
            await websocket_manager.send_progress(client_id, {
                "type": "progress",
                "message": f"Error occurred during scraping: {str(e)}",
                "step": "error",
                "current": 0,
                "total": 0,
                "repo_name": "",
                "timestamp": "2024-01-01T00:00:00",
                "alert": {
                    "type": "error",
                    "message": str(e)
                }
            })
        except Exception as ws_error:
            logger.error(f"Failed to send error message via WebSocket: {ws_error}")
    
    finally:
        # Clean up resources
        if scraper:
            scraper.cleanup()

@app.post("/api/v1/scrape-github")
async def scrape_github_profile(req: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Scrape all repositories from a GitHub profile and generate project summaries
    """
    try:
        github_username = req.github_username
        client_id = str(uuid.uuid4())
        logger.info(f"Received scrape request for: {github_username}, client_id: {client_id}")
        
        # Add the scraping task to background tasks
        background_tasks.add_task(perform_github_scraping, github_username, client_id)
        
        return {
            "message": f"GitHub scraping started for {github_username}", 
            "client_id": client_id,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error starting GitHub scraping: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)