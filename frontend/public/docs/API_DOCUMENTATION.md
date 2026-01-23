# Study Buddy API Documentation

## Base Configuration
- **Base URL**: `http://localhost:8000`
- **API Prefix**: `/api/v1`
- **Authentication**: Bearer JWT token
- **Content-Type**: `application/json`

## Authentication Endpoints

### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "mobile": "9876543210",
  "password": "password123",
  "otp": "123456",
  "name": "John Doe"
}

Response: 200 OK
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "user": {
    "id": "user_id",
    "mobile": "9876543210",
    "name": "John Doe"
  }
}
```

### Login User
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "mobile": "9876543210",
  "password": "password123"
}

Response: 200 OK
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

## Core Features API

### 1. File Upload & Processing

#### Upload Files
```http
POST /api/v1/upload/
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- files: File[] (multiple files)
- session_name: string (optional)
- processing_mode: "default" | "ocr" | "ai-based"

Response: 200 OK
{
  "session_id": "uuid",
  "upload_status": "success",
  "files_processed": 3,
  "processing_started": true,
  "message": "Files uploaded successfully"
}
```

#### Get Processing Status
```http
GET /api/v1/upload/status/{session_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "status": "processing",
  "progress": 45,
  "current_step": "Generating questions",
  "estimated_completion": "2026-01-23T20:30:00Z"
}
```

### 2. Flashcard Generator

#### Get Session Flashcards
```http
GET /api/v1/flashcards/{session_id}?skip=0&limit=50
Authorization: Bearer <token>

Response: 200 OK
{
  "flashcards": [
    {
      "id": "flashcard_id",
      "question": "What is the function of mitochondria?",
      "answer": "Powerhouse of the cell - produces ATP",
      "difficulty": "medium",
      "subject": "biology",
      "tags": ["cell biology", "organelles"],
      "created_at": "2026-01-23T15:30:00Z"
    }
  ],
  "total": 25,
  "skip": 0,
  "limit": 50
}
```

#### Review Flashcard
```http
POST /api/v1/flashcards/{flashcard_id}/review
Authorization: Bearer <token>
Content-Type: application/json

{
  "difficulty": "easy" | "medium" | "hard",
  "correct": true
}

Response: 200 OK
{
  "message": "Review recorded successfully",
  "next_review_date": "2026-01-25T15:30:00Z"
}
```

### 3. Study Planner

#### Generate Study Plan
```http
POST /api/v1/study-planner/generate-plan
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "session_uuid",
  "config": {
    "exam_date": "2026-02-15",
    "daily_study_hours": 6.0,
    "weak_areas": ["anatomy", "physiology"]
  },
  "plan_name": "NEET Preparation Plan"
}

Response: 200 OK
{
  "plan": {
    "plan_id": "plan_uuid",
    "session_id": "session_uuid",
    "plan_name": "NEET Preparation Plan",
    "config": {
      "exam_date": "2026-02-15",
      "daily_study_hours": 6.0,
      "weak_areas": ["anatomy", "physiology"]
    },
    "daily_schedules": [
      {
        "date": "2026-01-24",
        "total_study_time": 360,
        "tasks": [
          {
            "task_id": "task_uuid",
            "title": "Review Anatomy - Skeletal System",
            "description": "Study bones and joints",
            "task_type": "study_notes",
            "subject": "anatomy",
            "estimated_duration": 120,
            "priority": 3,
            "content_ids": ["content_id_1"]
          }
        ],
        "total_tasks": 3
      }
    ],
    "total_study_days": 23,
    "total_study_hours": 138,
    "subjects_covered": ["anatomy", "physiology"],
    "created_at": "2026-01-23T15:30:00Z"
  },
  "message": "Study plan generated successfully"
}
```

#### Get User Study Plans
```http
GET /api/v1/study-planner/plans
Authorization: Bearer <token>

Response: 200 OK
{
  "plans": [
    {
      "plan_id": "plan_uuid",
      "plan_name": "NEET Preparation Plan",
      "created_at": "2026-01-23T15:30:00Z",
      "total_study_days": 23,
      "progress": 15.5
    }
  ],
  "total": 1
}
```

#### Update Task Status
```http
PUT /api/v1/study-planner/tasks/{task_id}/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "completed" | "in_progress" | "pending"
}

Response: 200 OK
{
  "message": "Task status updated successfully",
  "task": {
    "task_id": "task_uuid",
    "status": "completed",
    "completed_at": "2026-01-23T16:30:00Z"
  }
}
```

### 4. Export & Download

#### Download Content
```http
GET /api/v1/download/{content_type}/{content_id}?format=pdf
Authorization: Bearer <token>

Parameters:
- content_type: "questions" | "flashcards" | "notes" | "cheat_sheets" | "mnemonics"
- content_id: string
- format: "pdf" | "json" (optional, default: pdf)

Response: 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="questions_export.pdf"

[Binary PDF content]
```

#### Bulk Export Session
```http
POST /api/v1/download/session/{session_id}/export
Authorization: Bearer <token>
Content-Type: application/json

{
  "content_types": ["questions", "flashcards", "notes"],
  "format": "pdf"
}

Response: 200 OK
{
  "download_url": "/api/v1/download/bulk/export_uuid",
  "expires_at": "2026-01-23T18:30:00Z"
}
```

## Content Retrieval Endpoints

### Questions
```http
GET /api/v1/questions/{session_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "questions": [
    {
      "question_id": "uuid",
      "question_text": "What is the function of the heart?",
      "options": [
        {"option_id": "a", "text": "Pump blood", "is_correct": true},
        {"option_id": "b", "text": "Filter toxins", "is_correct": false}
      ],
      "explanation": "The heart pumps blood throughout the body",
      "difficulty": "medium",
      "medical_subject": "anatomy"
    }
  ],
  "total": 25
}
```

### Mock Tests
```http
GET /api/v1/mock-tests/{session_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "mock_tests": [
    {
      "mock_test_id": "uuid",
      "test_name": "Anatomy Mock Test",
      "questions": ["question_id_1", "question_id_2"],
      "duration_minutes": 60,
      "total_marks": 100
    }
  ]
}
```

### Notes, Mnemonics, Cheat Sheets
```http
GET /api/v1/notes/{session_id}
GET /api/v1/mnemonics/{session_id}  
GET /api/v1/cheat-sheets/{session_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "content": [
    {
      "id": "uuid",
      "title": "Anatomy Notes",
      "content": "Detailed notes content...",
      "created_at": "2026-01-23T15:30:00Z"
    }
  ]
}
```

## Session Management

### Get User Sessions
```http
GET /api/v1/sessions?skip=0&limit=10
Authorization: Bearer <token>

Response: 200 OK
{
  "sessions": [
    {
      "session_id": "uuid",
      "session_name": "Anatomy Study Session",
      "created_at": "2026-01-23T15:30:00Z",
      "status": "completed",
      "files_count": 3,
      "content_generated": {
        "questions": 25,
        "flashcards": 20,
        "notes": 1,
        "cheat_sheets": 1,
        "mnemonics": 5
      }
    }
  ],
  "total": 1
}
```

### Delete Session
```http
DELETE /api/v1/sessions/{session_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "message": "Session deleted successfully"
}
```

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-01-23T15:30:00Z"
}
```

### Common Error Codes
- `AUTH_001`: Invalid or expired token (401)
- `UPLOAD_001`: Invalid file type (400)
- `UPLOAD_002`: File size exceeded (413)
- `PROCESS_001`: Processing failed (500)
- `AI_001`: AI service error (503)
- `DB_001`: Database error (500)
- `RATE_001`: Rate limit exceeded (429)

## Rate Limits
- **Authentication**: 10 requests/minute
- **Upload**: 5 requests/minute
- **API calls**: 100 requests/minute
- **Heavy operations**: 2 requests/minute

## File Constraints
- **Max file size**: 50MB per file
- **Max files per upload**: 10 files
- **Supported formats**: PDF, JPG, JPEG, PNG, PPTX
- **Total session size**: 500MB

## WebSocket Events (Real-time Updates)
```javascript
// Connect to processing updates
const ws = new WebSocket('ws://localhost:8000/ws/processing/{session_id}');

// Events received:
{
  "event": "progress_update",
  "data": {
    "progress": 45,
    "current_step": "Generating flashcards",
    "estimated_completion": "2026-01-23T16:30:00Z"
  }
}

{
  "event": "processing_complete",
  "data": {
    "session_id": "uuid",
    "content_generated": {
      "questions": 25,
      "flashcards": 20
    }
  }
}
```
