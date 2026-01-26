"""
Study Buddy App - Configuration Settings

This module defines the application configuration using Pydantic Settings
for type-safe environment variable management and validation.

Configuration includes:
- Database connection settings (MongoDB)
- AI service credentials (Google Gemini API)
- Authentication settings (JWT)
- File storage configuration
- Email/SMS service settings
- CORS and security settings

All settings are loaded from environment variables with sensible defaults
and validation to ensure proper application startup.

Author: Study Buddy Team
Created: January 2026
License: MIT
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    This class defines all configuration options for the Study Buddy App
    with type validation and default values. Settings are automatically
    loaded from environment variables or .env file.
    
    Attributes:
        Database settings: MongoDB connection and database name
        AI service: Google Gemini API configuration
        Authentication: JWT token settings
        File storage: Upload directory and limits
        Communication: Email and SMS service settings
        Security: CORS origins and rate limiting
    """
    
    # Core API Configuration
    google_ai_api_key: str
    
    # Database Configuration
    mongodb_url: str = os.getenv("MONGODB_URL")
    database_name: str = os.getenv("DATABASE_NAME", "studybuddy")
    
    # CORS Configuration - Frontend origins allowed to access API
    allowed_origins: list = [
        "http://localhost:3000", 
        "http://localhost:3001", 
        "https://study-material-generator.netlify.app"
    ]
    
    # AI Service Configuration - Google Gemini API
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    genai_project_id: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    google_cloud_project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "")
    google_cloud_location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    google_application_credentials: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # Authentication Configuration - JWT tokens
    jwt_secret: str = os.getenv("JWT_SECRET_KEY") or os.getenv("JWT_SECRET", "")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiry: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) * 60  # 24 hours default
    
    def model_post_init(self, __context) -> None:
        """
        Validate configuration after initialization.
        
        Ensures critical settings like JWT secret are properly configured
        and not using default/insecure values.
        
        Raises:
            ValueError: If JWT secret is missing or using default value
        """
        if not self.jwt_secret or self.jwt_secret == "your-secret-key-change-in-production":
            raise ValueError("JWT_SECRET_KEY environment variable is required and cannot be default value")
    
    # OTP Service Configuration - For user authentication
    default_otp_method: str = os.getenv("DEFAULT_OTP_METHOD", "sms")  # "sms" or "email"
    
    # SMS Service Configuration (Fast2SMS)
    fast2sms_api_key: str = os.getenv("FAST2SMS_API_KEY", "")
    
    # Email Service Configuration (SMTP)
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    
    # Gmail API Configuration (Alternative to SMTP)
    gmail_api_key: str = os.getenv("GMAIL_API_KEY", "")
    
    # Redis Configuration (Optional)
    ENABLE_REDIS_CACHE: bool = Field(default=False, env="ENABLE_REDIS_CACHE")
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: str = Field(default="", env="REDIS_PASSWORD")
    REDIS_TIMEOUT: int = Field(default=5, env="REDIS_TIMEOUT")
    upload_dir: str = os.getenv("UPLOAD_DIR", "./uploads")
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50MB default
    max_images_per_upload: int = int(os.getenv("MAX_IMAGES_PER_UPLOAD", "25"))
    
    # File size limits (in bytes) - Medical study materials
    max_pdf_size: int = int(os.getenv("MAX_PDF_SIZE", "50485760"))  # 48MB for medical textbooks
    max_image_size: int = int(os.getenv("MAX_IMAGE_SIZE", "10485760"))  # 10MB for medical images/diagrams
    max_slide_size: int = int(os.getenv("MAX_SLIDE_SIZE", "104857600"))  # 100MB for presentation files
    
    # Upload restrictions - Rate limiting for API protection
    upload_cooldown_minutes: int = int(os.getenv("UPLOAD_COOLDOWN_MINUTES", "5"))
    enable_upload_restrictions: bool = os.getenv("ENABLE_UPLOAD_RESTRICTIONS", "true").lower() == "true"
    
    # API Configuration - Application metadata
    api_v1_str: str = "/api/v1"
    project_name: str = "StudyBuddy"
    version: str = "1.0.0"
    description: str = "AI-powered study companion for medical students"
    
    # Upload Restrictions - Timing controls
    restrict_upload_timing: bool = os.getenv("RESTRICT_UPLOAD_TIMING", "true").lower() == "true"
    
    # Rate Limiting - API protection
    enable_rate_limiting: bool = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
    
    # AWS S3 Configuration - Cloud storage (optional)
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "ap-south-1")
    study_buddy_bucket_name: str = os.getenv("STUDY_BUDDY_BUCKET_NAME", "")
    storage_mode: str = os.getenv("STORAGE_MODE", "LOCAL").upper()
    
    # Legacy compatibility properties for backward compatibility
    @property
    def JWT_SECRET(self):
        """Legacy property for JWT secret access."""
        return self.jwt_secret
    
    @property
    def JWT_ALGORITHM(self):
        """Legacy property for JWT algorithm access."""
        return self.jwt_algorithm
    
    @property
    def FAST2SMS_API_KEY(self):
        """Legacy property for SMS service API key."""
        return self.fast2sms_api_key
    
    @property
    def SMTP_SERVER(self):
        """Legacy property for SMTP server configuration."""
        return self.smtp_server
    
    @property
    def SMTP_PORT(self):
        """Legacy property for SMTP port configuration."""
        return self.smtp_port
    
    @property
    def SMTP_USERNAME(self):
        """Legacy property for SMTP username."""
        return self.smtp_username
    
    @property
    def SMTP_PASSWORD(self):
        """Legacy property for SMTP password."""
        return self.smtp_password
    
    @property
    def DEFAULT_OTP_METHOD(self):
        """Legacy property for default OTP method."""
        return self.default_otp_method
    
    class Config:
        """Pydantic configuration for settings validation."""
        env_file = ".env"
        extra = "forbid"  # Prevent typos in environment variables

# Global settings instance
settings = Settings()
