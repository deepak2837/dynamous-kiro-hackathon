from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List
import uuid
import os
import shutil
from datetime import datetime

from app.config import settings
from app.models import UploadRequest, UploadResponse, ProcessingMode, StudySession, SessionStatus
from app.database import get_database
from app.services.processing import ProcessingService

router = APIRouter()

@router.post("/", response_model=UploadResponse)
async def upload_files(
    files: List[UploadFile] = File(...),
    processing_mode: ProcessingMode = Form(ProcessingMode.DEFAULT),
    user_id: str = Form(...),  # In real app, this would come from JWT token
    db=Depends(get_database)
):
    """Upload files and start processing"""
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Validate files
    uploaded_files = []
    for file in files:
        # Check file size
        if file.size > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File {file.filename} is too large. Maximum size is {settings.max_file_size} bytes"
            )
        
        # Check file type
        allowed_types = ['.pdf', '.jpg', '.jpeg', '.png', '.pptx']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Allowed types: {allowed_types}"
            )
        
        # Save file
        file_path = os.path.join(settings.upload_dir, f"{session_id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        uploaded_files.append(file_path)
    
    # Generate session name
    session_name = f"Study Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # Create session record
    session = StudySession(
        session_id=session_id,
        user_id=user_id,
        session_name=session_name,
        files=uploaded_files,
        processing_mode=processing_mode,
        status=SessionStatus.PENDING
    )
    
    # Save to database
    await db.study_sessions.insert_one(session.dict())
    
    # Start async processing
    processing_service = ProcessingService()
    await processing_service.start_processing(session_id, uploaded_files, processing_mode, user_id)
    
    return UploadResponse(
        session_id=session_id,
        message="Files uploaded successfully. Processing started.",
        files_uploaded=len(uploaded_files)
    )

@router.get("/status/{session_id}")
async def get_processing_status(
    session_id: str,
    db=Depends(get_database)
):
    """Get processing status for a session"""
    
    session = await db.study_sessions.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "status": session["status"],
        "message": f"Session is {session['status']}",
        "error_message": session.get("error_message")
    }
