from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from enum import Enum

class ProcessingMode(str, Enum):
    OCR_AI = "ocr_ai"
    AI_ONLY = "ai_only"

class InputType(str, Enum):
    FILE_UPLOAD = "file_upload"
    TEXT_INPUT = "text_input"

class DocumentType(str, Enum):
    CONTAINS_QUESTIONS = "contains_questions"
    STUDY_NOTES = "study_notes"
    MIXED = "mixed"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class ProcessingStep(str, Enum):
    UPLOAD_COMPLETE = "upload_complete"
    FILE_ANALYSIS = "file_analysis"
    OCR_PROCESSING = "ocr_processing"
    AI_PROCESSING = "ai_processing"
    GENERATING_QUESTIONS = "generating_questions"
    GENERATING_MOCK_TESTS = "generating_mock_tests"
    GENERATING_MNEMONICS = "generating_mnemonics"
    GENERATING_CHEAT_SHEETS = "generating_cheat_sheets"
    GENERATING_NOTES = "generating_notes"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"

class SessionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Batching Models
class TextBatch(BaseModel):
    batch_id: str = Field(..., description="Unique batch identifier")
    session_id: str = Field(..., description="Associated session")
    page_range: Tuple[int, int] = Field(..., description="Start and end page numbers")
    text_content: str = Field(..., description="Extracted text from pages")
    batch_number: int = Field(..., description="Batch sequence number (1-indexed)")
    total_batches: int = Field(..., description="Total number of batches in session")

class BatchContent(BaseModel):
    batch_id: str = Field(..., description="Associated batch identifier")
    questions: List[Dict[str, Any]] = Field(default=[], description="Generated questions")
    mnemonics: List[Dict[str, Any]] = Field(default=[], description="Generated mnemonics")
    cheat_sheet_points: List[str] = Field(default=[], description="Cheat sheet key points")
    key_concepts: List[str] = Field(default=[], description="Key concepts identified")

# Base Models
class StudySession(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    session_name: str = Field(..., description="Auto-generated session name")
    files: List[str] = Field(default=[], description="List of uploaded file paths")
    file_urls: List[str] = Field(default=[], description="List of file URLs (S3 or local)")
    s3_keys: List[Optional[str]] = Field(default=[], description="List of S3 keys (None for local files)")
    processing_mode: ProcessingMode = Field(default=ProcessingMode.AI_ONLY, description="Processing mode used")
    input_type: InputType = Field(default=InputType.FILE_UPLOAD, description="Type of input: file or text")
    text_input: Optional[str] = Field(None, description="Topic text for text-only input mode")
    status: SessionStatus = Field(default=SessionStatus.PENDING, description="Current status")
    
    # Progress tracking
    current_step: Optional[ProcessingStep] = Field(None, description="Current processing step")
    step_progress: int = Field(default=0, description="Progress of current step (0-100)")
    overall_progress: int = Field(default=0, description="Overall progress (0-100)")
    estimated_time_remaining: Optional[int] = Field(None, description="Estimated time remaining in seconds")
    pages_processed: Optional[int] = Field(None, description="Number of pages processed")
    total_pages: Optional[int] = Field(None, description="Total number of pages")
    step_message: Optional[str] = Field(None, description="Current step message")
    
    # Email notification
    email_notification_enabled: bool = Field(default=False, description="Email notification on completion")
    notification_email: Optional[str] = Field(None, description="Email for notifications")
    
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
    processing_mode: ProcessingMode = ProcessingMode.OCR_AI

class UploadResponse(BaseModel):
    session_id: str
    message: str
    files_uploaded: int

class ProcessingStep(str, Enum):
    UPLOAD_COMPLETE = "upload_complete"
    FILE_ANALYSIS = "file_analysis"
    OCR_PROCESSING = "ocr_processing"
    AI_PROCESSING = "ai_processing"
    GENERATING_QUESTIONS = "generating_questions"
    GENERATING_MOCK_TESTS = "generating_mock_tests"
    GENERATING_MNEMONICS = "generating_mnemonics"
    GENERATING_CHEAT_SHEETS = "generating_cheat_sheets"
    GENERATING_NOTES = "generating_notes"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessingProgress(BaseModel):
    current_step: ProcessingStep
    step_progress: int  # 0-100 for current step
    overall_progress: int  # 0-100 overall
    estimated_time_remaining: Optional[int] = None  # seconds
    pages_processed: Optional[int] = None
    total_pages: Optional[int] = None
    step_message: Optional[str] = None

class ProcessingStatusResponse(BaseModel):
    session_id: str
    status: SessionStatus
    progress: Optional[ProcessingProgress] = None
    message: Optional[str] = None
    error_message: Optional[str] = None
    email_notification_enabled: bool = False

class SessionListResponse(BaseModel):
    sessions: List[StudySession]
    total_count: int

class QuestionListResponse(BaseModel):
    questions: List[Question]
    total_count: int

class MockTestListResponse(BaseModel):
    mock_tests: List[MockTest]
    total_count: int
