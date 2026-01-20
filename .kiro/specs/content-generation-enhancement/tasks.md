# Implementation Plan: Content Generation Enhancement

## Overview

This implementation enhances the Study Buddy App's content generation pipeline with intelligent question handling, batched processing for large documents, text-only input support, and robust error handling. Tasks are organized to build incrementally with testing integrated throughout.

## Tasks

- [x] 1. Configure Gemini API with safety settings
  - Update `AIService.__init__()` to set BLOCK_NONE for all harm categories
  - Add logging for safety settings configuration
  - _Requirements: 7.1, 7.4_

- [x] 1.1 Write unit test for safety settings configuration
  - Verify safety_settings dict contains BLOCK_NONE for all HarmCategory values
  - _Requirements: 7.1_

- [x] 2. Implement document type detection
  - [x] 2.1 Add `DocumentType` enum to models.py
    - Add CONTAINS_QUESTIONS, STUDY_NOTES, MIXED values
    - _Requirements: 1.3_

  - [x] 2.2 Implement `AIService.detect_document_type()`
    - Analyze text to identify if it contains questions or study notes
    - Return appropriate DocumentType
    - _Requirements: 1.3_

  - [x] 2.3 Write property test for document type detection
    - **Property 3: Document Type Detection**
    - **Validates: Requirements 1.3**

- [x] 3. Implement intelligent question handling
  - [x] 3.1 Implement `AIService.extract_existing_questions()`
    - Parse text to find existing questions with options and answers
    - Preserve original format and explanations
    - Return list of Question dicts
    - _Requirements: 1.1, 1.4_

  - [x] 3.2 Implement `AIService.generate_new_questions()`
    - Generate MCQs from study notes content
    - Create clinically relevant questions for MBBS students
    - Return list of Question dicts
    - _Requirements: 1.2_

  - [x] 3.3 Update `AIService.generate_questions()` to use detection
    - Call `detect_document_type()` first
    - Route to `extract_existing_questions()` or `generate_new_questions()`
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 3.4 Write property test for question extraction
    - **Property 1: Question Extraction Preserves Format**
    - **Validates: Requirements 1.1, 1.4**

  - [x] 3.5 Write property test for question generation
    - **Property 2: Question Generation for Study Notes**
    - **Validates: Requirements 1.2**

- [x] 4. Checkpoint - Verify question handling works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement batching logic
  - [x] 5.1 Add `TextBatch` model to models.py
    - Add batch_id, session_id, page_range, text_content, batch_number, total_batches fields
    - _Requirements: 2.1, 2.2_

  - [x] 5.2 Implement `FileProcessor.create_batches()`
    - Count total pages in document
    - If pages ≤ 5: create single batch
    - If pages > 5: create batches of 2-3 pages each
    - Return list of TextBatch objects
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 5.3 Update `FileProcessor.extract_text_ocr()` to support batching
    - Process PDF page by page
    - Group pages into batches based on batch size
    - Return list of TextBatch objects instead of single string
    - _Requirements: 2.3_

  - [x] 5.4 Update `FileProcessor.extract_text_ai()` to support batching
    - Convert PDF pages to images in batches of 3
    - Return list of TextBatch objects
    - _Requirements: 2.4_

  - [ ] 5.5 Write property test for batch size correctness
    - **Property 4: Batch Size Correctness**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

- [x] 6. Implement batch content generation
  - [x] 6.1 Add `BatchContent` model to models.py
    - Add batch_id, questions, mnemonics, cheat_sheet_points, key_concepts fields
    - _Requirements: 3.1_

  - [x] 6.2 Implement `AIService.generate_content_from_batch()`
    - Generate questions from batch text
    - Generate mnemonics from batch text
    - Generate cheat sheet points from batch text
    - Return BatchContent object with all three types
    - _Requirements: 3.1_

  - [ ] 6.3 Write property test for parallel content generation
    - **Property 7: Parallel Content Generation**
    - **Validates: Requirements 3.1**

- [x] 7. Implement content aggregation
  - [x] 7.1 Create `ContentAggregator` class in new file `backend/app/services/content_aggregator.py`
    - _Requirements: 3.2, 3.3, 3.4_

  - [x] 7.2 Implement `ContentAggregator.aggregate_questions()`
    - Combine questions from all BatchContent objects
    - Remove duplicates if any
    - Return list of Question objects
    - _Requirements: 3.2_

  - [x] 7.3 Implement `ContentAggregator.aggregate_mnemonics()`
    - Combine mnemonics from all BatchContent objects
    - Return list of Mnemonic objects
    - _Requirements: 3.3_

  - [x] 7.4 Implement `ContentAggregator.aggregate_cheat_sheets()`
    - Combine cheat sheet points from all BatchContent objects
    - Organize into comprehensive cheat sheets
    - Return list of CheatSheet objects
    - _Requirements: 3.4_

  - [ ] 7.5 Write property test for single question bank per session
    - **Property 5: Single Question Bank Per Session**
    - **Validates: Requirements 2.5, 3.2**

  - [ ] 7.6 Write property test for content aggregation completeness
    - **Property 8: Content Aggregation Completeness**
    - **Validates: Requirements 3.2, 3.3, 3.4**

- [ ] 8. Checkpoint - Verify batching and aggregation works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement mock test generation without AI calls
  - [x] 9.1 Create `MockTestGenerator` class in new file `backend/app/services/mock_test_generator.py`
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 9.2 Implement `MockTestGenerator.create_mock_test_from_questions()`
    - Take list of Question objects
    - Create MockTest with all question IDs
    - Calculate duration as question_count * 1.5
    - Generate descriptive test name
    - Do NOT call AI service
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ] 9.3 Write property test for mock test without AI calls
    - **Property 9: Mock Test Without AI Calls**
    - **Validates: Requirements 3.5, 4.1, 4.2, 4.3**

  - [ ] 9.4 Write property test for mock test duration calculation
    - **Property 10: Mock Test Duration Calculation**
    - **Validates: Requirements 4.4**

- [x] 10. Implement notes compilation
  - [x] 10.1 Implement `ContentAggregator.compile_notes()`
    - Take questions, mnemonics, cheat sheets as input
    - Select important questions for notes
    - Include cheat sheet key points
    - Reference relevant mnemonics
    - Generate high-level summary
    - Return Note object
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ] 10.2 Write property test for notes compilation completeness
    - **Property 11: Notes Compilation Completeness**
    - **Validates: Requirements 3.6, 5.1, 5.2, 5.3, 5.4**

- [ ] 11. Implement text-only input support
  - [ ] 11.1 Add `InputType` enum to models.py
    - Add FILE_UPLOAD and TEXT_INPUT values
    - _Requirements: 6.1_

  - [ ] 11.2 Update `StudySession` model
    - Add text_input: Optional[str] field
    - Add input_type: InputType field
    - Add document_type: Optional[DocumentType] field
    - _Requirements: 6.1, 6.5_

  - [ ] 11.3 Update upload endpoint to accept text input
    - Add optional text_input parameter
    - Set input_type based on whether files or text provided
    - _Requirements: 6.1_

  - [ ] 11.4 Implement `AIService.generate_from_text_input()`
    - Generate all five content types from topic text
    - Return dict with questions, mnemonics, cheat_sheets, notes
    - _Requirements: 6.2, 6.3_

  - [ ] 11.5 Implement `ProcessingService.process_text_input()`
    - Call `generate_from_text_input()`
    - Store all content in database
    - Update session status
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ] 11.6 Write property test for text input mode selection
    - **Property 12: Text Input Mode Selection**
    - **Validates: Requirements 6.1, 6.4, 6.5**

  - [ ] 11.7 Write property test for text input content generation
    - **Property 13: Text Input Content Generation**
    - **Validates: Requirements 6.2, 6.3**

- [ ] 12. Checkpoint - Verify text input works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Implement enhanced processing workflow
  - [ ] 13.1 Update `ProcessingService.start_processing()` to use batching
    - Call `FileProcessor.create_batches()`
    - Process each batch with `generate_content_from_batch()`
    - Aggregate results with `ContentAggregator`
    - Create mock test with `MockTestGenerator`
    - Compile notes
    - Store all content
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ] 13.2 Add progress tracking for batches
    - Update progress after each batch processed
    - Track pages_processed and total_pages
    - Update step_message for current batch
    - _Requirements: 2.6_

  - [ ] 13.3 Write property test for progress monotonicity
    - **Property 6: Progress Monotonicity**
    - **Validates: Requirements 2.6, 10.2, 10.4**

- [ ] 14. Implement error handling
  - [ ] 14.1 Create `ErrorHandler` class in new file `backend/app/utils/error_handler.py`
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

  - [ ] 14.2 Implement `ErrorHandler.handle_ai_error()`
    - Detect error type (rate limit, auth, content blocked, etc.)
    - Return appropriate user message
    - Log technical details
    - _Requirements: 8.1, 8.2, 8.3_

  - [ ] 14.3 Implement OCR fallback logic
    - Wrap OCR calls in try-except
    - On OCR failure, switch to AI_ONLY mode
    - Log fallback action
    - Continue processing
    - _Requirements: 8.4_

  - [ ] 14.4 Implement partial result preservation
    - On processing failure, commit any completed batches to database
    - Update session with error details
    - Set status to FAILED
    - _Requirements: 8.5, 8.6_

  - [ ] 14.5 Write property test for OCR fallback
    - **Property 14: OCR Fallback on Failure**
    - **Validates: Requirements 8.4**

  - [ ] 14.6 Write property test for error state consistency
    - **Property 15: Error State Consistency**
    - **Validates: Requirements 8.1, 8.5, 8.6**

  - [ ] 14.7 Write unit tests for specific error cases
    - Test rate limit error response
    - Test authentication error response
    - _Requirements: 8.2, 8.3_

- [ ] 15. Implement session history retrieval
  - [ ] 15.1 Create session history endpoint
    - GET /api/v1/sessions/{user_id}
    - Return all sessions for user sorted by created_at
    - _Requirements: 9.1_

  - [ ] 15.2 Create session detail endpoint
    - GET /api/v1/sessions/detail/{session_id}
    - Return session with all five output types
    - _Requirements: 9.2, 9.3, 9.4_

  - [ ] 15.3 Write property test for session history completeness
    - **Property 16: Session History Completeness**
    - **Validates: Requirements 9.1**

  - [ ] 15.4 Write property test for session data completeness
    - **Property 17: Session Data Completeness**
    - **Validates: Requirements 9.2, 9.3, 9.4**

- [ ] 16. Implement progress tracking enhancements
  - [ ] 16.1 Update `ProgressTracker` to track batch progress
    - Add batch_number and total_batches to progress updates
    - Calculate overall_progress based on batches completed
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

  - [ ] 16.2 Add completion state handling
    - Set overall_progress to 100 on completion
    - Set completed_at timestamp
    - Set final step_message
    - _Requirements: 10.5_

  - [ ] 16.3 Write property test for progress completion state
    - **Property 18: Progress Completion State**
    - **Validates: Requirements 10.5**

- [ ] 17. Integration and testing
  - [ ] 17.1 Write integration test for small PDF processing (≤5 pages)
    - Upload 3-page PDF
    - Verify single batch created
    - Verify all five outputs generated
    - _Requirements: 2.1_

  - [ ] 17.2 Write integration test for large PDF processing (>5 pages)
    - Upload 10-page PDF
    - Verify multiple batches created (2-3 pages each)
    - Verify all outputs aggregated correctly
    - _Requirements: 2.2, 2.3, 2.5_

  - [ ] 17.3 Write integration test for text-only input
    - Submit topic text without files
    - Verify AI_ONLY mode used
    - Verify all five outputs generated
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ] 17.4 Write integration test for document with existing questions
    - Upload PDF containing practice questions
    - Verify questions extracted (not generated)
    - Verify mock test created from extracted questions
    - _Requirements: 1.1, 1.4_

  - [ ] 17.5 Write integration test for OCR fallback
    - Mock OCR failure
    - Verify fallback to AI_ONLY
    - Verify processing completes successfully
    - _Requirements: 8.4_

  - [ ] 17.6 Write integration test for partial failure recovery
    - Mock failure after 2 of 5 batches
    - Verify first 2 batches stored in database
    - Verify session marked as FAILED
    - _Requirements: 8.6_

- [ ] 18. Final checkpoint - End-to-end verification
  - Run all tests (unit, property, integration)
  - Verify all requirements covered
  - Test with real medical PDFs
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Integration tests validate end-to-end workflows
- All code should handle medical content without safety filter blocking
