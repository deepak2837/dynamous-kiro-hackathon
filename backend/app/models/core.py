"""
Study Buddy App - Core Data Models

This module defines the core Pydantic models used throughout the Study Buddy App
for data validation, serialization, and API request/response handling.

Models include:
- Study session management
- Content generation (questions, tests, mnemonics, etc.)
- Processing pipeline status tracking
- Medical content classification

All models are designed for MBBS-oriented medical education content.

Author: Study Buddy Team
Created: January 2026
License: MIT
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from enum import Enum

class ProcessingMode(str, Enum):
    """
    Processing modes for uploaded content.
    
    AI_ONLY: Advanced AI-based content extraction and analysis
    """
    AI_ONLY = "ai_only"

class InputType(str, Enum):
    """
    Types of input sources for content generation.
    
    FILE_UPLOAD: Content from uploaded files (PDF, images, PPTX)
    TEXT_INPUT: Content from direct text input by user
    """
    FILE_UPLOAD = "file_upload"
    TEXT_INPUT = "text_input"

class DocumentType(str, Enum):
    """
    Classification of document content types for medical materials.
    
    CONTAINS_QUESTIONS: Document has existing questions/MCQs
    STUDY_NOTES: Document contains study notes and explanations
    MIXED: Document contains both questions and study material
    """
    CONTAINS_QUESTIONS = "contains_questions"
    STUDY_NOTES = "study_notes"
    MIXED = "mixed"

class DifficultyLevel(str, Enum):
    """
    Difficulty levels for medical questions and content.
    
    Aligned with MBBS exam difficulty progression.
    """
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class ProcessingStep(str, Enum):
    """
    Processing pipeline steps for content generation.
    
    Tracks the current stage of AI-powered content generation
    from upload to completion.
    """
    UPLOAD_COMPLETE = "upload_complete"
    FILE_ANALYSIS = "file_analysis"
    OCR_PROCESSING = "ocr_processing"
    AI_PROCESSING = "ai_processing"
    GENERATING_QUESTIONS = "generating_questions"
    GENERATING_MOCK_TESTS = "generating_mock_tests"
    GENERATING_MNEMONICS = "generating_mnemonics"
    GENERATING_CHEAT_SHEETS = "generating_cheat_sheets"
    GENERATING_NOTES = "generating_notes"
    GENERATING_FLASHCARDS = "generating_flashcards"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"

class SessionStatus(str, Enum):
    """
    Overall status of a study session.
    
    PENDING: Session created, processing not started
    PROCESSING: AI content generation in progress
    COMPLETED: All content generated successfully
    FAILED: Processing failed due to error
    """
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Batching Models
class TextBatch(BaseModel):
    """
    Text batch for processing large documents in chunks.
    
    Used to handle large PDF files by processing them in manageable
    batches to avoid AI API limits and improve processing efficiency.
    """
    batch_id: str = Field(..., description="Unique batch identifier")
    session_id: str = Field(..., description="Associated session")
    page_range: Tuple[int, int] = Field(..., description="Start and end page numbers")
    text_content: str = Field(..., description="Extracted text from pages")
    batch_number: int = Field(..., description="Batch sequence number (1-indexed)")
    total_batches: int = Field(..., description="Total number of batches in session")

class BatchContent(BaseModel):
    """
    Generated content for a specific text batch.
    
    Stores AI-generated content for each batch of processed text,
    allowing for incremental content generation and aggregation.
    """
    batch_id: str = Field(..., description="Associated batch identifier")
    questions: List[Dict[str, Any]] = Field(default=[], description="Generated questions")
    mnemonics: List[Dict[str, Any]] = Field(default=[], description="Generated mnemonics")
    cheat_sheet_points: List[str] = Field(default=[], description="Cheat sheet key points")
    key_concepts: List[str] = Field(default=[], description="Key concepts identified")

# Base Models
class StudySession(BaseModel):
    """
    Core study session model for organizing medical study materials.
    
    Represents a complete study session where users upload materials
    and receive AI-generated content for MBBS exam preparation.
    
    Attributes:
        session_id: Unique identifier for the session
        user_id: Reference to the authenticated user
        session_name: Auto-generated descriptive name
        files: List of uploaded file paths
        processing_mode: AI processing mode used
        status: Current processing status
        progress tracking: Real-time progress information
        email_notification: Optional completion notifications
    """
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
    """
    Medical question model for MBBS exam preparation.
    
    Represents AI-generated multiple choice questions with explanations,
    difficulty classification, and topic categorization for medical studies.
    
    Attributes:
        question_id: Unique identifier for the question
        session_id: Reference to the study session
        question_text: The medical question content
        options: List of multiple choice options
        correct_answer: Index of the correct answer (0-based)
        explanation: Detailed explanation for medical concept
        difficulty: Question difficulty level (Easy/Medium/Hard)
        topic: Medical subject area (Anatomy, Physiology, etc.)
    """
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
    """
    Mock test model for medical exam simulation.
    
    Represents a timed mock test created from generated questions,
    designed to simulate MBBS exam conditions and patterns.
    
    Attributes:
        test_id: Unique identifier for the mock test
        session_id: Reference to the study session
        test_name: Auto-generated descriptive name
        questions: List of question IDs included in test
        duration_minutes: Time limit for the test
        total_questions: Number of questions in the test
    """
    test_id: str = Field(..., description="Unique test identifier")
    session_id: str = Field(..., description="Associated session")
    user_id: str = Field(..., description="User identifier")
    test_name: str = Field(..., description="Auto-generated test name")
    questions: List[str] = Field(..., description="List of question IDs")
    duration_minutes: int = Field(default=60, description="Test duration")
    total_questions: int = Field(..., description="Number of questions")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Mnemonic(BaseModel):
    """
    Mnemonic model for medical concept memorization.
    
    Represents AI-generated memory aids specifically designed for
    Indian medical students with culturally relevant associations.
    
    Attributes:
        mnemonic_id: Unique identifier for the mnemonic
        session_id: Reference to the study session
        topic: Medical concept or topic
        mnemonic_text: The memory aid text
        explanation: How the mnemonic relates to the concept
        is_india_specific: Whether it uses Indian cultural references
    """
    mnemonic_id: str = Field(..., description="Unique mnemonic identifier")
    session_id: str = Field(..., description="Associated session")
    user_id: str = Field(..., description="User identifier")
    topic: str = Field(..., description="Topic for the mnemonic")
    mnemonic_text: str = Field(..., description="The mnemonic content")
    explanation: str = Field(..., description="What the mnemonic helps remember")
    key_terms: List[str] = Field(default=[], description="Key terms highlighted")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CheatSheet(BaseModel):
    """
    Cheat sheet model for quick reference study materials.
    
    Represents AI-generated high-yield facts and key points
    organized for rapid review during MBBS exam preparation.
    
    Attributes:
        sheet_id: Unique identifier for the cheat sheet
        session_id: Reference to the study session
        title: Descriptive title for the content area
        key_points: Essential facts and concepts
        high_yield_facts: Most important exam-relevant information
        quick_references: Key-value mappings for rapid lookup
    """
    sheet_id: str = Field(..., description="Unique sheet identifier")
    session_id: str = Field(..., description="Associated session")
    user_id: str = Field(..., description="User identifier")
    title: str = Field(..., description="Cheat sheet title")
    key_points: List[str] = Field(..., description="List of key points")
    high_yield_facts: List[str] = Field(..., description="High-yield facts")
    quick_references: Dict[str, str] = Field(default={}, description="Quick reference mappings")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Note(BaseModel):
    """
    Compiled study notes model for comprehensive review.
    
    Represents AI-aggregated study notes that combine questions,
    mnemonics, and key concepts into organized study materials.
    
    Attributes:
        note_id: Unique identifier for the note
        session_id: Reference to the study session
        title: Descriptive title for the notes
        content: Main compiled content
        important_questions: References to key questions
        summary_points: Condensed summary information
        related_mnemonics: Associated memory aids
    """
    note_id: str = Field(..., description="Unique note identifier")
    session_id: str = Field(..., description="Associated session")
    user_id: str = Field(..., description="User identifier")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Compiled note content")
    important_questions: List[str] = Field(default=[], description="Important question IDs")
    summary_points: List[str] = Field(default=[], description="Summary points")
    related_mnemonics: List[str] = Field(default=[], description="Related mnemonic IDs")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Flashcard(BaseModel):
    """
    Flashcard model for spaced repetition learning.
    
    Represents AI-generated flashcards with spaced repetition data
    for effective long-term retention of medical concepts.
    
    Attributes:
        flashcard_id: Unique identifier for the flashcard
        session_id: Reference to the study session
        front_text: Question or prompt side
        back_text: Answer or explanation side
        category: Medical subject category
        difficulty: Learning difficulty level
        spaced_repetition_data: Algorithm data for optimal review timing
    """
    flashcard_id: str = Field(..., description="Unique flashcard identifier")
    session_id: str = Field(..., description="Associated session")
    user_id: str = Field(..., description="User identifier")
    front_text: str = Field(..., description="Question/prompt side")
    back_text: str = Field(..., description="Answer/explanation side")
    category: str = Field(..., description="Medical category (anatomy, pharmacology, etc.)")
    difficulty: DifficultyLevel = Field(..., description="Flashcard difficulty")
    medical_topic: Optional[str] = Field(None, description="Specific medical topic")
    pronunciation: Optional[str] = Field(None, description="Phonetic pronunciation")
    spaced_repetition_data: Dict[str, Any] = Field(default={}, description="SR algorithm data")
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Request/Response Models
class UploadRequest(BaseModel):
    """Request model for file upload operations."""
    processing_mode: ProcessingMode = ProcessingMode.AI_ONLY

class UploadResponse(BaseModel):
    """Response model for successful file uploads."""
    session_id: str
    message: str
    files_uploaded: int

class ProcessingProgress(BaseModel):
    """Real-time processing progress information."""
    current_step: ProcessingStep
    step_progress: int  # 0-100 for current step
    overall_progress: int  # 0-100 overall
    estimated_time_remaining: Optional[int] = None  # seconds
    pages_processed: Optional[int] = None
    total_pages: Optional[int] = None
    step_message: Optional[str] = None

class ProcessingStatusResponse(BaseModel):
    """Response model for processing status queries."""
    session_id: str
    status: SessionStatus
    progress: Optional[ProcessingProgress] = None
    message: Optional[str] = None
    error_message: Optional[str] = None
    email_notification_enabled: bool = False

class SessionListResponse(BaseModel):
    """Response model for session history listings."""
    sessions: List[StudySession]
    total_count: int

class QuestionListResponse(BaseModel):
    """Response model for question listings."""
    questions: List[Question]
    total_count: int

class MockTestListResponse(BaseModel):
    """Response model for mock test listings."""
    mock_tests: List[MockTest]
    total_count: int
