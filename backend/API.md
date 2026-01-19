# Backend API Endpoints

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints require JWT authentication (except health checks).
Include in header: `Authorization: Bearer <token>`

## Endpoints

### Health & Status
- `GET /` - API root information
- `GET /health` - Health check

### File Upload & Processing
- `POST /upload` - Upload files and start processing
- `GET /upload/status/{session_id}` - Get processing status

### Session Management
- `GET /sessions?user_id={user_id}` - Get user sessions
- `GET /sessions/{session_id}` - Get session details
- `DELETE /sessions/{session_id}` - Delete session

### Generated Content
- `GET /questions/{session_id}` - Get session questions
- `GET /questions/question/{question_id}` - Get specific question
- `GET /mock-tests/{session_id}` - Get session mock tests
- `GET /mock-tests/test/{test_id}` - Get specific mock test
- `GET /mnemonics/{session_id}` - Get session mnemonics
- `GET /mnemonics/mnemonic/{mnemonic_id}` - Get specific mnemonic
- `GET /cheat-sheets/{session_id}` - Get session cheat sheets
- `GET /cheat-sheets/sheet/{sheet_id}` - Get specific cheat sheet
- `GET /notes/{session_id}` - Get session notes
- `GET /notes/note/{note_id}` - Get specific note

## Request/Response Examples

### Upload Files
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document.pdf" \
  -F "processing_mode=default" \
  -F "user_id=user123"
```

Response:
```json
{
  "session_id": "uuid-here",
  "message": "Files uploaded successfully. Processing started.",
  "files_uploaded": 1
}
```

### Get Questions
```bash
curl "http://localhost:8000/api/v1/questions/session-id-here"
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
