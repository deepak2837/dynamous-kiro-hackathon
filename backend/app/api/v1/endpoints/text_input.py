"""
Text-only input endpoint for processing topics without file uploads.
Allows users to generate study materials from a topic name.
"""

from fastapi import APIRouter, HTTPException, Depends, Form, BackgroundTasks
from typing import Optional
import uuid
from datetime import datetime

from app.config import settings
from app.models import UploadResponse, ProcessingMode, InputType, StudySession, SessionStatus
from app.database import get_database
from app.services.processing import ProcessingService
from app.services.progress_tracker import ProgressTracker

router = APIRouter()

@router.post("/", response_model=UploadResponse)
async def process_text_input(
    background_tasks: BackgroundTasks,
    topic: str = Form(..., description="Topic to generate content about"),
    user_id: str = Form(..., description="User identifier"),
    db=Depends(get_database)
):
    """
    Process text-only input to generate study materials.
    
    This endpoint allows users to enter a topic (e.g., "Heart anatomy", "Diabetes management")
    and generate all 5 content types without uploading any files.
    """
    
    if not topic or len(topic.strip()) < 3:
        raise HTTPException(
            status_code=400,
            detail="Topic must be at least 3 characters long"
        )
    
    if len(topic) > 500:
        raise HTTPException(
            status_code=400,
            detail="Topic must be less than 500 characters"
        )
    
    # Generate session ID and name
    session_id = str(uuid.uuid4())
    session_name = f"Topic: {topic[:50]}{'...' if len(topic) > 50 else ''}"
    
    # Create session record
    session = StudySession(
        session_id=session_id,
        user_id=user_id,
        session_name=session_name,
        files=[],
        file_urls=[],
        s3_keys=[],
        processing_mode=ProcessingMode.AI_ONLY,
        input_type=InputType.TEXT_INPUT,
        text_input=topic.strip(),
        status=SessionStatus.PENDING
    )
    
    # Save to database
    await db.study_sessions.insert_one(session.dict())
    
    # Start background processing
    processing_service = ProcessingService()
    background_tasks.add_task(
        processing_service.process_text_input,
        session_id,
        topic.strip(),
        user_id
    )
    
    return UploadResponse(
        session_id=session_id,
        message=f"Processing started for topic: {topic[:50]}{'...' if len(topic) > 50 else ''}",
        files_uploaded=0
    )


@router.get("/examples")
async def get_topic_examples():
    """Get example topics for text input"""
    return {
        "examples": [
            "Heart anatomy and physiology",
            "Diabetes mellitus types and management",
            "Cranial nerves and their functions",
            "Respiratory system pathology",
            "Pharmacology of antibiotics",
            "Thyroid disorders",
            "Cardiac arrhythmias",
            "Kidney function and diseases"
        ],
        "tips": [
            "Be specific: 'Cardiac muscle contraction' is better than 'Heart'",
            "Include context: 'Diabetes management in elderly patients'",
            "You can ask about specific conditions, drugs, or anatomical structures"
        ]
    }
