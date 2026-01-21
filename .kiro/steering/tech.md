# Study Buddy App - Technical Specifications

## System Architecture

### Overview
Microservices architecture with separate frontend and backend services, designed for future integration into the existing MedGloss platform.

### Tech Stack

#### Frontend
- **Framework**: Next.js 14+ with React 18+
- **Styling**: TailwindCSS
- **State Management**: React Context API / Redux
- **HTTP Client**: Axios
- **File Upload**: React Dropzone
- **UI Components**: Shadcn/ui or custom components

#### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: MongoDB (local instance)
- **ODM**: PyMongo / Motor (async)
- **File Processing**: PyPDF2, Pillow, OpenCV
- **AI/ML**: Google GenAI API
- **Authentication**: JWT (existing MedGloss logic)
- **Task Queue**: Celery + Redis (for async processing)

#### Infrastructure
- **Database**: MongoDB 6.0+
- **Cache**: Redis 7.0+
- **File Storage**: Local filesystem (./uploads)
- **OCR**: Existing scripts from medgloss-data-extractorfiles

## Repository Structure

```
/home/unknown/Documents/hackathon application/dynamous-kiro-hackathon/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── study-buddy/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── dashboard/
│   │   │   │   └── results/
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── StudyBuddyCard.tsx
│   │   │   ├── UploadSection.tsx
│   │   │   ├── ResultsViewer.tsx
│   │   │   └── SessionManager.tsx
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── utils.ts
│   │   └── types/
│   │       └── index.ts
│   ├── public/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── .env.local
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   │   ├── session.py
│   │   │   ├── question.py
│   │   │   ├── mnemonic.py
│   │   │   └── cheatsheet.py
│   │   ├── services/
│   │   │   ├── file_processor.py
│   │   │   ├── ai_processor.py
│   │   │   ├── ocr_service.py
│   │   │   └── export_service.py
│   │   ├── api/
│   │   │   ├── upload.py
│   │   │   ├── process.py
│   │   │   └── results.py
│   │   └── utils/
│   │       ├── auth.py
│   │       └── helpers.py
│   ├── requirements.txt
│   └── .env
│
├── docs/
│   ├── API.md
│   ├── SETUP.md
│   └── ARCHITECTURE.md
│
├── README.md
├── DEVLOG.md
└── .gitignore
```

## Database Schema

### Collections

#### 1. study_sessions
```javascript
{
  _id: ObjectId,
  session_id: String (UUID),
  user_id: ObjectId,
  session_name: String,
  created_at: ISODate,
  files_uploaded: [{
    filename: String,
    file_type: String,
    file_size: Number,
    processing_mode: String
  }],
  processing_status: String, // "pending" | "processing" | "completed" | "failed"
  progress: Number, // 0-100
  outputs_generated: {
    questions: Boolean,
    mock_tests: Boolean,
    mnemonics: Boolean,
    cheat_sheets: Boolean,
    notes: Boolean
  }
}
```

#### 2. questions
```javascript
{
  _id: ObjectId,
  question_id: String (UUID),
  session_id: String,
  created_by: ObjectId,
  question_text: String,
  options: [{
    option_id: String,
    text: String,
    is_correct: Boolean
  }],
  explanation: String,
  difficulty: String, // "Easy" | "Medium" | "Hard"
  medical_subject: String,
  tags: [String],
  created_at: ISODate
}
```

#### 3. mock_tests
```javascript
{
  _id: ObjectId,
  mock_test_id: String (UUID),
  session_id: String,
  created_by: ObjectId,
  test_name: String,
  questions: [ObjectId],
  duration_minutes: Number,
  total_marks: Number,
  created_at: ISODate
}
```

#### 4. mnemonics
```javascript
{
  _id: ObjectId,
  session_id: String,
  created_by: ObjectId,
  topic: String,
  mnemonic_text: String,
  mnemonic_type: String, // "text" | "image"
  image_url: String,
  is_india_specific: Boolean,
  key_terms: [String],
  created_at: ISODate
}
```

#### 5. cheat_sheets
```javascript
{
  _id: ObjectId,
  session_id: String,
  created_by: ObjectId,
  title: String,
  content: String, // HTML/Markdown
  key_topics: [String],
  high_yield_points: [String],
  download_formats: {
    pdf_url: String,
    image_url: String
  },
  created_at: ISODate
}
```

#### 6. notes
```javascript
{
  _id: ObjectId,
  session_id: String,
  created_by: ObjectId,
  title: String,
  content: {
    important_questions: [ObjectId],
    cheat_sheet_summaries: [String],
    mnemonics: [ObjectId],
    high_yield_topics: [String]
  },
  download_url: String,
  created_at: ISODate
}
```

### Indexes
```javascript
// study_sessions
db.study_sessions.createIndex({ user_id: 1, created_at: -1 })
db.study_sessions.createIndex({ session_id: 1 }, { unique: true })

// questions
db.questions.createIndex({ session_id: 1 })
db.questions.createIndex({ created_by: 1 })

// mock_tests
db.mock_tests.createIndex({ session_id: 1 })

// mnemonics
db.mnemonics.createIndex({ session_id: 1 })

// cheat_sheets
db.cheat_sheets.createIndex({ session_id: 1 })

// notes
db.notes.createIndex({ session_id: 1 })
```

## API Specifications

### Base Configuration
```
Base URL: http://localhost:8000
API Prefix: /api/v1
Authentication: Bearer JWT token
```

### Endpoints

#### 1. Upload Files
```
POST /api/v1/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

Request Body:
- files: File[] (multiple files)
- video_links: string[] (optional)
- processing_mode: "default" | "ocr" | "ai-based"

Response: 200 OK
{
  "session_id": "uuid",
  "upload_status": "success",
  "files_processed": 3,
  "processing_started": true
}
```

#### 2. Get Processing Status
```
GET /api/v1/process/{session_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "status": "processing",
  "progress": 45,
  "current_step": "Generating questions",
  "estimated_completion": "2026-01-19T20:30:00Z"
}
```

#### 3. Get Questions
```
GET /api/v1/questions/{session_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "session_id": "uuid",
  "questions": [
    {
      "question_id": "uuid",
      "question_text": "What is...",
      "options": [...],
      "explanation": "...",
      "difficulty": "Medium",
      "medical_subject": "Anatomy"
    }
  ],
  "total": 25
}
```

#### 4. Get Mock Tests
```
GET /api/v1/mock-tests/{session_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "session_id": "uuid",
  "mock_tests": [
    {
      "mock_test_id": "uuid",
      "test_name": "Curated Mock Test",
      "questions": [...],
      "duration_minutes": 60,
      "total_marks": 100
    }
  ]
}
```

#### 5. Get Mnemonics
```
GET /api/v1/mnemonics/{session_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "session_id": "uuid",
  "mnemonics": [
    {
      "topic": "Cranial Nerves",
      "mnemonic_text": "...",
      "is_india_specific": true,
      "key_terms": [...]
    }
  ]
}
```

#### 6. Get Cheat Sheets
```
GET /api/v1/cheat-sheets/{session_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "session_id": "uuid",
  "cheat_sheets": [
    {
      "title": "Anatomy Key Points",
      "content": "...",
      "key_topics": [...],
      "download_formats": {
        "pdf_url": "/downloads/...",
        "image_url": "/downloads/..."
      }
    }
  ]
}
```

#### 7. Get Notes
```
GET /api/v1/notes/{session_id}
Authorization: Bearer <token>

Response: 200 OK
{
  "session_id": "uuid",
  "notes": {
    "title": "Session Notes",
    "content": {...},
    "download_url": "/downloads/..."
  }
}
```

#### 8. Download Resource
```
GET /api/v1/download/{resource_type}/{resource_id}
Authorization: Bearer <token>

Response: 200 OK
Content-Type: application/pdf | image/png
Content-Disposition: attachment; filename="..."
```

## Processing Pipeline

### 1. File Upload Flow
```
User uploads files
    ↓
Validate file types and sizes
    ↓
Store files in ./uploads/{session_id}/
    ↓
Create session record in database
    ↓
Queue processing task
    ↓
Return session_id to frontend
```

### 2. Processing Flow
```
Retrieve files from storage
    ↓
Extract text based on processing mode
    ├── Default: Direct text extraction
    ├── OCR: Convert to images → OCR
    └── AI-based: Advanced extraction
    ↓
Send text to AI processor
    ↓
Generate outputs in parallel:
    ├── Questions
    ├── Mock Tests
    ├── Mnemonics
    ├── Cheat Sheets
    └── Notes
    ↓
Store outputs in database
    ↓
Update session status to "completed"
```

### 3. AI Processing Service

#### Question Generation
```python
def generate_questions(text: str, count: int = 25) -> List[Question]:
    prompt = f"""
    Generate {count} medical MCQs from the following text.
    Format: Question, 4 options, correct answer, explanation.
    Classify by difficulty (Easy/Medium/Hard) and subject.
    
    Text: {text}
    """
    response = genai.generate(prompt)
    return parse_questions(response)
```

#### Mnemonic Generation
```python
def generate_mnemonics(text: str) -> List[Mnemonic]:
    prompt = f"""
    Create India-specific mnemonics for key concepts in this text.
    Focus on memorable, culturally relevant associations.
    
    Text: {text}
    """
    response = genai.generate(prompt)
    return parse_mnemonics(response)
```

#### Cheat Sheet Generation
```python
def generate_cheat_sheet(text: str) -> CheatSheet:
    prompt = f"""
    Extract key topics and high-yield points from this medical text.
    Format as concise, exam-focused summaries.
    
    Text: {text}
    """
    response = genai.generate(prompt)
    return parse_cheat_sheet(response)
```

## Authentication Integration

### JWT Validation
```python
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(
            token.credentials,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401)
        return user_id
    except JWTError:
        raise HTTPException(status_code=401)
```

## Environment Configuration

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=StudyBuddy
NEXTAUTH_SECRET=your-nextauth-secret-here
```

### Backend (.env)
```env
# Database
MONGODB_URL=mongodb://localhost:27017/medgloss
DATABASE_NAME=medgloss

# AI Service
GOOGLE_AI_API_KEY=your-api-key-here
GENAI_PROJECT_ID=<project_id>

# Authentication
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRY=86400

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=52428800  # 50MB

# OCR Scripts
OCR_SCRIPTS_PATH=/home/unknown/Documents/medgloss-data-extractorfiles

# Redis
REDIS_URL=redis://localhost:6379

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## Performance Optimization

### Caching Strategy
- Cache AI responses for similar content (Redis)
- Cache user sessions (Redis)
- Database query result caching

### Async Processing
- Use Celery for background tasks
- Process large files asynchronously
- Parallel output generation

### Database Optimization
- Proper indexing on frequently queried fields
- Connection pooling
- Batch inserts for bulk data

## Security Measures

### Input Validation
- File type whitelist: PDF, JPG, PNG, PPTX
- File size limit: 50MB
- Sanitize filenames
- Validate video URLs

### Data Protection
- User-specific data isolation
- JWT token validation on all endpoints
- Rate limiting (100 requests/minute per user)
- CORS configuration

### File Security
- Store files outside web root
- Generate unique filenames
- Automatic cleanup of old files (30 days)

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

### Error Codes
- `AUTH_001`: Invalid or expired token
- `UPLOAD_001`: Invalid file type
- `UPLOAD_002`: File size exceeded
- `PROCESS_001`: Processing failed
- `AI_001`: AI service error
- `DB_001`: Database error

## Testing Strategy

### Unit Tests
- Test each service independently
- Mock external dependencies
- Coverage target: 80%

### Integration Tests
- Test API endpoints
- Test database operations
- Test file processing pipeline

### Performance Tests
- Load testing with multiple concurrent users
- File processing time benchmarks
- Database query performance

## Deployment

### Development
```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Production Considerations
- Use Gunicorn with Uvicorn workers
- Nginx reverse proxy
- SSL/TLS certificates
- Environment-specific configs
- Logging and monitoring
