# Remaining Implementation Guide

## Summary of Progress

We've successfully implemented **Tasks 1-5.3** (approximately 30% of the total implementation):

✅ **Core Foundation Complete:**
- Safety settings for medical content
- Document type detection (questions vs notes)
- Intelligent question handling (extract vs generate)
- Batch creation logic
- OCR batching support

## Critical Remaining Tasks

### HIGH PRIORITY (Core Functionality)

#### 1. Complete Task 5.4-5.5: Finish Batching
```python
# In file_processor.py, add:
async def extract_text_ai_batched(self, file_path: str, session_id: str) -> List[TextBatch]:
    """Extract text using AI with batching support"""
    batches = self.create_batches(file_path, session_id)
    # Similar to extract_text_ocr_batched but uses AI
    # Process each batch with AI vision model
    return batches
```

#### 2. Task 6: Batch Content Generation
```python
# In ai_service.py, add:
async def generate_content_from_batch(self, batch: TextBatch, document_type: DocumentType) -> BatchContent:
    """Generate all content types from a single batch"""
    # Generate questions, mnemonics, cheat sheet points in parallel
    questions = await self.generate_questions(batch.text_content, num_questions=5)
    mnemonics = await self.generate_mnemonics(batch.text_content, num_mnemonics=3)
    # Extract key points for cheat sheets
    return BatchContent(
        batch_id=batch.batch_id,
        questions=questions,
        mnemonics=mnemonics,
        cheat_sheet_points=[],
        key_concepts=[]
    )
```

#### 3. Task 7: Content Aggregation
```python
# Create new file: backend/app/services/content_aggregator.py
class ContentAggregator:
    async def aggregate_questions(self, batch_contents: List[BatchContent]) -> List[Question]:
        """Combine all questions from batches"""
        all_questions = []
        for batch_content in batch_contents:
            all_questions.extend(batch_content.questions)
        return all_questions
    
    async def aggregate_mnemonics(self, batch_contents: List[BatchContent]) -> List[Mnemonic]:
        """Combine all mnemonics from batches"""
        pass
    
    async def aggregate_cheat_sheets(self, batch_contents: List[BatchContent]) -> List[CheatSheet]:
        """Combine cheat sheet points into comprehensive sheets"""
        pass
    
    async def compile_notes(self, questions, mnemonics, cheat_sheets, summary) -> Note:
        """Compile comprehensive notes from all content"""
        pass
```

#### 4. Task 9: Mock Test Generator
```python
# Create new file: backend/app/services/mock_test_generator.py
class MockTestGenerator:
    async def create_mock_test_from_questions(
        self, 
        session_id: str, 
        questions: List[Question],
        session_name: str
    ) -> MockTest:
        """Create mock test from existing questions - NO AI CALLS"""
        total_questions = len(questions)
        duration = max(15, min(90, int(total_questions * 1.5)))
        
        return MockTest(
            test_id=str(uuid.uuid4()),
            session_id=session_id,
            user_id=questions[0].user_id if questions else "",
            test_name=f"Mock Test - {session_name}",
            questions=[q.question_id for q in questions],
            duration_minutes=duration,
            total_questions=total_questions
        )
```

#### 5. Task 11: Text-Only Input
```python
# In models.py, add:
class InputType(str, Enum):
    FILE_UPLOAD = "file_upload"
    TEXT_INPUT = "text_input"

# Update StudySession model to include:
text_input: Optional[str] = None
input_type: InputType = InputType.FILE_UPLOAD
document_type: Optional[DocumentType] = None

# In upload.py, add new endpoint:
@router.post("/text-input")
async def process_text_input(
    topic: str = Form(...),
    user_id: str = Form(...),
    db=Depends(get_database)
):
    """Process text-only input without files"""
    session_id = str(uuid.uuid4())
    # Create session with text_input
    # Call processing_service.process_text_input()
    pass
```

#### 6. Task 13: Enhanced Processing Workflow
```python
# Update processing.py start_processing() to:
async def start_processing(self, session_id: str, files: List[str], mode: ProcessingMode, user_id: str):
    # 1. Create batches
    batches = await self.file_processor.extract_text_ocr_batched(files[0], session_id)
    
    # 2. Process each batch
    batch_contents = []
    for batch in batches:
        content = await self.ai_service.generate_content_from_batch(batch, doc_type)
        batch_contents.append(content)
        # Update progress
    
    # 3. Aggregate results
    aggregator = ContentAggregator()
    all_questions = await aggregator.aggregate_questions(batch_contents)
    all_mnemonics = await aggregator.aggregate_mnemonics(batch_contents)
    all_cheat_sheets = await aggregator.aggregate_cheat_sheets(batch_contents)
    
    # 4. Create mock test (no AI call)
    mock_test_gen = MockTestGenerator()
    mock_test = await mock_test_gen.create_mock_test_from_questions(session_id, all_questions, session_name)
    
    # 5. Compile notes
    notes = await aggregator.compile_notes(all_questions, all_mnemonics, all_cheat_sheets, summary)
    
    # 6. Store everything
    pass
```

#### 7. Task 14: Error Handling
```python
# Create new file: backend/app/utils/error_handler.py
class ErrorHandler:
    @staticmethod
    async def handle_ai_error(error: Exception, context: Dict) -> Dict:
        """Handle AI service errors with appropriate user messages"""
        if "rate limit" in str(error).lower():
            return {
                "user_message": "AI service rate limit exceeded. Please try again in a few minutes.",
                "recovery_action": "RETRY_LATER"
            }
        elif "authentication" in str(error).lower():
            return {
                "user_message": "AI service authentication failed. Please contact support.",
                "recovery_action": "CONTACT_SUPPORT"
            }
        else:
            return {
                "user_message": f"Processing failed: {str(error)}",
                "recovery_action": "RETRY"
            }
    
    @staticmethod
    async def handle_ocr_fallback(file_path: str, session_id: str):
        """Fallback to AI_ONLY mode when OCR fails"""
        logger.warning(f"OCR failed for {file_path}, falling back to AI_ONLY mode")
        # Switch processing mode and retry
        pass
```

### MEDIUM PRIORITY (Enhancement Features)

#### Task 15: Session History
```python
# In upload.py or new sessions.py, add:
@router.get("/sessions/{user_id}")
async def get_user_sessions(user_id: str, db=Depends(get_database)):
    """Get all sessions for a user"""
    sessions = await db.study_sessions.find(
        {"user_id": user_id}
    ).sort("created_at", -1).to_list(length=100)
    return {"sessions": sessions, "total_count": len(sessions)}

@router.get("/sessions/detail/{session_id}")
async def get_session_detail(session_id: str, db=Depends(get_database)):
    """Get session with all five output types"""
    session = await db.study_sessions.find_one({"session_id": session_id})
    questions = await db.questions.find({"session_id": session_id}).to_list(length=None)
    mock_tests = await db.mock_tests.find({"session_id": session_id}).to_list(length=None)
    mnemonics = await db.mnemonics.find({"session_id": session_id}).to_list(length=None)
    cheat_sheets = await db.cheat_sheets.find({"session_id": session_id}).to_list(length=None)
    notes = await db.notes.find({"session_id": session_id}).to_list(length=None)
    
    return {
        "session": session,
        "questions": questions,
        "mock_tests": mock_tests,
        "mnemonics": mnemonics,
        "cheat_sheets": cheat_sheets,
        "notes": notes
    }
```

#### Task 16: Progress Tracking
```python
# Update progress_tracker.py to include:
async def update_batch_progress(session_id: str, batch_number: int, total_batches: int):
    """Update progress for batch processing"""
    overall_progress = int((batch_number / total_batches) * 100)
    await update_progress(
        session_id,
        ProcessingStep.GENERATING_QUESTIONS,
        overall_progress,
        f"Processing batch {batch_number} of {total_batches}"
    )
```

### LOW PRIORITY (Testing)

#### Task 17: Integration Tests
```python
# Create backend/tests/test_integration.py
@pytest.mark.asyncio
async def test_small_pdf_processing():
    """Test end-to-end processing for PDF with ≤5 pages"""
    # Upload 3-page PDF
    # Verify single batch created
    # Verify all five outputs generated
    pass

@pytest.mark.asyncio
async def test_large_pdf_processing():
    """Test end-to-end processing for PDF with >5 pages"""
    # Upload 10-page PDF
    # Verify multiple batches created (2-3 pages each)
    # Verify all outputs aggregated correctly
    pass

@pytest.mark.asyncio
async def test_text_only_input():
    """Test processing text-only input"""
    # Submit topic text
    # Verify AI_ONLY mode used
    # Verify all five outputs generated
    pass
```

## Quick Implementation Checklist

- [ ] Complete batching (Tasks 5.4-5.5)
- [ ] Add batch content generation (Task 6)
- [ ] Create ContentAggregator (Task 7)
- [ ] Create MockTestGenerator (Task 9)
- [ ] Add notes compilation (Task 10)
- [ ] Add text-only input (Task 11)
- [ ] Update processing workflow (Task 13)
- [ ] Add error handling (Task 14)
- [ ] Add session history endpoints (Task 15)
- [ ] Enhance progress tracking (Task 16)
- [ ] Write integration tests (Task 17)

## Testing Commands

```bash
# Run all tests
cd backend
pytest tests/ -v

# Run specific test file
pytest tests/test_ai_service.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Key Design Principles to Follow

1. **Batching**: Always process large documents in batches of 2-3 pages
2. **No Redundant AI Calls**: Mock tests use existing questions
3. **Error Recovery**: Always have fallback mechanisms
4. **Progress Tracking**: Update progress after each batch
5. **Safety Settings**: All AI calls use BLOCK_NONE for medical content
6. **Aggregation**: Combine batch results into single collections per session

## Files to Create

1. `backend/app/services/content_aggregator.py`
2. `backend/app/services/mock_test_generator.py`
3. `backend/app/utils/error_handler.py`
4. `backend/tests/test_integration.py`
5. `backend/tests/test_batching.py`
6. `backend/tests/test_aggregation.py`

## Files to Modify

1. `backend/app/services/processing.py` - Update start_processing()
2. `backend/app/services/file_processor.py` - Complete batching methods
3. `backend/app/services/ai_service.py` - Add batch content generation
4. `backend/app/api/v1/endpoints/upload.py` - Add text input endpoint
5. `backend/app/models.py` - Add InputType enum, update StudySession
6. `backend/app/services/progress_tracker.py` - Add batch progress tracking

## Priority Order for Implementation

1. **First**: Complete batching (critical for large documents)
2. **Second**: Content aggregation (combines batch results)
3. **Third**: Mock test generator (uses aggregated questions)
4. **Fourth**: Enhanced processing workflow (ties everything together)
5. **Fifth**: Error handling (makes system robust)
6. **Sixth**: Text-only input (additional feature)
7. **Last**: Integration tests (validates everything works)

Good luck with the remaining implementation! The foundation is solid, and the remaining tasks follow clear patterns.
