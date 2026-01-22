# Backend Documentation - Study Buddy App

## Overview

The Study Buddy backend is built with FastAPI, Python 3.12, and MongoDB. It provides a robust API for processing study materials and generating AI-powered educational content using Google Gemini API.

## Architecture

### Tech Stack
- **Framework**: FastAPI
- **Language**: Python 3.12
- **Database**: MongoDB
- **AI Service**: Google Gemini API
- **Authentication**: JWT with OTP verification
- **File Processing**: PyPDF2, Pillow, Tesseract OCR
- **Logging**: Python logging with file rotation

### Directory Structure

```
backend/app/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── logging_config.py      # Logging configuration
├── database.py            # MongoDB connection
├── models.py              # Pydantic models
├── auth_models_simple.py  # Authentication models
├── api/                   # API route handlers
│   ├── auth_simple.py     # Authentication endpoints
│   ├── upload_basic.py    # File upload endpoints
│   ├── history.py         # Session history endpoints
│   └── v1/                # API version 1 routes
├── services/              # Business logic services
│   ├── ai_service.py      # AI content generation
│   ├── auth_service.py    # Authentication logic
│   ├── content_aggregator.py    # Content compilation
│   ├── file_processor.py        # File processing
│   ├── file_service.py          # File management
│   ├── mock_test_generator.py   # Mock test creation
│   ├── otp_service.py           # OTP handling
│   ├── processing.py            # Main processing pipeline
│   ├── progress_tracker.py     # Progress tracking
│   └── upload_restrictions.py  # Upload validation
├── utils/                 # Utility functions
│   ├── db_helpers.py      # Database utilities
│   ├── error_handler.py   # Error handling
│   └── error_logger.py    # Error logging
├── middleware/            # Custom middleware
│   └── rate_limit.py      # Rate limiting
└── models/                # Database models (if using ODM)
```

## Core Services

### 1. Authentication Service (`services/auth_service.py`)

Handles user authentication with mobile OTP verification.

**Key Features:**
- Mobile-based registration and login
- OTP generation and verification
- JWT token management
- Password hashing with bcrypt

**Core Functions:**
```python
async def send_otp(mobile: str) -> bool
async def verify_otp(mobile: str, otp: str) -> bool
async def register_user(mobile: str, password: str, otp: str) -> User
async def authenticate_user(mobile: str, password: str) -> User
def create_access_token(user_id: str) -> str
```

### 2. File Processing Service (`services/file_processor.py`)

Handles file upload, validation, and text extraction.

**Supported File Types:**
- PDF documents (PyPDF2)
- Images (Tesseract OCR)
- PowerPoint presentations (python-pptx)

**Key Features:**
- File type validation
- Size limit enforcement (50MB)
- Text extraction with multiple methods
- Error handling and logging

**Core Functions:**
```python
async def process_uploaded_files(files: List[UploadFile], session_id: str) -> ProcessingResult
def extract_text_from_pdf(file_path: str) -> str
def extract_text_from_image(file_path: str) -> str
def extract_text_from_pptx(file_path: str) -> str
```

### 3. AI Service (`services/ai_service.py`)

Integrates with Google Gemini API for content generation.

**Content Types Generated:**
- Multiple Choice Questions (MCQs)
- Mock Tests
- Mnemonics (India-specific)
- Cheat Sheets
- Study Notes

**Key Features:**
- Structured prompt engineering
- Response parsing and validation
- Error handling and retries
- Content quality assurance

**Core Functions:**
```python
async def generate_questions(text: str, count: int = 25) -> List[Question]
async def generate_mock_test(questions: List[Question]) -> MockTest
async def generate_mnemonics(text: str) -> List[Mnemonic]
async def generate_cheat_sheet(text: str) -> CheatSheet
async def generate_notes(content: Dict) -> StudyNotes
```

### 4. Processing Pipeline (`services/processing.py`)

Main orchestration service that coordinates the entire processing workflow.

**Processing Steps:**
1. File validation and storage
2. Text extraction
3. Content analysis
4. AI content generation (parallel)
5. Results compilation and storage

**Key Features:**
- Asynchronous processing
- Progress tracking
- Error recovery
- Result caching

### 5. Progress Tracker (`services/progress_tracker.py`)

Tracks and reports processing progress in real-time.

**Features:**
- Step-by-step progress tracking
- Estimated completion time
- Error state management
- WebSocket support (future)

## Database Models

### User Model
```python
class User(BaseModel):
    id: Optional[str] = None
    mobile: str
    password_hash: str
    created_at: datetime
    is_active: bool = True
```

### Session Model
```python
class StudySession(BaseModel):
    id: Optional[str] = None
    session_id: str
    user_id: str
    session_name: str
    created_at: datetime
    files_uploaded: List[FileInfo]
    processing_status: ProcessingStatus
    results: Optional[SessionResults] = None
```

### Question Model
```python
class Question(BaseModel):
    id: Optional[str] = None
    session_id: str
    question_text: str
    options: List[QuestionOption]
    correct_answer: str
    explanation: str
    difficulty: DifficultyLevel
    subject: str
    tags: List[str]
```

### Mock Test Model
```python
class MockTest(BaseModel):
    id: Optional[str] = None
    session_id: str
    test_name: str
    questions: List[str]  # Question IDs
    duration_minutes: int
    total_marks: int
    created_at: datetime
```

## API Endpoints

### Authentication Endpoints (`api/auth_simple.py`)

#### Send OTP
```
POST /api/v1/auth/send-otp
Content-Type: application/json

{
  "mobile": "9876543210"
}

Response: 200 OK
{
  "message": "OTP sent successfully",
  "expires_in": 300
}
```

#### Verify OTP
```
POST /api/v1/auth/verify-otp
Content-Type: application/json

{
  "mobile": "9876543210",
  "otp": "123456"
}

Response: 200 OK
{
  "message": "OTP verified successfully",
  "valid": true
}
```

#### Register User
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "mobile": "9876543210",
  "password": "securepassword",
  "otp": "123456"
}

Response: 201 Created
{
  "user": {
    "id": "user_id",
    "mobile": "9876543210"
  },
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

#### Login User
```
POST /api/v1/auth/login
Content-Type: application/json

{
  "mobile": "9876543210",
  "password": "securepassword"
}

Response: 200 OK
{
  "user": {
    "id": "user_id",
    "mobile": "9876543210"
  },
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

### Upload Endpoints (`api/upload_basic.py`)

#### Upload Files
```
POST /api/v1/upload/
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- files: File[] (multiple files)
- session_name: string (optional)

Response: 200 OK
{
  "session_id": "uuid",
  "message": "Files uploaded successfully",
  "files_count": 3,
  "processing_started": true
}
```

#### Process Text Input
```
POST /api/v1/text-input/
Content-Type: application/json
Authorization: Bearer <token>

{
  "text": "Study material content...",
  "session_name": "Anatomy Chapter 1"
}

Response: 200 OK
{
  "session_id": "uuid",
  "message": "Text processing started",
  "processing_started": true
}
```

#### Get Processing Status
```
GET /api/v1/upload/status/{session_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "session_id": "uuid",
  "status": "processing",
  "progress": 65,
  "current_step": "Generating questions",
  "estimated_completion": "2026-01-23T10:30:00Z",
  "error": null
}
```

### History Endpoints (`api/history.py`)

#### Get Session History
```
GET /api/v1/history/sessions
Authorization: Bearer <token>

Response: 200 OK
{
  "sessions": [
    {
      "session_id": "uuid",
      "session_name": "Anatomy Chapter 1",
      "created_at": "2026-01-22T10:00:00Z",
      "status": "completed",
      "files_count": 2,
      "results_available": true
    }
  ],
  "total": 10,
  "page": 1,
  "per_page": 20
}
```

#### Get Session Results
```
GET /api/v1/history/sessions/{session_id}/results
Authorization: Bearer <token>

Response: 200 OK
{
  "session_id": "uuid",
  "results": {
    "questions": [...],
    "mock_tests": [...],
    "mnemonics": [...],
    "cheat_sheets": [...],
    "notes": {...}
  },
  "metadata": {
    "generated_at": "2026-01-22T10:30:00Z",
    "processing_time": 120
  }
}
```

#### Delete Session
```
DELETE /api/v1/history/sessions/{session_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "message": "Session deleted successfully"
}
```

## Configuration Management

### Environment Variables (`.env`)
```env
# Database
MONGODB_URL=mongodb://localhost:27017/studybuddy
DATABASE_NAME=studybuddy

# AI Service
GOOGLE_AI_API_KEY=your-gemini-api-key
GENAI_MODEL=gemini-1.5-flash

# Authentication
JWT_SECRET=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=52428800  # 50MB
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png,pptx

# OTP Service
OTP_EXPIRY_MINUTES=5
OTP_LENGTH=6

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/studybuddy.log

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

### Configuration Class (`config.py`)
```python
class Settings(BaseSettings):
    # Database settings
    mongodb_url: str = "mongodb://localhost:27017/studybuddy"
    database_name: str = "studybuddy"
    
    # AI settings
    google_ai_api_key: str
    genai_model: str = "gemini-1.5-flash"
    
    # Auth settings
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    
    # File settings
    upload_dir: str = "./uploads"
    max_file_size: int = 52428800
    allowed_extensions: List[str] = ["pdf", "jpg", "jpeg", "png", "pptx"]
    
    class Config:
        env_file = ".env"
```

## Error Handling

### Custom Exception Classes
```python
class StudyBuddyException(Exception):
    """Base exception for Study Buddy application"""
    pass

class AuthenticationError(StudyBuddyException):
    """Authentication related errors"""
    pass

class FileProcessingError(StudyBuddyException):
    """File processing related errors"""
    pass

class AIServiceError(StudyBuddyException):
    """AI service related errors"""
    pass
```

### Error Handler Middleware
```python
@app.exception_handler(StudyBuddyException)
async def studybuddy_exception_handler(request: Request, exc: StudyBuddyException):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "type": exc.__class__.__name__,
                "message": str(exc),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )
```

## Security Measures

### Authentication Security
- JWT token validation on protected routes
- Password hashing with bcrypt
- OTP-based verification
- Token expiration handling

### Input Validation
- Pydantic models for request validation
- File type and size validation
- SQL injection prevention (NoSQL)
- XSS prevention

### Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/auth/send-otp")
@limiter.limit("5/minute")
async def send_otp_endpoint(request: Request, ...):
    # OTP sending logic
```

## Logging and Monitoring

### Logging Configuration
```python
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/studybuddy.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["file"],
    },
}
```

### Performance Monitoring
- Request/response time tracking
- Database query performance
- AI service response times
- Error rate monitoring

## Testing Strategy

### Unit Testing
- Service layer testing
- Model validation testing
- Utility function testing
- Mock external dependencies

### Integration Testing
- API endpoint testing
- Database integration testing
- File processing pipeline testing
- Authentication flow testing

### Performance Testing
- Load testing with multiple concurrent users
- File processing performance benchmarks
- Database query optimization
- Memory usage monitoring

## Deployment

### Production Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MONGODB_URL="mongodb://production-host:27017/studybuddy"
export GOOGLE_AI_API_KEY="production-api-key"
export JWT_SECRET="production-jwt-secret"

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Configuration
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

## Performance Optimization

### Database Optimization
- Proper indexing on frequently queried fields
- Connection pooling
- Query optimization
- Aggregation pipeline usage

### Caching Strategy
- In-memory caching for frequently accessed data
- Redis integration for session storage
- AI response caching
- File processing result caching

### Async Processing
- Asynchronous file processing
- Concurrent AI API calls
- Background task processing
- Non-blocking I/O operations

## Troubleshooting

### Common Issues

1. **MongoDB Connection Issues**
   - Check MongoDB service status
   - Verify connection string
   - Check network connectivity

2. **AI Service Errors**
   - Verify API key validity
   - Check rate limits
   - Monitor API quotas

3. **File Processing Failures**
   - Check file permissions
   - Verify disk space
   - Validate file formats

4. **Authentication Problems**
   - Check JWT secret configuration
   - Verify token expiration
   - Validate OTP service

### Debug Tools
- FastAPI automatic documentation (`/docs`)
- Logging analysis
- Database query profiling
- API response monitoring

## Future Enhancements

### Planned Features
- WebSocket support for real-time updates
- Advanced caching with Redis
- Microservices architecture
- Advanced analytics and reporting

### Technical Improvements
- Celery for background task processing
- Advanced error recovery mechanisms
- Enhanced security measures
- Performance optimizations

## API Documentation

The backend automatically generates interactive API documentation using FastAPI's built-in Swagger UI, available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
