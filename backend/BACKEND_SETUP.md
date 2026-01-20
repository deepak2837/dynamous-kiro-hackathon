# Backend Setup & Configuration Guide

## Overview

The StudyBuddy backend is built with FastAPI and provides a RESTful API for file uploads, AI-powered content generation, and user authentication.

## Architecture

### Core Components

1. **FastAPI Application** (`app/main.py`)
   - Async lifespan management
   - CORS middleware for frontend communication
   - Request logging middleware
   - Rate limiting with slowapi

2. **Authentication System** (`app/api/auth_simple.py`)
   - User registration with mobile/email
   - OTP verification (SMS/Email)
   - JWT token-based authentication
   - Password hashing with bcrypt

3. **File Upload System** (`app/api/upload_basic.py`)
   - Multi-file upload support
   - Dual storage: Local filesystem and AWS S3
   - Upload restrictions and cooldown
   - File validation by type and size

4. **Database** (`app/database.py`)
   - MongoDB with Motor (async driver)
   - Collections: users, sessions, questions, mock_tests, etc.

## Installation

### Prerequisites

- Python 3.10+
- MongoDB 6.0+
- Redis 7.0+ (optional, for Celery)
- AWS account (optional, for S3 storage)

### Setup Steps

1. **Create Virtual Environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Start MongoDB**
```bash
mongod --dbpath /path/to/data
```

5. **Run Backend Server**
```bash
uvicorn app.main:app --reload --port 8000
```

## Environment Configuration

### Required Variables

```env
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=studybuddy

# Authentication
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

### Optional Variables

```env
# AI Service (Gemini)
GEMINI_API_KEY=your_api_key
GOOGLE_CLOUD_PROJECT_ID=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./google_service_account.json

# OTP Services
DEFAULT_OTP_METHOD=email  # "sms" or "email"
FAST2SMS_API_KEY=your_key  # For SMS
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# AWS S3 Storage
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-south-1
STUDY_BUDDY_BUCKET_NAME=your-bucket-name
STORAGE=LOCAL  # "S3" or "LOCAL"

# Upload Restrictions
MAX_PDF_SIZE=50485760  # 48MB
MAX_IMAGE_SIZE=10485760  # 10MB
MAX_SLIDE_SIZE=104857600  # 100MB
MAX_IMAGES_PER_UPLOAD=25
UPLOAD_COOLDOWN_MINUTES=5
ENABLE_UPLOAD_RESTRICTIONS=true

# Rate Limiting
ENABLE_RATE_LIMITING=true
```

## API Endpoints

### Authentication

**Register User**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "mobile_number": "1234567890",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Login**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "mobile_number": "1234567890",
  "password": "SecurePass123!"
}
```

### File Upload

**Upload Files**
```http
POST /api/v1/upload/
Authorization: Bearer <token>
Content-Type: multipart/form-data

files: [file1.pdf, file2.png]
processing_mode: "default"
```

**Check Upload Status**
```http
GET /api/v1/upload/status/{session_id}
Authorization: Bearer <token>
```

### Content Retrieval

```http
GET /api/v1/questions/{session_id}
GET /api/v1/mock-tests/{session_id}
GET /api/v1/mnemonics/{session_id}
GET /api/v1/cheat-sheets/{session_id}
GET /api/v1/notes/{session_id}
```

## Storage Configuration

### Local Storage

Files are stored in `./uploads` directory by default.

```env
STORAGE=LOCAL
UPLOAD_DIR=./uploads
```

### AWS S3 Storage

Configure S3 credentials and bucket:

```env
STORAGE=S3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=ap-south-1
STUDY_BUDDY_BUCKET_NAME=your-bucket
```

The system automatically falls back to local storage if S3 upload fails.

## Security Features

### Authentication
- JWT tokens with configurable expiration
- Password hashing with bcrypt
- OTP verification for registration

### Rate Limiting
- Configurable rate limits per endpoint
- Prevents abuse and ensures fair usage
- Can be disabled for development

### File Validation
- File type whitelist (PDF, images, slides)
- Size limits per file type
- Maximum files per upload
- Upload cooldown period

### CORS
- Configured for localhost development
- Allows credentials for authenticated requests
- Customizable origins

## Logging

### Log Files
- `logs/backend.log` - Application logs
- `backend/backend.log` - Backup log location

### Log Format
```
2026-01-20 11:36:23,108 - app - INFO - Request: GET http://localhost:8000/health
2026-01-20 11:36:23,108 - app - INFO - Response: 200 - 0.001s
```

### Log Levels
- DEBUG: Detailed debugging information
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages

## Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  mobile_number: String,
  email: String,
  password_hash: String,
  full_name: String,
  is_verified: Boolean,
  created_at: ISODate,
  last_login: ISODate
}
```

### Sessions Collection
```javascript
{
  _id: ObjectId,
  session_id: String (UUID),
  user_id: ObjectId,
  files: [{
    filename: String,
    storage_location: String,
    file_size: Number
  }],
  processing_mode: String,
  status: String,
  created_at: ISODate
}
```

## Troubleshooting

### MongoDB Connection Issues
```bash
# Check if MongoDB is running
mongosh

# Start MongoDB
mongod --dbpath /path/to/data
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### S3 Upload Failures
- Verify AWS credentials are correct
- Check bucket permissions
- Ensure bucket exists in specified region
- System will fallback to local storage

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black app/
```

### Type Checking
```bash
mypy app/
```

## Production Deployment

### Using Gunicorn
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker
```bash
docker build -t studybuddy-backend .
docker run -p 8000:8000 studybuddy-backend
```

### Environment Variables
- Use production-grade secrets
- Enable HTTPS
- Configure proper CORS origins
- Set up monitoring and logging

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
