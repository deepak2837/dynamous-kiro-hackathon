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

# File Storage Configuration
FILE_STORAGE_TYPE=local  # Options: local, s3
UPLOAD_DIR=./uploads

# AWS S3 Configuration (if FILE_STORAGE_TYPE=s3)
AWS_S3_BUCKET=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1

# File Upload Limits
MAX_FILE_SIZE=52428800  # 50MB in bytes
MAX_FILES_PER_UPLOAD=10
ALLOWED_FILE_TYPES=pdf,jpg,jpeg,png,pptx

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# OTP Service
OTP_EXPIRY_MINUTES=5
OTP_LENGTH=6

# Email Notification System
ENABLE_EMAIL_NOTIFICATIONS=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=studybuddy@yourapp.com
NOTIFY_ON_COMPLETION=true
NOTIFY_ON_ERROR=true
EMAIL_TEMPLATE_PATH=./templates/emails/

# Mock Test Configuration
MOCK_TEST_DURATION_MINUTES=60
QUESTIONS_PER_TEST=25
ENABLE_TEST_RETRIES=true

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
    
    # File storage settings
    file_storage_type: str = "local"  # local or s3
    upload_dir: str = "./uploads"
    
    # AWS S3 settings (if using S3)
    aws_s3_bucket: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    
    # File upload limits
    max_file_size: int = 52428800  # 50MB
    max_files_per_upload: int = 10
    allowed_file_types: List[str] = ["pdf", "jpg", "jpeg", "png", "pptx"]
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000
    
    # Mock test settings
    mock_test_duration_minutes: int = 60
    questions_per_test: int = 25
    enable_test_retries: bool = True
    
    # Email notification settings
    enable_email_notifications: bool = False
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: str = "studybuddy@yourapp.com"
    notify_on_completion: bool = True
    notify_on_error: bool = True
    email_template_path: str = "./templates/emails/"
    
    class Config:
        env_file = ".env"
```

## Email Notification System

### Email Service Implementation
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template

class EmailService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.enabled = settings.enable_email_notifications
    
    async def send_processing_complete_email(self, user_email: str, session_id: str, session_name: str):
        if not self.enabled:
            return
        
        template = self._load_template("processing_complete.html")
        html_content = template.render(
            session_name=session_name,
            results_link=f"http://localhost:3000/results/{session_id}",
            user_name=user_email.split('@')[0]
        )
        
        await self._send_email(
            to_email=user_email,
            subject=f"✅ Study Materials Ready - {session_name}",
            html_content=html_content
        )
    
    async def send_processing_error_email(self, user_email: str, session_name: str, error_message: str):
        if not self.enabled or not self.settings.notify_on_error:
            return
        
        template = self._load_template("processing_error.html")
        html_content = template.render(
            session_name=session_name,
            error_message=error_message,
            support_email="support@studybuddy.com"
        )
        
        await self._send_email(
            to_email=user_email,
            subject=f"❌ Processing Failed - {session_name}",
            html_content=html_content
        )
    
    async def _send_email(self, to_email: str, subject: str, html_content: str):
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.settings.from_email
            msg['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as server:
                server.starttls()
                server.login(self.settings.smtp_username, self.settings.smtp_password)
                server.send_message(msg)
                
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
    
    def _load_template(self, template_name: str) -> Template:
        template_path = os.path.join(self.settings.email_template_path, template_name)
        with open(template_path, 'r') as f:
            return Template(f.read())
```

### Email Templates

#### Processing Complete Template (`templates/emails/processing_complete.html`)
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        .container { max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; }
        .header { background: #3B82F6; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .button { background: #10B981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0; }
        .footer { background: #F3F4F6; padding: 15px; text-align: center; font-size: 12px; color: #6B7280; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Your Study Materials are Ready!</h1>
        </div>
        <div class="content">
            <h2>Hi {{ user_name }}!</h2>
            <p>Great news! We've finished processing your study materials for <strong>{{ session_name }}</strong>.</p>
            
            <p>Your AI-generated content includes:</p>
            <ul>
                <li>📝 25 Multiple Choice Questions with explanations</li>
                <li>🎯 Interactive Mock Tests</li>
                <li>🧠 India-specific Mnemonics</li>
                <li>📋 High-yield Cheat Sheets</li>
                <li>📚 Comprehensive Study Notes</li>
            </ul>
            
            <a href="{{ results_link }}" class="button">View Your Results</a>
            
            <p>Happy studying!</p>
            <p><strong>The Study Buddy Team</strong></p>
        </div>
        <div class="footer">
            <p>This email was sent because you opted to receive notifications when your study materials are ready.</p>
        </div>
    </div>
</body>
</html>
```

### Integration with Processing Pipeline
```python
class ProcessingService:
    def __init__(self, email_service: EmailService):
        self.email_service = email_service
    
    async def process_files_with_notification(self, files: List[UploadFile], user_id: str, user_email: str, session_name: str):
        try:
            # Start processing
            session_id = await self.process_files(files, user_id, session_name)
            
            # Send completion notification
            if self.email_service.enabled:
                await self.email_service.send_processing_complete_email(
                    user_email=user_email,
                    session_id=session_id,
                    session_name=session_name
                )
            
            return session_id
            
        except Exception as e:
            # Send error notification
            await self.email_service.send_processing_error_email(
                user_email=user_email,
                session_name=session_name,
                error_message=str(e)
            )
            raise
```

## File Storage System

### Local Storage (Default)
```python
# File stored in ./uploads/{session_id}/{filename}
FILE_STORAGE_TYPE=local
UPLOAD_DIR=./uploads
```

### AWS S3 Storage
```python
# Files stored in S3 bucket
FILE_STORAGE_TYPE=s3
AWS_S3_BUCKET=studybuddy-files
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

### Storage Service Implementation
```python
class FileStorageService:
    def __init__(self, storage_type: str):
        self.storage_type = storage_type
        if storage_type == "s3":
            self.s3_client = boto3.client('s3')
    
    async def save_file(self, file: UploadFile, session_id: str) -> str:
        if self.storage_type == "local":
            return await self._save_local(file, session_id)
        elif self.storage_type == "s3":
            return await self._save_s3(file, session_id)
    
    async def _save_local(self, file: UploadFile, session_id: str) -> str:
        # Save to local filesystem
        pass
    
    async def _save_s3(self, file: UploadFile, session_id: str) -> str:
        # Save to AWS S3
        pass
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

@app.post("/api/v1/upload/")
@limiter.limit("10/minute")
async def upload_files_endpoint(request: Request, ...):
    # File upload logic

@app.post("/api/v1/text-input/")
@limiter.limit("20/minute")
async def text_input_endpoint(request: Request, ...):
    # Text processing logic
```

### File Upload Validation
```python
class FileValidator:
    def __init__(self, settings: Settings):
        self.max_file_size = settings.max_file_size
        self.allowed_types = settings.allowed_file_types
        self.max_files = settings.max_files_per_upload
    
    def validate_file(self, file: UploadFile) -> bool:
        # Check file size
        if file.size > self.max_file_size:
            raise HTTPException(400, f"File size exceeds {self.max_file_size} bytes")
        
        # Check file type
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in self.allowed_types:
            raise HTTPException(400, f"File type {file_ext} not allowed")
        
        return True
    
    def validate_upload(self, files: List[UploadFile]) -> bool:
        # Check number of files
        if len(files) > self.max_files:
            raise HTTPException(400, f"Maximum {self.max_files} files allowed")
        
        # Validate each file
        for file in files:
            self.validate_file(file)
        
        return True
```

### Mock Test System

#### Test Creation
```python
class MockTestService:
    async def create_test(self, questions: List[Question], duration: int = 60) -> MockTest:
        return MockTest(
            test_name=f"Mock Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            questions=questions[:25],  # Limit to 25 questions
            duration_minutes=duration,
            total_marks=len(questions),
            created_at=datetime.utcnow()
        )
    
    async def start_test(self, test_id: str, user_id: str) -> TestSession:
        return TestSession(
            test_id=test_id,
            user_id=user_id,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(minutes=60),
            status="in_progress"
        )
```

#### Test Taking Interface
```python
class TestInterface:
    def __init__(self, test_session: TestSession):
        self.session = test_session
        self.current_question = 0
        self.answers = {}
        self.marked_for_review = set()
    
    def answer_question(self, question_id: str, answer: str):
        self.answers[question_id] = answer
    
    def mark_for_review(self, question_id: str):
        self.marked_for_review.add(question_id)
    
    def navigate_to_question(self, question_index: int):
        self.current_question = question_index
    
    def submit_test(self) -> TestResult:
        return self.calculate_score()
```

#### Auto-Scoring System
```python
class TestScorer:
    def calculate_score(self, test: MockTest, answers: Dict[str, str]) -> TestResult:
        correct_answers = 0
        total_questions = len(test.questions)
        question_results = []
        
        for question in test.questions:
            user_answer = answers.get(question.id)
            is_correct = user_answer == question.correct_answer
            
            if is_correct:
                correct_answers += 1
            
            question_results.append({
                "question_id": question.id,
                "user_answer": user_answer,
                "correct_answer": question.correct_answer,
                "is_correct": is_correct,
                "explanation": question.explanation
            })
        
        score_percentage = (correct_answers / total_questions) * 100
        
        return TestResult(
            score=correct_answers,
            total_questions=total_questions,
            percentage=score_percentage,
            question_results=question_results,
            time_taken=self.calculate_time_taken(),
            performance_analytics=self.generate_analytics(question_results)
        )
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
