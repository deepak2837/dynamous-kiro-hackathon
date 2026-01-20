from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import uuid
import os
from datetime import datetime
from app.config import settings
from app.services.upload_restrictions import UploadRestrictionService
from app.utils.error_logger import error_logger

router = APIRouter()

@router.post("/")
async def upload_files(
    files: List[UploadFile] = File(...),
    processing_mode: str = Form("default"),
    user_id: str = Form("demo-user")
):
    """Upload files with restrictions"""
    
    try:
        # Check upload restrictions
        allowed, restriction_message, remaining_seconds = UploadRestrictionService.check_upload_allowed(user_id)
        if not allowed:
            raise HTTPException(
                status_code=429,
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
        
        # Create upload directory if it doesn't exist
        os.makedirs(settings.upload_dir, exist_ok=True)
        
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
            
            # Save file locally
            local_file_path = os.path.join(settings.upload_dir, f"{session_id}_{file.filename}")
            with open(local_file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            uploaded_files.append(local_file_path)
        
        # Record upload time for restrictions
        UploadRestrictionService.record_upload(user_id)
        
        return {
            "session_id": session_id,
            "message": "Files uploaded successfully. Processing started.",
            "files_uploaded": len(uploaded_files)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        error_logger.log_error(e, "upload_files", user_id, {"files_count": len(files), "processing_mode": processing_mode})
        raise HTTPException(
            status_code=500,
            detail="Internal server error during file upload"
        )

@router.get("/check-upload-allowed/{user_id}")
async def check_upload_allowed(user_id: str):
    """Check if user can upload files"""
    
    try:
        allowed, message, remaining_seconds = UploadRestrictionService.check_upload_allowed(user_id)
        
        return {
            "upload_allowed": allowed,
            "message": message,
            "remaining_seconds": remaining_seconds,
            "restriction_settings": UploadRestrictionService.get_cooldown_info()
        }
    except Exception as e:
        error_logger.log_error(e, "check_upload_allowed", user_id)
        raise HTTPException(
            status_code=500,
            detail="Error checking upload restrictions"
        )

@router.get("/file-limits")
async def get_file_limits():
    """Get file size limits for different file types"""
    try:
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
    except Exception as e:
        error_logger.log_error(e, "get_file_limits")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving file limits"
        )
