from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Body
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
from app.services.progress_tracker import ProgressTracker
from app.services.s3_service import s3_service
from app.middleware.rate_limit import upload_rate_limit, api_rate_limit
from fastapi import Request

router = APIRouter()

@router.get("/file-limits")
async def get_file_limits():
    """Get file size limits"""
    return {
        "pdf": {"max_size_mb": 50, "description": "PDF documents up to 50MB"},
        "image": {"max_size_mb": 10, "description": "Images up to 10MB"},
        "slide": {"max_size_mb": 100, "description": "Presentation files up to 100MB"}
    }

@router.post("/", response_model=UploadResponse)
@upload_rate_limit()
async def upload_files(
    request: Request,
    files: List[UploadFile] = File(...),
    processing_mode: ProcessingMode = Form(ProcessingMode.OCR_AI),
    user_id: str = Form(...),  # In real app, this would come from JWT token
    db=Depends(get_database)
):
    """Upload files and start processing"""
    
    # Check upload restrictions
    allowed, restriction_message, remaining_seconds = UploadRestrictionService.check_upload_allowed(user_id)
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
    image_count = 0
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # First pass: count images and validate file types
    for file in files:
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        # Count images
        if file_ext in ['.jpg', '.jpeg', '.png']:
            image_count += 1
    
    # Check image limit
    if image_count > settings.max_images_per_upload:
        raise HTTPException(
            status_code=400,
            detail=f"Too many images. Maximum {settings.max_images_per_upload} images allowed per upload. You selected {image_count} images."
        )
    
    # Second pass: process files
    for file in files:
        # Get file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        # Check file type and size limits
        allowed_types = {
            '.pdf': settings.max_pdf_size,
            '.jpg': settings.max_image_size, 
            '.jpeg': settings.max_image_size,
            '.png': settings.max_image_size,
            '.pptx': settings.max_slide_size,
            '.ppt': settings.max_slide_size
        }
        
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{file_ext}' not supported. Allowed types: PDF, JPG, PNG, PPTX"
            )
        
        max_size = allowed_types[file_ext]
        if file.size > max_size:
            # Convert bytes to MB for user-friendly message
            max_size_mb = max_size / (1024 * 1024)
            file_size_mb = file.size / (1024 * 1024)
            
            file_type_name = {
                '.pdf': 'PDF',
                '.jpg': 'Image', 
                '.jpeg': 'Image',
                '.png': 'Image',
                '.pptx': 'Slide',
                '.ppt': 'Slide'
            }[file_ext]
            
            raise HTTPException(
                status_code=413,
                detail=f"{file_type_name} file '{file.filename}' is too large ({file_size_mb:.1f}MB). Maximum allowed size for {file_type_name.lower()} files is {max_size_mb:.0f}MB."
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
    
    # Record upload time for restrictions
    UploadRestrictionService.record_upload(user_id)
    
    # Start async processing
    processing_service = ProcessingService()
    await processing_service.start_processing(session_id, uploaded_files, processing_mode, user_id)
    
    return UploadResponse(
        session_id=session_id,
        message="Files uploaded successfully. Processing started.",
        files_uploaded=len(uploaded_files)
    )

@router.get("/status/{session_id}")
@api_rate_limit()
async def get_processing_status(
    request: Request,
    session_id: str,
    db=Depends(get_database)
):
    """Get detailed processing status for a session"""
    
    session = await db.study_sessions.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get detailed progress information
    progress = await ProgressTracker.get_progress(session_id)
    
    return {
        "session_id": session_id,
        "status": session["status"],
        "progress": progress.dict() if progress else None,
        "message": session.get("step_message", f"Session is {session['status']}"),
        "error_message": session.get("error_message"),
        "email_notification_enabled": session.get("email_notification_enabled", False)
    }

@router.post("/enable-notification/{session_id}")
@api_rate_limit()
async def enable_email_notification(
    request: Request,
    session_id: str,
    email: str = Body(..., embed=True),
    db=Depends(get_database)
):
    """Enable email notification for session completion"""
    
    # Verify session exists
    session = await db.study_sessions.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Enable email notification
    success = await ProgressTracker.enable_email_notification(session_id, email)
    
    if success:
        return {"message": "Email notification enabled", "email": email}
    else:
        raise HTTPException(status_code=500, detail="Failed to enable email notification")

@router.get("/check-upload-allowed/{user_id}")
async def check_upload_allowed(user_id: str):
    """Check if user can upload files"""
    
    allowed, message, remaining_seconds = UploadRestrictionService.check_upload_allowed(user_id)
    
    return {
        "upload_allowed": allowed,
        "message": message,
        "remaining_seconds": remaining_seconds,
        "restriction_settings": UploadRestrictionService.get_cooldown_info()
    }

@router.get("/file-limits")
async def get_file_limits():
    """Get file size limits for different file types"""
    return {
        "limits": {
            "pdf": {
                "max_size_bytes": settings.max_pdf_size,
                "max_size_mb": settings.max_pdf_size / (1024 * 1024),
                "description": "PDF documents"
            },
            "image": {
                "max_size_bytes": settings.max_image_size,
                "max_size_mb": settings.max_image_size / (1024 * 1024),
                "description": "Images (JPG, PNG)"
            },
            "slide": {
                "max_size_bytes": settings.max_slide_size,
                "max_size_mb": settings.max_slide_size / (1024 * 1024),
                "description": "Presentations (PPTX, PPT)"
            }
        },
        "supported_types": ["pdf", "jpg", "jpeg", "png", "pptx", "ppt"]
    }

@router.get("/storage-info")
@api_rate_limit()
async def get_storage_info(request: Request):
    """Get current storage configuration"""
    return {
        "storage_mode": s3_service.storage_mode,
        "s3_enabled": s3_service.is_s3_enabled(),
        "bucket_name": s3_service.bucket_name if s3_service.is_s3_enabled() else None,
        "region": s3_service.aws_region if s3_service.is_s3_enabled() else None
    }
