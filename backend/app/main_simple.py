from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.api.auth_simple import router as auth_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up StudyBuddy API...")
    
    # Create upload directory
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Connect to database
    await connect_to_mongo()
    
    yield
    
    # Shutdown
    logger.info("Shutting down StudyBuddy API...")
    await close_mongo_connection()

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description=settings.description,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth_router)  # Auth routes (no prefix for compatibility)

# Add simple upload routes
from app.api.upload_with_logging import router as upload_simple_router
app.include_router(upload_simple_router, prefix="/api/v1/upload")

# Add history routes
from app.api.history import router as history_router
app.include_router(history_router)

@app.get("/")
async def root():
    return {
        "message": "StudyBuddy API is running!",
        "version": settings.version,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.project_name,
        "version": settings.version
    }
