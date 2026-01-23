# Study Buddy API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication

All endpoints except `/api/v1/auth/*` require JWT Bearer token authentication.

### Headers
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

---

## Endpoints

### Authentication

#### Register User
```http
POST /api/v1/auth/register
```

**Request Body:**
```json
{
  "mobile_number": "+919876543210",
  "password": "SecurePass123",
  "full_name": "John Doe",
  "email": "john@example.com"
}
```

**Response:** `201 Created`
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "mobile_number": "+919876543210",
  "full_name": "John Doe",
  "email": "john@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Login
```http
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "mobile_number": "+919876543210",
  "password": "SecurePass123"
}
```

**Response:** `200 OK`
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "mobile_number": "+919876543210",
  "full_name": "John Doe",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### File Upload & Processing

#### Upload Files
```http
POST /api/v1/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**Form Data:**
- `files`: File[] (PDF, JPG, PNG, PPTX - max 50MB each)
- `session_name`: string (optional)

**Response:** `200 OK`
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "Files uploaded successfully. Processing started.",
  "files_count": 2,
  "session_name": "Anatomy Study Session"
}
```

#### Generate from Topic
```http
POST /api/v1/text-input
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "topic": "Cardiovascular System",
  "session_name": "Cardiology Basics"
}
```

**Response:** `200 OK`
```json
{
  "session_id": "b2c3d4e5-f6g7-8901-bcde-fg2345678901",
  "message": "Processing started for topic",
  "topic": "Cardiovascular System"
}
```

#### Get Processing Status
```http
GET /api/v1/process/{session_id}
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "processing",
  "progress": 65,
  "current_step": "generating_mnemonics",
  "outputs_generated": {
    "questions": true,
    "mock_tests": true,
    "mnemonics": false,
    "cheat_sheets": false,
    "notes": false
  }
}
```

**Status Values:**
- `pending`: Queued for processing
- `processing`: Currently being processed
- `completed`: All outputs generated
- `failed`: Processing failed

---

### Results

#### Get Questions
```http
GET /api/v1/questions/{session_id}
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "questions": [
    {
      "question_id": "q1",
      "question": "What are the four chambers of the heart?",
      "options": {
        "A": "Two atria and two ventricles",
        "B": "Four ventricles",
        "C": "Four atria",
        "D": "One atrium and three ventricles"
      },
      "correct_answer": "A",
      "explanation": "The heart has four chambers: right atrium, left atrium, right ventricle, and left ventricle.",
      "difficulty": "easy",
      "topic": "Cardiovascular Anatomy"
    }
  ],
  "total": 25
}
```

#### Get Mock Tests
```http
GET /api/v1/mock-tests/{session_id}
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "mock_tests": [
    {
      "test_id": "mt1",
      "test_name": "Mock Test - Anatomy Study Session",
      "questions": ["q1", "q2", "q3", "q4", "q5"],
      "duration_minutes": 30,
      "total_questions": 25
    }
  ]
}
```

#### Get Mnemonics
```http
GET /api/v1/mnemonics/{session_id}
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "mnemonics": [
    {
      "mnemonic_id": "m1",
      "topic": "Heart Valves",
      "mnemonic_text": "Try Pulling My Arm - Tricuspid, Pulmonary, Mitral, Aortic",
      "explanation": "Helps remember the four heart valves in order",
      "key_terms": ["Tricuspid", "Pulmonary", "Mitral", "Aortic"],
      "is_india_specific": false
    }
  ],
  "total": 8
}
```

#### Get Cheat Sheets
```http
GET /api/v1/cheat-sheets/{session_id}
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "cheat_sheets": [
    {
      "cheat_sheet_id": "cs1",
      "title": "Cardiovascular System - Key Points",
      "key_points": [
        "Heart has 4 chambers",
        "Blood flows in one direction",
        "Systemic and pulmonary circulation"
      ],
      "high_yield_facts": [
        "Normal heart rate: 60-100 bpm",
        "Cardiac output = HR × SV"
      ],
      "quick_references": {
        "Systole": "Contraction phase",
        "Diastole": "Relaxation phase"
      }
    }
  ],
  "total": 3
}
```

#### Get Notes
```http
GET /api/v1/notes/{session_id}
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "notes": {
    "note_id": "n1",
    "title": "Study Notes - Anatomy Study Session",
    "content": "Comprehensive notes covering all key topics...",
    "summary_points": [
      "Cardiovascular system overview",
      "Heart anatomy and physiology",
      "Blood circulation pathways"
    ]
  }
}
```

---

### History

#### Get User Sessions
```http
GET /api/v1/history/sessions
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit`: number (default: 10, max: 50)
- `skip`: number (default: 0)

**Response:** `200 OK`
```json
{
  "sessions": [
    {
      "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "session_name": "Anatomy Study Session",
      "created_at": "2026-01-22T10:30:00Z",
      "processing_status": "completed",
      "files_uploaded": 2,
      "content_counts": {
        "questions": 25,
        "mock_tests": 1,
        "mnemonics": 8,
        "cheat_sheets": 3,
        "notes": 1
      }
    }
  ],
  "total": 15,
  "limit": 10,
  "skip": 0
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

### 404 Not Found
```json
{
  "detail": "Session not found"
}
```

### 413 Payload Too Large
```json
{
  "detail": "File size exceeds 50MB limit"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error occurred"
}
```

---

## Rate Limiting

- **Limit**: 100 requests per minute per user
- **Headers**:
  - `X-RateLimit-Limit`: 100
  - `X-RateLimit-Remaining`: 95
  - `X-RateLimit-Reset`: 1642857600

---

## File Upload Constraints

- **Supported formats**: PDF, JPG, PNG, PPTX
- **Max file size**: 50MB per file
- **Max files per upload**: 10 files
- **Total upload size**: 200MB per request

---

## Processing Times

| Content Type | Avg. Time | Max Time |
|--------------|-----------|----------|
| Questions | 30-60s | 2 min |
| Mock Tests | 10-20s | 1 min |
| Mnemonics | 40-80s | 3 min |
| Cheat Sheets | 30-60s | 2 min |
| Notes | 20-40s | 1 min |

**Total processing time**: 2-5 minutes for complete session

---

## WebSocket Support (Future)

Real-time processing updates will be available via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/process/{session_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress, '%');
  console.log('Step:', data.current_step);
};
```

---

## SDK Examples

### Python
```python
import requests

# Login
response = requests.post(
    'http://localhost:8000/api/v1/auth/login',
    json={
        'mobile_number': '+919876543210',
        'password': 'SecurePass123'
    }
)
token = response.json()['token']

# Upload files
files = {'files': open('anatomy.pdf', 'rb')}
headers = {'Authorization': f'Bearer {token}'}
response = requests.post(
    'http://localhost:8000/api/v1/upload',
    files=files,
    headers=headers
)
session_id = response.json()['session_id']

# Get questions
response = requests.get(
    f'http://localhost:8000/api/v1/questions/{session_id}',
    headers=headers
)
questions = response.json()['questions']
```

### JavaScript/TypeScript
```typescript
// Login
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    mobile_number: '+919876543210',
    password: 'SecurePass123'
  })
});
const { token } = await loginResponse.json();

// Upload files
const formData = new FormData();
formData.append('files', fileInput.files[0]);

const uploadResponse = await fetch('http://localhost:8000/api/v1/upload', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});
const { session_id } = await uploadResponse.json();

// Get questions
const questionsResponse = await fetch(
  `http://localhost:8000/api/v1/questions/${session_id}`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);
const { questions } = await questionsResponse.json();
```

---

## Testing

### Postman Collection
Import the Postman collection: [Download](./StudyBuddy.postman_collection.json)

### cURL Examples

**Register:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "mobile_number": "+919876543210",
    "password": "SecurePass123",
    "full_name": "John Doe",
    "email": "john@example.com"
  }'
```

**Upload File:**
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@anatomy.pdf"
```

**Get Questions:**
```bash
curl -X GET http://localhost:8000/api/v1/questions/SESSION_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

