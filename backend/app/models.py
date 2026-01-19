from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ProcessingMode(str, Enum):
    DEFAULT = "default"
    OCR = "ocr"
    AI_BASED = "ai_based"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class SessionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Base Models
class StudySession(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    session_name: str = Field(..., description="Auto-generated session name")
    files: List[str] = Field(default=[], description="List of uploaded file paths")
    file_urls: List[str] = Field(default=[], description="List of file URLs (S3 or local)")
    s3_keys: List[Optional[str]] = Field(default=[], description="List of S3 keys (None for local files)")
    processing_mode: ProcessingMode = Field(..., description="Processing mode used")
    status: SessionStatus = Field(default=SessionStatus.PENDING, description="Current status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    last_upload_time: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Last upload timestamp")

class Question(BaseModel):
    question_id: str = Field(..., description="Unique question identifier")
    session_id: str = Field(..., description="Associated session")
    user_id: str = Field(..., description="User identifier")
    question_text: str = Field(..., description="The question text")
    options: List[str] = Field(..., description="Multiple choice options")
    correct_answer: int = Field(..., description="Index of correct answer (0-based)")
    explanation: str = Field(..., description="Explanation for the answer")
    difficulty: DifficultyLevel = Field(..., description="Question difficulty")
    topic: Optional[str] = Field(None, description="Medical topic/subject")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MockTest(BaseModel):
    test_id: str = Field(..., description="Unique test identifier")
    session_id: str = Field(..., description="Associated session")
    user_id: str = Field(..., description="User identifier")
    test_name: str = Field(..., description="Auto-generated test name")
    questions: List[str] = Field(..., description="List of question IDs")
    duration_minutes: int = Field(default=60, description="Test duration")
    total_questions: int = Field(..., description="Number of questions")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Mnemonic(BaseModel):
    mnemonic_id: str = Field(..., description="Unique mnemonic identifier")
    session_id: str = Field(..., description="Associated session")
    user_id: str = Field(..., description="User identifier")
    topic: str = Field(..., description="Topic for the mnemonic")
    mnemonic_text: str = Field(..., description="The mnemonic content")
    explanation: str = Field(..., description="What the mnemonic helps remember")
    key_terms: List[str] = Field(default=[], description="Key terms highlighted")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CheatSheet(BaseModel):
    sheet_id: str = Field(..., description="Unique sheet identifier")
    session_id: str = Field(..., description="Associated session")
    user_id: str = Field(..., description="User identifier")
    title: str = Field(..., description="Cheat sheet title")
    key_points: List[str] = Field(..., description="List of key points")
    high_yield_facts: List[str] = Field(..., description="High-yield facts")
    quick_references: Dict[str, str] = Field(default={}, description="Quick reference mappings")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Note(BaseModel):
    note_id: str = Field(..., description="Unique note identifier")
    session_id: str = Field(..., description="Associated session")
    user_id: str = Field(..., description="User identifier")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Compiled note content")
    important_questions: List[str] = Field(default=[], description="Important question IDs")
    summary_points: List[str] = Field(default=[], description="Summary points")
    related_mnemonics: List[str] = Field(default=[], description="Related mnemonic IDs")
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Request/Response Models
class UploadRequest(BaseModel):
    processing_mode: ProcessingMode = ProcessingMode.DEFAULT

class UploadResponse(BaseModel):
    session_id: str
    message: str
    files_uploaded: int

class ProcessingStatusResponse(BaseModel):
    session_id: str
    status: SessionStatus
    progress_percentage: Optional[int] = None
    message: Optional[str] = None
    error_message: Optional[str] = None

class SessionListResponse(BaseModel):
    sessions: List[StudySession]
    total_count: int

class QuestionListResponse(BaseModel):
    questions: List[Question]
    total_count: int

class MockTestListResponse(BaseModel):
    mock_tests: List[MockTest]
    total_count: int
