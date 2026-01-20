from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.s3_service import s3_service
import tempfile
import os

router = APIRouter()

@router.post("/test-s3")
async def test_s3_upload(file: UploadFile = File(...)):
    """Test S3 upload functionality"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Test upload to S3
        file_url, s3_key = await s3_service.upload_file(
            temp_file_path, 
            "test-session", 
            file.filename
        )
        
        # Clean up temp file if it still exists
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        return {
            "success": True,
            "storage_mode": s3_service.storage_mode,
            "s3_enabled": s3_service.is_s3_enabled(),
            "file_url": file_url,
            "s3_key": s3_key,
            "original_filename": file.filename
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "storage_mode": s3_service.storage_mode,
            "s3_enabled": s3_service.is_s3_enabled()
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
