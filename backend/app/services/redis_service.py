# Redis Session Storage (Optional)
# Provides session caching when Redis is enabled

from typing import Optional, Dict, Any
import json
from datetime import datetime, timedelta
from app.cache import redis_manager

class SessionCache:
    """Session caching with Redis backend"""
    
    @staticmethod
    async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """Get session from cache"""
        if not redis_manager.enabled:
            return None
            
        cached = await redis_manager.get(f"session:{session_id}")
        if cached:
            return json.loads(cached)
        return None
    
    @staticmethod
    async def set_session(session_id: str, session_data: Dict[str, Any], expire: int = 3600):
        """Cache session data"""
        if not redis_manager.enabled:
            return
            
        await redis_manager.set(
            f"session:{session_id}", 
            json.dumps(session_data, default=str), 
            expire
        )
    
    @staticmethod
    async def delete_session(session_id: str):
        """Remove session from cache"""
        if not redis_manager.enabled:
            return
            
        await redis_manager.delete(f"session:{session_id}")

class UserCache:
    """User data caching"""
    
    @staticmethod
    async def get_user_sessions(user_id: str) -> Optional[list]:
        """Get cached user sessions"""
        if not redis_manager.enabled:
            return None
            
        cached = await redis_manager.get(f"user_sessions:{user_id}")
        if cached:
            return json.loads(cached)
        return None
    
    @staticmethod
    async def set_user_sessions(user_id: str, sessions: list, expire: int = 1800):
        """Cache user sessions"""
        if not redis_manager.enabled:
            return
            
        await redis_manager.set(
            f"user_sessions:{user_id}", 
            json.dumps(sessions, default=str), 
            expire
        )
    
    @staticmethod
    async def invalidate_user_cache(user_id: str):
        """Clear user cache"""
        if not redis_manager.enabled:
            return
            
        await redis_manager.delete(f"user_sessions:{user_id}")

class AICache:
    """AI response caching to avoid regeneration"""
    
    @staticmethod
    async def get_ai_response(content_hash: str, request_type: str) -> Optional[Dict[str, Any]]:
        """Get cached AI response"""
        if not redis_manager.enabled:
            return None
            
        cached = await redis_manager.get(f"ai:{request_type}:{content_hash}")
        if cached:
            return json.loads(cached)
        return None
    
    @staticmethod
    async def set_ai_response(content_hash: str, request_type: str, response: Dict[str, Any], expire: int = 86400):
        """Cache AI response for 24 hours"""
        if not redis_manager.enabled:
            return
            
        await redis_manager.set(
            f"ai:{request_type}:{content_hash}", 
            json.dumps(response, default=str), 
            expire
        )
