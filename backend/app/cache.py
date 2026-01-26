# Redis configuration for Study Buddy App
# Optional caching layer - disabled by default

import redis.asyncio as redis
from typing import Optional
import json
import os
from app.config import settings

class RedisManager:
    """Redis connection manager with optional functionality"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = settings.ENABLE_REDIS_CACHE
        
    async def connect(self):
        """Connect to Redis if enabled"""
        if not self.enabled:
            return
            
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            # Test connection
            await self.redis_client.ping()
        except Exception:
            # Fallback to disabled mode if Redis unavailable
            self.enabled = False
            self.redis_client = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if not self.enabled or not self.redis_client:
            return None
        try:
            return await self.redis_client.get(key)
        except Exception:
            return None
    
    async def set(self, key: str, value: str, expire: int = 3600):
        """Set value in cache"""
        if not self.enabled or not self.redis_client:
            return
        try:
            await self.redis_client.setex(key, expire, value)
        except Exception:
            pass
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.enabled or not self.redis_client:
            return
        try:
            await self.redis_client.delete(key)
        except Exception:
            pass

# Global Redis instance
redis_manager = RedisManager()

# Cache decorators
def cache_result(expire: int = 3600):
    """Decorator to cache function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if not redis_manager.enabled:
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = await redis_manager.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await redis_manager.set(cache_key, json.dumps(result), expire)
            return result
        return wrapper
    return decorator
