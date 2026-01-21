"""
Test endpoint for AI_ONLY processing without authentication
"""
from fastapi import APIRouter, File, UploadFile, Form
from typing import List
import uuid
import os
import shutil
from datetime import datetime

from app.models import ProcessingMode, StudySession, SessionStatus
from app.database import get_database
from app.services.processing import ProcessingService
from app.config import settings

router = APIRouter()

@router.post("/test-ai-only")
async def test_ai_only_upload(
    files: List[UploadFile] = File(...),
    processing_mode: ProcessingMode = Form(ProcessingMode.AI_ONLY)
):
    """Test AI_ONLY processing without authentication"""
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    user_id = "test_user"
    
    print(f"🧪 TEST AI_ONLY UPLOAD")
    print(f"📋 Session ID: {session_id}")
    print(f"🤖 Processing Mode: {processing_mode}")
    print(f"📁 Files: {len(files)}")
    
    # Save files
    uploaded_files = []
    for file in files:
        local_file_path = os.path.join(settings.upload_dir, f"{session_id}_{file.filename}")
        with open(local_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded_files.append(local_file_path)
        print(f"   Saved: {file.filename}")
    
    # Create session record
    db = get_database()
    session = StudySession(
        session_id=session_id,
        user_id=user_id,
        session_name=f"Test AI_ONLY Session {datetime.now().strftime('%H:%M')}",
        files=uploaded_files,
        file_urls=uploaded_files,
        file_paths=uploaded_files,  # This is what FileUploadProcessingService expects
        s3_keys=[],
        processing_mode=processing_mode,
        status=SessionStatus.PENDING,
        last_upload_time=datetime.utcnow()
    )
    
    await db.study_sessions.insert_one(session.dict())
    print(f"✅ Created session in database")
    
    # Start processing
    processing_service = ProcessingService()
    print(f"🚀 Starting processing with mode: {processing_mode}")
    await processing_service.start_processing(session_id, uploaded_files, processing_mode, user_id)
    
    return {
        "session_id": session_id,
        "message": "AI_ONLY processing started",
        "files_uploaded": len(uploaded_files),
        "processing_mode": str(processing_mode)
    }
