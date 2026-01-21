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
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
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
    """Backward compatibility endpoint for /login"""
    return await auth_login_user(request)

# Add basic upload routes for frontend
from app.api.upload_basic import router as upload_basic_router
app.include_router(upload_basic_router, prefix="/api/v1/upload")

# Add history routes
from app.api.history import router as history_router
app.include_router(history_router)

# Add v1 API router (includes text-input, upload, sessions, etc.)
from app.api.v1.api import api_router
app.include_router(api_router, prefix="/api/v1")

# Add real content routes
from app.api.v1.endpoints.questions import router as questions_router
app.include_router(questions_router, prefix="/api/v1/questions")

# Add real results routes  
from app.api.questions_basic import router as questions_basic_router
app.include_router(questions_basic_router, prefix="/api/v1")

# Comment out mock routes - using real AI processing instead
# from app.api.mock_questions import router as mock_questions_router
# app.include_router(mock_questions_router, prefix="/api/v1/questions")

# from app.api.mock_tests import router as mock_tests_router
# app.include_router(mock_tests_router, prefix="/api/v1/mock-tests")

# from app.api.mock_content import router as mock_content_router
# app.include_router(mock_content_router, prefix="/api/v1/mnemonics")
# app.include_router(mock_content_router, prefix="/api/v1/cheat-sheets")
# app.include_router(mock_content_router, prefix="/api/v1/notes")

# Add S3 test routes
from app.api.s3_test import router as s3_test_router
app.include_router(s3_test_router, prefix="/api/v1/s3-test")

# Add simple upload routes - commented out due to missing dependencies
# from app.api.upload_simple import router as upload_simple_router
# app.include_router(upload_simple_router, prefix="/api/v1/upload")

# Add history routes - commented out due to missing dependencies  
# from app.api.history import router as history_router
# app.include_router(history_router)

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
