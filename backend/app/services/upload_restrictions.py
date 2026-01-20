from datetime import datetime, timedelta
from typing import Dict, Tuple
from app.config import settings

class UploadRestrictionService:
    """Service to manage upload restrictions and cooldowns"""
    
    # In-memory store for user upload times (use Redis in production)
    _user_uploads: Dict[str, datetime] = {}
    
    @classmethod
    def check_upload_allowed(cls, user_id: str) -> Tuple[bool, str, int]:
        """
        Check if user can upload files
        Returns: (allowed, message, remaining_seconds)
        """
        if not settings.enable_upload_restrictions:
            return True, "Upload allowed", 0
        
        last_upload = cls._user_uploads.get(user_id)
        if not last_upload:
            return True, "Upload allowed", 0
        
        cooldown_delta = timedelta(minutes=settings.upload_cooldown_minutes)
        next_allowed_time = last_upload + cooldown_delta
        current_time = datetime.utcnow()
        
        if current_time >= next_allowed_time:
            return True, "Upload allowed", 0
        
        remaining_seconds = int((next_allowed_time - current_time).total_seconds())
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        
        if minutes > 0:
            message = f"Please wait {minutes} minute(s) and {seconds} second(s) before uploading again"
        else:
            message = f"Please wait {seconds} second(s) before uploading again"
        
        return False, message, remaining_seconds
    
    @classmethod
    def record_upload(cls, user_id: str):
        """Record successful upload time for user"""
        cls._user_uploads[user_id] = datetime.utcnow()
    
    @classmethod
    def get_cooldown_info(cls) -> dict:
        """Get current cooldown configuration"""
        return {
            "enabled": settings.enable_upload_restrictions,
            "cooldown_minutes": settings.upload_cooldown_minutes
        }
