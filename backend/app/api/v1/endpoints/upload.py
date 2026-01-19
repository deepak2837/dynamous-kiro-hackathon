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
from app.services.upload_restrictions import UploadRestrictionService
from app.services.s3_service import s3_service

router = APIRouter()

@router.post("/", response_model=UploadResponse)
async def upload_files(
    files: List[UploadFile] = File(...),
    processing_mode: ProcessingMode = Form(ProcessingMode.DEFAULT),
    user_id: str = Form(...),  # In real app, this would come from JWT token
    db=Depends(get_database)
):
    """Upload files and start processing"""
    
    # Check upload restrictions
    allowed, restriction_message, remaining_seconds = await UploadRestrictionService.check_upload_allowed(user_id)
    if not allowed:
        raise HTTPException(
            status_code=429,  # Too Many Requests
            detail={
                "message": restriction_message,
                "remaining_seconds": remaining_seconds,
                "restriction_active": True
            }
        )
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Validate files and save them
    uploaded_files = []
    file_urls = []
    s3_keys = []
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    
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
        
        # Save file locally first
        local_file_path = os.path.join(settings.upload_dir, f"{session_id}_{file.filename}")
        with open(local_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Upload to S3 or keep local based on storage mode
        file_url, s3_key = await s3_service.upload_file(local_file_path, session_id, file.filename)
        
        uploaded_files.append(local_file_path if not s3_service.is_s3_enabled() else file_url)
        file_urls.append(file_url)
        s3_keys.append(s3_key)
    
    # Generate session name
    session_name = f"Study Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # Create session record
    session = StudySession(
        session_id=session_id,
        user_id=user_id,
        session_name=session_name,
        files=uploaded_files,
        file_urls=file_urls,
        s3_keys=s3_keys,
        processing_mode=processing_mode,
        status=SessionStatus.PENDING,
        last_upload_time=datetime.utcnow()
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

@router.get("/check-upload-allowed/{user_id}")
async def check_upload_allowed(user_id: str):
    """Check if user can upload files"""
    
    allowed, message, remaining_seconds = await UploadRestrictionService.check_upload_allowed(user_id)
    
    return {
        "upload_allowed": allowed,
        "message": message,
        "remaining_seconds": remaining_seconds,
        "restriction_settings": {
            "enabled": settings.restrict_upload_timing,
            "cooldown_minutes": settings.upload_cooldown_minutes
        }
    }

@router.get("/storage-info")
async def get_storage_info():
    """Get current storage configuration"""
    return {
        "storage_mode": s3_service.storage_mode,
        "s3_enabled": s3_service.is_s3_enabled(),
        "bucket_name": s3_service.bucket_name if s3_service.is_s3_enabled() else None,
        "region": s3_service.aws_region if s3_service.is_s3_enabled() else None
    }
