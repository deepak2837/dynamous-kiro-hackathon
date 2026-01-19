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
    
    # AI Service
    google_ai_api_key: str = os.getenv("GEMINI_API_KEY", "")
    genai_project_id: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    google_cloud_project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "")
    google_cloud_location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    google_application_credentials: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # Authentication
    jwt_secret: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiry: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")) * 60  # Convert to seconds
    
    # File Storage
    upload_dir: str = os.getenv("UPLOAD_DIR", "./uploads")
    max_file_size: int = 52428800  # 50MB
    
    # OCR Scripts
    ocr_scripts_path: str = "/home/unknown/Documents/medgloss-data-extractorfiles"
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "StudyBuddy"
    version: str = "1.0.0"
    description: str = "AI-powered study companion for medical students"
    
    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields from environment

settings = Settings()
