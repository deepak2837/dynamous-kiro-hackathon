# Design Document: Content Generation Enhancement

## Overview

This design enhances the Study Buddy App's content generation pipeline to intelligently handle different document types, process large documents efficiently through batching, support text-only input, and provide robust error handling. The system will generate five types of study materials (question banks, mock tests, mnemonics, cheat sheets, and notes) from uploaded PDFs, images, presentations, or text input.

## Architecture

### High-Level Flow

```
User Upload → File Validation → Text Extraction (Batched) → Content Generation (Parallel) → Storage → User Retrieval
```

### Component Interaction

```
┌─────────────────┐
│  Upload API     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ File Processor  │──────┐
└────────┬────────┘      │
         │               │
         ▼               ▼
┌─────────────────┐  ┌──────────────┐
│  OCR Service    │  │  AI Service  │
└────────┬────────┘  └──────┬───────┘
         │                  │
         └──────┬───────────┘
                │
                ▼
┌─────────────────────────────┐
│   Processing Service        │
│  - Batch Coordinator        │
│  - Content Aggregator       │
│  - Progress Tracker         │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────┐
│   MongoDB       │
│  - Questions    │
│  - Mock Tests   │
│  - Mnemonics    │
│  - Cheat Sheets │
│  - Notes        │
└─────────────────┘
```

## Components and Interfaces

### 1. Enhanced File Processor

**Purpose:** Extract text from files with intelligent batching for large documents

**Interface:**
```python
class FileProcessor:
    async def extract_text_with_batching(
        self, 
        file_path: str, 
        mode: ProcessingMode,
        session_id: str
    ) -> List[TextBatch]:
        """
        Extract text in batches based on document size
        Returns list of TextBatch objects for processing
        """
        pass
    
    async def detect_document_type(self, text: str) -> DocumentType:
        """
        Analyze text to determine if it contains questions or study notes
        Returns: CONTAINS_QUESTIONS or STUDY_NOTES
        """
        pass
```

**TextBatch Model:**
```python
class TextBatch:
    batch_id: str
    session_id: str
    page_range: Tuple[int, int]  # (start_page, end_page)
    text_content: str
    batch_number: int
    total_batches: int
```

### 2. Enhanced AI Service

**Purpose:** Generate content with intelligent question handling and safety settings

**Interface:**
```python
class AIService:
    def __init__(self):
        # Configure with safety settings
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        }
    
    async def generate_content_from_batch(
        self,
        batch: TextBatch,
        document_type: DocumentType
    ) -> BatchContent:
        """
        Generate all content types from a single batch
        Handles both question extraction and generation
        """
        pass
    
    async def extract_existing_questions(self, text: str) -> List[Question]:
        """Extract questions that already exist in the document"""
        pass
    
    async def generate_new_questions(self, text: str) -> List[Question]:
        """Generate new questions from study notes"""
        pass
    
    async def generate_from_text_input(self, topic: str) -> Dict[str, Any]:
        """Generate all content types from text-only input"""
        pass
```

**BatchContent Model:**
```python
class BatchContent:
    batch_id: str
    questions: List[Dict[str, Any]]
    mnemonics: List[Dict[str, Any]]
    cheat_sheet_points: List[str]
    key_concepts: List[str]
```

### 3. Content Aggregator

**Purpose:** Combine batch results into final output collections

**Interface:**
```python
class ContentAggregator:
    async def aggregate_questions(
        self,
        batch_contents: List[BatchContent]
    ) -> List[Question]:
        """Combine all questions from batches into single Question_Bank"""
        pass
    
    async def aggregate_mnemonics(
        self,
        batch_contents: List[BatchContent]
    ) -> List[Mnemonic]:
        """Combine all mnemonics from batches"""
        pass
    
    async def aggregate_cheat_sheets(
        self,
        batch_contents: List[BatchContent]
    ) -> List[CheatSheet]:
        """Combine cheat sheet points into comprehensive sheets"""
        pass
    
    async def compile_notes(
        self,
        questions: List[Question],
        mnemonics: List[Mnemonic],
        cheat_sheets: List[CheatSheet],
        summary: str
    ) -> Note:
        """Compile comprehensive notes from all content"""
        pass
```

### 4. Mock Test Generator

**Purpose:** Create mock tests from existing question bank without AI calls

**Interface:**
```python
class MockTestGenerator:
    async def create_mock_test_from_questions(
        self,
        session_id: str,
        questions: List[Question],
        session_name: str
    ) -> MockTest:
        """
        Create one comprehensive mock test from question bank
        No AI API calls - uses existing questions
        """
        pass
```

### 5. Enhanced Processing Service

**Purpose:** Orchestrate the entire processing workflow with batching

**Interface:**
```python
class ProcessingService:
    async def process_with_batching(
        self,
        session_id: str,
        files: List[str],
        mode: ProcessingMode,
        user_id: str
    ) -> None:
        """
        Main processing workflow with batching support
        """
        # 1. Extract text in batches
        # 2. Detect document type
        # 3. Process each batch (parallel content generation)
        # 4. Aggregate results
        # 5. Create mock test from questions
        # 6. Compile notes
        # 7. Store all content
        pass
    
    async def process_text_input(
        self,
        session_id: str,
        topic: str,
        user_id: str
    ) -> None:
        """Process text-only input without files"""
        pass
```

## Data Models

### Enhanced Session Model

```python
class StudySession(BaseModel):
    session_id: str
    user_id: str
    session_name: str
    
    # Input
    files: List[str] = []
    text_input: Optional[str] = None  # NEW: For text-only input
    input_type: InputType  # NEW: FILE_UPLOAD or TEXT_INPUT
    
    # Processing
    processing_mode: ProcessingMode
    document_type: Optional[DocumentType] = None  # NEW: CONTAINS_QUESTIONS or STUDY_NOTES
    total_pages: Optional[int] = None
    total_batches: Optional[int] = None
    batches_processed: int = 0
    
    # Status
    status: SessionStatus
    current_step: Optional[ProcessingStep] = None
    step_progress: int = 0
    overall_progress: int = 0
    step_message: Optional[str] = None
    error_message: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    completed_at: Optional[datetime] = None
```

### New Enums

```python
class InputType(str, Enum):
    FILE_UPLOAD = "file_upload"
    TEXT_INPUT = "text_input"

class DocumentType(str, Enum):
    CONTAINS_QUESTIONS = "contains_questions"
    STUDY_NOTES = "study_notes"
    MIXED = "mixed"
```

## Processing Workflows

### Workflow 1: File Upload with Batching (PDF > 5 pages)

```
1. User uploads PDF (50 pages)
2. File Processor counts pages → 50 pages
3. File Processor creates batches:
   - Batch 1: Pages 1-3
   - Batch 2: Pages 4-6
   - ...
   - Batch 17: Pages 49-50
4. For each batch:
   a. Extract text (OCR or AI)
   b. Send to AI Service
   c. Generate questions, mnemonics, cheat sheet points
   d. Store BatchContent
   e. Update progress (batch X of 17)
5. After all batches:
   a. Aggregate all questions → Question_Bank
   b. Aggregate all mnemonics → Mnemonics collection
   c. Aggregate cheat sheet points → Cheat_Sheets
   d. Create Mock_Test from Question_Bank (no AI call)
   e. Compile Notes from all content
6. Store all final content in database
7. Mark session as COMPLETED
```

### Workflow 2: Small File Upload (PDF ≤ 5 pages)

```
1. User uploads PDF (3 pages)
2. File Processor counts pages → 3 pages
3. Process all pages together:
   a. Extract text from all pages
   b. Send to AI Service once
   c. Generate all content types
4. Store content in database
5. Mark session as COMPLETED
```

### Workflow 3: Text-Only Input

```
1. User enters topic: "Heart Anatomy"
2. Create session with input_type=TEXT_INPUT
3. AI Service generates content from topic:
   a. Generate questions about heart anatomy
   b. Generate mnemonics for heart structures
   c. Generate cheat sheet with key points
   d. Generate study notes
4. Create Mock_Test from questions
5. Store all content in database
6. Mark session as COMPLETED
```

### Workflow 4: Document with Existing Questions

```
1. User uploads PDF with practice questions
2. File Processor extracts text
3. AI Service detects document_type=CONTAINS_QUESTIONS
4. AI Service extracts existing questions:
   - Preserves original format
   - Maintains options and explanations
   - Adds to Question_Bank
5. AI Service also generates:
   - Mnemonics for key concepts
   - Cheat sheets from content
   - Study notes
6. Create Mock_Test from extracted questions
7. Store all content
```

## Error Handling Strategy

### Error Types and Responses

| Error Type | Detection | Response | User Message |
|------------|-----------|----------|--------------|
| AI API Rate Limit | HTTP 429 from Gemini | Log error, mark session FAILED | "AI service rate limit exceeded. Please try again in a few minutes." |
| AI API Key Invalid | HTTP 401 from Gemini | Log error, mark session FAILED | "AI service authentication failed. Please contact support." |
| AI Content Blocked | Safety filter triggered | Retry with BLOCK_NONE settings | "Processing medical content..." |
| OCR Failure | Exception in pytesseract | Fallback to AI_ONLY mode | "OCR failed, using AI-based extraction..." |
| No Text Extracted | Empty text after extraction | Mark session FAILED | "Could not extract text from uploaded files. Please ensure files contain readable content." |
| Partial Batch Failure | Exception in batch processing | Continue with remaining batches, note partial results | "Some pages could not be processed. Generated content from X of Y pages." |
| Database Error | MongoDB exception | Log error, retry once | "Database error. Retrying..." |

### Error Recovery

```python
class ErrorHandler:
    async def handle_ai_error(self, error: Exception, context: Dict) -> ErrorResponse:
        """
        Centralized error handling for AI service failures
        Returns appropriate user message and recovery action
        """
        if isinstance(error, RateLimitError):
            return ErrorResponse(
                user_message="AI service rate limit exceeded. Please try again in a few minutes.",
                recovery_action="RETRY_LATER",
                technical_details=str(error)
            )
        elif isinstance(error, AuthenticationError):
            return ErrorResponse(
                user_message="AI service authentication failed. Please contact support.",
                recovery_action="CONTACT_SUPPORT",
                technical_details=str(error)
            )
        # ... handle other error types
```

## Testing Strategy

### Unit Tests

- Test batch creation logic for different page counts
- Test document type detection (questions vs notes)
- Test content aggregation from multiple batches
- Test mock test generation from question bank
- Test error handling for each error type
- Test safety settings configuration

### Integration Tests

- Test end-to-end processing for small PDFs (≤5 pages)
- Test end-to-end processing for large PDFs (>5 pages)
- Test text-only input processing
- Test processing with existing questions in document
- Test OCR fallback to AI_ONLY on failure
- Test partial batch failure recovery

### Property-Based Tests

See Correctness Properties section below for detailed property definitions.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified the following redundancies:
- Properties 2.1-2.4 all test batch creation logic and can be combined into one comprehensive batching property
- Properties 3.2, 3.3, 3.4 all test aggregation and can be combined into one aggregation property
- Properties 4.1 and 4.3 both test mock test creation from questions and can be combined
- Properties 5.1, 5.2, 5.3 all test Notes compilation and can be combined
- Properties 9.2, 9.3, 9.4 all test session data completeness and can be combined

### Core Properties

**Property 1: Question Extraction Preserves Format**
*For any* document containing questions, extracting then storing those questions should preserve the original question text, options, correct answer index, and explanation.
**Validates: Requirements 1.1, 1.4**

**Property 2: Question Generation for Study Notes**
*For any* document identified as study notes (no existing questions), the generated Question_Bank should contain at least one question.
**Validates: Requirements 1.2**

**Property 3: Document Type Detection**
*For any* document, the AI_Service should classify it as either CONTAINS_QUESTIONS, STUDY_NOTES, or MIXED based on content analysis.
**Validates: Requirements 1.3**

**Property 4: Batch Size Correctness**
*For any* PDF document, if page_count ≤ 5 then batch_count = 1, and if page_count > 5 then each batch should contain 2-3 pages (except possibly the last batch).
**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

**Property 5: Single Question Bank Per Session**
*For any* session with multiple batches, there should be exactly one Question_Bank containing all questions from all batches, and the total question count should equal the sum of questions from each batch.
**Validates: Requirements 2.5, 3.2**

**Property 6: Progress Monotonicity**
*For any* session during processing, the overall_progress and pages_processed values should never decrease, and pages_processed should always be ≤ total_pages.
**Validates: Requirements 2.6, 10.2, 10.4**

**Property 7: Parallel Content Generation**
*For any* processed batch, the resulting BatchContent should contain questions, mnemonics, and cheat_sheet_points (all three types non-empty).
**Validates: Requirements 3.1**

**Property 8: Content Aggregation Completeness**
*For any* session, the total count of items in final collections (Question_Bank, Mnemonics, Cheat_Sheets) should equal the sum of items from all BatchContent objects.
**Validates: Requirements 3.2, 3.3, 3.4**

**Property 9: Mock Test Without AI Calls**
*For any* mock test generation, the AI service should not be invoked, and the mock test should contain all question IDs from the Question_Bank.
**Validates: Requirements 3.5, 4.1, 4.2, 4.3**

**Property 10: Mock Test Duration Calculation**
*For any* mock test with N questions, the duration_minutes should equal N * 1.5 (rounded appropriately).
**Validates: Requirements 4.4**

**Property 11: Notes Compilation Completeness**
*For any* compiled Notes, it should reference questions from Question_Bank (important_questions non-empty), include content from Cheat_Sheets, and reference Mnemonics (related_mnemonics non-empty).
**Validates: Requirements 3.6, 5.1, 5.2, 5.3, 5.4**

**Property 12: Text Input Mode Selection**
*For any* session with text_input (no files), the processing_mode should be AI_ONLY and session.files should be empty.
**Validates: Requirements 6.1, 6.4, 6.5**

**Property 13: Text Input Content Generation**
*For any* text-only input session, all five output collections (questions, mock_tests, mnemonics, cheat_sheets, notes) should be non-empty after processing.
**Validates: Requirements 6.2, 6.3**

**Property 14: OCR Fallback on Failure**
*For any* session where OCR processing fails, the system should switch processing_mode to AI_ONLY and continue processing.
**Validates: Requirements 8.4**

**Property 15: Error State Consistency**
*For any* session where processing fails, the session.status should be FAILED, error_message should be non-empty, and any partial results should remain in the database.
**Validates: Requirements 8.1, 8.5, 8.6**

**Property 16: Session History Completeness**
*For any* user_id, retrieving session history should return all sessions where session.user_id matches, sorted by created_at descending.
**Validates: Requirements 9.1**

**Property 17: Session Data Completeness**
*For any* completed session, it should have either files or text_input populated, status should be COMPLETED, and all five output types should be retrievable from database.
**Validates: Requirements 9.2, 9.3, 9.4**

**Property 18: Progress Completion State**
*For any* session with status=COMPLETED, the overall_progress should be 100 and completed_at should be set.
**Validates: Requirements 10.5**

### Edge Cases

The following edge cases will be handled by property test generators:

- **Empty documents**: Documents with no extractable text
- **Very large documents**: PDFs with 100+ pages
- **Mixed content**: Documents with both questions and study notes
- **Malformed questions**: Questions missing options or answers
- **Special characters**: Medical terminology with Unicode characters
- **API failures mid-batch**: Failures occurring during batch processing
- **Concurrent sessions**: Multiple users processing simultaneously

