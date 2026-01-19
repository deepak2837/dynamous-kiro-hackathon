from datetime import datetime, timedelta
from typing import Optional, Tuple
from app.config import settings
from app.models import SessionStatus
from app.database import get_database

class UploadRestrictionService:
    """Service to handle upload timing restrictions"""
    
    @staticmethod
    async def check_upload_allowed(user_id: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Check if user is allowed to upload files
        
        Returns:
            Tuple[bool, Optional[str], Optional[int]]: 
            - allowed: Whether upload is allowed
            - message: Error message if not allowed
            - remaining_seconds: Remaining cooldown time in seconds
        """
        if not settings.restrict_upload_timing:
            return True, None, None
        
        db = await get_database()
        
        # Check for active processing sessions
        active_session = await db.study_sessions.find_one({
            "user_id": user_id,
            "status": {"$in": [SessionStatus.PENDING, SessionStatus.PROCESSING]}
        })
        
        if active_session:
            return False, "Please wait for current processing to complete before uploading new files", None
        
        # Check cooldown period
        cooldown_time = timedelta(minutes=settings.upload_cooldown_minutes)
        cutoff_time = datetime.utcnow() - cooldown_time
        
        recent_session = await db.study_sessions.find_one({
            "user_id": user_id,
            "last_upload_time": {"$gt": cutoff_time}
        }, sort=[("last_upload_time", -1)])
        
        if recent_session:
            last_upload = recent_session.get("last_upload_time")
            if isinstance(last_upload, datetime):
                time_since_upload = datetime.utcnow() - last_upload
                remaining_time = cooldown_time - time_since_upload
                
                if remaining_time.total_seconds() > 0:
                    remaining_minutes = int(remaining_time.total_seconds() // 60)
                    remaining_seconds = int(remaining_time.total_seconds() % 60)
                    
                    if remaining_minutes > 0:
                        message = f"Please wait {remaining_minutes} minute(s) and {remaining_seconds} second(s) before uploading again"
                    else:
                        message = f"Please wait {remaining_seconds} second(s) before uploading again"
                    
                    return False, message, int(remaining_time.total_seconds())
        
        return True, None, None
    
    @staticmethod
    async def update_last_upload_time(user_id: str, session_id: str):
        """Update the last upload time for a user's session"""
        db = await get_database()
        await db.study_sessions.update_one(
            {"session_id": session_id, "user_id": user_id},
            {"$set": {"last_upload_time": datetime.utcnow()}}
        )
