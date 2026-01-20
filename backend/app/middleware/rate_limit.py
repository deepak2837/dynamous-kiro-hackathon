from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from app.config import settings

# Create limiter instance with in-memory storage (no Redis)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000/hour"]  # Global default limit
)

# Custom rate limit exceeded handler
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return {
        "error": "Rate limit exceeded",
        "detail": f"Rate limit exceeded: {exc.detail}",
        "retry_after": exc.retry_after
    }

# Rate limiting decorators for different endpoints
def auth_rate_limit():
    """Rate limit for auth endpoints: 10 requests per minute"""
    return limiter.limit("10/minute")

def upload_rate_limit():
    """Rate limit for upload endpoints: 5 requests per minute"""
    return limiter.limit("5/minute")

def api_rate_limit():
    """Rate limit for general API endpoints: 100 requests per minute"""
    return limiter.limit("100/minute")

def heavy_rate_limit():
    """Rate limit for heavy operations: 2 requests per minute"""
    return limiter.limit("2/minute")
