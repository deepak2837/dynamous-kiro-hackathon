"""
Study Buddy App - FastAPI Backend Application

This module initializes the FastAPI application for the Study Buddy App,
an AI-powered study companion for medical students preparing for MBBS exams.

The application provides:
- Multi-format file upload (PDF, images, PPTX)
- AI-powered content generation (questions, mock tests, mnemonics, cheat sheets, notes)
- Session-based study material organization
- Real-time processing status tracking
- Export functionality for offline study

Author: Study Buddy Team
Created: January 2026
License: MIT
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import time

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.api.auth_simple import router as auth_router
from app.logging_config import logger
from app.middleware.rate_limit import limiter, rate_limit_handler
from slowapi.errors import RateLimitExceeded

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    Handles:
    - Database connection initialization
    - Upload directory creation
    - Graceful shutdown of connections
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None: Application runs between startup and shutdown
    """
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

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # Use specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    HTTP request logging middleware.
    
    Logs all incoming requests and outgoing responses with timing information
    for monitoring and debugging purposes.
    
    Args:
        request: Incoming HTTP request
        call_next: Next middleware/endpoint in the chain
        
    Returns:
        Response: HTTP response with added timing headers
    """
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response

# Include API routes
app.include_router(auth_router)  # Auth routes with /api/v1/auth prefix

# Add backward compatibility for direct /login endpoint
from app.api.auth_simple import login_user as auth_login_user
from app.auth_models_simple import UserLoginRequest, TokenResponse

@app.post("/login", response_model=TokenResponse)
async def login_compatibility(request: UserLoginRequest):
    """
    Backward compatibility endpoint for direct /login access.
    
    Provides compatibility with existing MedGloss authentication patterns
    while maintaining the new /api/v1/auth/login structure.
    
    Args:
        request: User login credentials (mobile and password)
        
    Returns:
        TokenResponse: JWT access token and user information
        
    Raises:
        HTTPException: If authentication fails
    """
    return await auth_login_user(request)

# Add v1 API router (includes text-input, upload, sessions, etc.)
from app.api.v1.api import api_router
app.include_router(api_router, prefix="/api/v1")

# Add history routes
from app.api.history import router as history_router
app.include_router(history_router)

# Add test endpoint for AI_ONLY processing

# Add real content routes
from app.api.v1.endpoints.questions import router as questions_router
app.include_router(questions_router, prefix="/api/v1/questions")

# Add real results routes  
from app.api.questions_basic import router as questions_basic_router
app.include_router(questions_basic_router, prefix="/api/v1")

# Add S3 test routes

@app.get("/")
async def root():
    """
    Root endpoint providing API information.
    
    Returns basic information about the Study Buddy API including
    version and documentation links.
    
    Returns:
        dict: API metadata and status information
    """
    return {
        "message": "StudyBuddy API is running!",
        "version": settings.version,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Provides service health status for monitoring systems
    and deployment health checks.
    
    Returns:
        dict: Service health status and metadata
    """
    return {
        "status": "healthy",
        "service": settings.project_name,
        "version": settings.version
    }
