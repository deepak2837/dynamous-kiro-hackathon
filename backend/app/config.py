from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    mongodb_url: str = "mongodb://localhost:27017/medgloss"
    database_name: str = "medgloss"
    
    # AI Service
    google_ai_api_key: str
    genai_project_id: Optional[str] = None
    
    # Authentication
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiry: int = 86400
    
    # File Storage
    upload_dir: str = "./uploads"
    max_file_size: int = 52428800  # 50MB
    
    # OCR Scripts
    ocr_scripts_path: str = "/home/unknown/Documents/medgloss-data-extractorfiles"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "StudyBuddy"
    version: str = "1.0.0"
    description: str = "AI-powered study companion for medical students"
    
    class Config:
        env_file = ".env"

settings = Settings()
