# Backend API Endpoints

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Most endpoints require JWT authentication (except health checks and login).
Include in header: `Authorization: Bearer <token>`

## Endpoints

### Health & Status
- `GET /` - API root information
- `GET /health` - Health check

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/send-otp` - Send OTP for verification
- `POST /api/v1/auth/verify-otp` - Verify OTP code
- `POST /api/v1/auth/login` - Login with credentials
- `POST /login` - Login (backward compatibility endpoint)

### File Upload & Processing
- `POST /api/v1/upload/` - Upload files and start processing
- `GET /api/v1/upload/status/{session_id}` - Get processing status
- `GET /api/v1/upload/check-upload-allowed/{user_id}` - Check if user can upload
- `GET /api/v1/upload/file-limits` - Get file size limits

### Generated Content
- `GET /api/v1/questions/{session_id}` - Get session questions
- `GET /api/v1/mock-tests/{session_id}` - Get session mock tests
- `GET /api/v1/mnemonics/{session_id}` - Get session mnemonics
- `GET /api/v1/cheat-sheets/{session_id}` - Get session cheat sheets
- `GET /api/v1/notes/{session_id}` - Get session notes

### S3 Testing (Development)
- `POST /api/v1/s3-test/upload` - Test S3 upload
- `GET /api/v1/s3-test/list` - List S3 objects
- `GET /api/v1/s3-test/download/{key}` - Download from S3
- `DELETE /api/v1/s3-test/delete/{key}` - Delete from S3

## Request/Response Examples

### Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "mobile_number": "1234567890",
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'
```

Response:
```json
{
  "message": "User registered successfully",
  "user_id": "user-uuid-here"
}
```

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "mobile_number": "1234567890",
    "password": "SecurePass123!"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "mobile_number": "1234567890",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

### Upload Files
```bash
curl -X POST "http://localhost:8000/api/v1/upload/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document.pdf" \
  -F "processing_mode=default"
```

Response:
```json
{
  "session_id": "uuid-here",
  "message": "Files uploaded successfully",
  "files_uploaded": 1,
  "storage_location": "s3"
}
```

### Check Upload Status
```bash
curl "http://localhost:8000/api/v1/upload/status/session-id-here" \
  -H "Authorization: Bearer <token>"
```

Response:
```json
{
  "session_id": "session-uuid",
  "status": "completed",
  "progress": 100,
  "files_count": 1,
  "created_at": "2026-01-20T11:37:18Z"
}
```

### Get Questions
```bash
curl "http://localhost:8000/api/v1/questions/session-id-here" \
  -H "Authorization: Bearer <token>"
```

Response:
```json
{
  "questions": [
    {
      "question_id": "uuid",
      "session_id": "session-uuid",
      "user_id": "user123",
      "question_text": "What is the function of the heart?",
      "options": ["Pump blood", "Filter toxins", "Produce hormones", "Store energy"],
      "correct_answer": 0,
      "explanation": "The heart's primary function is to pump blood...",
      "difficulty": "easy",
      "topic": "Cardiology",
      "created_at": "2026-01-19T19:13:42.516Z"
    }
  ],
  "total_count": 1
}
```

## Features

### Rate Limiting
- Enabled by default (configurable via `ENABLE_RATE_LIMITING` env var)
- Protects against abuse and ensures fair resource usage

### CORS Configuration
- Allows requests from localhost:3000, localhost:3001 (frontend dev servers)
- Supports credentials for authenticated requests
- Allows all HTTP methods and headers

### Request Logging
- All requests are logged with method, URL, status code, and processing time
- Logs stored in `logs/backend.log` and `backend/backend.log`

### Storage Options
- **Local Storage**: Files stored in `./uploads` directory
- **S3 Storage**: Files stored in AWS S3 bucket (configurable via `STORAGE` env var)
- Automatic fallback to local storage if S3 fails

### Upload Restrictions
- File size limits: PDF (48MB), Images (10MB), Slides (100MB)
- Maximum 25 images per upload
- Upload cooldown period (configurable, default 5 minutes)
- Can be disabled via `ENABLE_UPLOAD_RESTRICTIONS` env var
