import os
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Database
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017/studybuddy")
    database_name: str = os.getenv("DATABASE_NAME", "studybuddy")
    
    # CORS Configuration
    allowed_origins: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    
    # AI Service
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    genai_project_id: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    google_cloud_project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "")
    google_cloud_location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    google_application_credentials: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # Authentication
    jwt_secret: str = os.getenv("JWT_SECRET_KEY") or os.getenv("JWT_SECRET", "")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiry: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) * 60  # 24 hours default
    
    def model_post_init(self, __context) -> None:
        if not self.jwt_secret or self.jwt_secret == "your-secret-key-change-in-production":
            raise ValueError("JWT_SECRET_KEY environment variable is required and cannot be default value")
    
    # OTP Service Configuration
    default_otp_method: str = os.getenv("DEFAULT_OTP_METHOD", "sms")  # "sms" or "email"
    
    # SMS Service (Fast2SMS)
    fast2sms_api_key: str = os.getenv("FAST2SMS_API_KEY", "")
    
    # Email Service (SMTP)
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    
    # Gmail API (Alternative to SMTP)
    gmail_api_key: str = os.getenv("GMAIL_API_KEY", "")
    
    # File Storage
    upload_dir: str = os.getenv("UPLOAD_DIR", "./uploads")
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50MB default
    max_images_per_upload: int = int(os.getenv("MAX_IMAGES_PER_UPLOAD", "25"))
    
    # File size limits (in bytes)
    max_pdf_size: int = int(os.getenv("MAX_PDF_SIZE", "50485760"))  # 48MB
    max_image_size: int = int(os.getenv("MAX_IMAGE_SIZE", "10485760"))  # 10MB  
    max_slide_size: int = int(os.getenv("MAX_SLIDE_SIZE", "104857600"))  # 100MB
    
    # Upload restrictions
    upload_cooldown_minutes: int = int(os.getenv("UPLOAD_COOLDOWN_MINUTES", "5"))
    enable_upload_restrictions: bool = os.getenv("ENABLE_UPLOAD_RESTRICTIONS", "true").lower() == "true"
    
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "StudyBuddy"
    version: str = "1.0.0"
    description: str = "AI-powered study companion for medical students"
    
    # Upload Restrictions
    restrict_upload_timing: bool = os.getenv("RESTRICT_UPLOAD_TIMING", "true").lower() == "true"
    
    # Rate Limiting
    enable_rate_limiting: bool = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
    
    # AWS S3 Configuration
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "ap-south-1")
    study_buddy_bucket_name: str = os.getenv("STUDY_BUDDY_BUCKET_NAME", "")
    storage_mode: str = os.getenv("STORAGE_MODE", "LOCAL").upper()
    
    # Legacy compatibility properties
    @property
    def JWT_SECRET(self):
        return self.jwt_secret
    
    @property
    def JWT_ALGORITHM(self):
        return self.jwt_algorithm
    
    @property
    def FAST2SMS_API_KEY(self):
        return self.fast2sms_api_key
    
    @property
    def SMTP_SERVER(self):
        return self.smtp_server
    
    @property
    def SMTP_PORT(self):
        return self.smtp_port
    
    @property
    def SMTP_USERNAME(self):
        return self.smtp_username
    
    @property
    def SMTP_PASSWORD(self):
        return self.smtp_password
    
    @property
    def DEFAULT_OTP_METHOD(self):
        return self.default_otp_method
    
    class Config:
        env_file = ".env"
        extra = "forbid"  # Prevent typos in environment variables

settings = Settings()
