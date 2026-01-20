# Requirements Document: Content Generation Enhancement

## Introduction

The Study Buddy App is an AI-powered medical study companion that processes uploaded documents (PDFs, images, presentations) and generates five types of study materials: question banks, mock tests, mnemonics, cheat sheets, and notes. This specification enhances the existing system to handle intelligent question extraction, batched processing for large documents, text-only input, and robust error handling.

## Glossary

- **System**: The Study Buddy backend processing pipeline
- **AI_Service**: Google Gemini AI service for content generation
- **OCR_Service**: Optical Character Recognition service for text extraction
- **File_Processor**: Service that extracts text from uploaded files
- **Processing_Service**: Orchestrates the entire content generation workflow
- **Session**: A user's upload and processing instance with unique session_id
- **Question_Bank**: Collection of all generated MCQ questions for a session
- **Mock_Test**: Interactive test interface using questions from Question_Bank
- **Batch**: Group of 2-3 pages processed together for API efficiency
- **Safety_Settings**: Gemini API configuration to allow medical content without blocking

## Requirements

### Requirement 1: Intelligent Question Extraction

**User Story:** As a medical student, I want the system to intelligently handle documents that already contain questions versus documents that need questions generated, so that I get relevant question banks regardless of source material type.

#### Acceptance Criteria

1. WHEN a document contains existing questions THEN THE System SHALL extract and preserve those questions in the Question_Bank
2. WHEN a document contains study notes without questions THEN THE System SHALL generate new questions based on the content
3. WHEN processing a document THEN THE AI_Service SHALL analyze content type and determine appropriate question handling strategy
4. WHEN extracting existing questions THEN THE System SHALL maintain original question format, options, and explanations
5. WHEN generating new questions THEN THE System SHALL create clinically relevant MCQs suitable for MBBS exams

### Requirement 2: Batched Processing for Large Documents

**User Story:** As a user uploading large PDFs, I want the system to process my documents efficiently in batches, so that I can upload documents of any size without performance issues.

#### Acceptance Criteria

1. WHEN a PDF has 5 or fewer pages THEN THE System SHALL process all pages together in one batch
2. WHEN a PDF has more than 5 pages THEN THE System SHALL process pages in batches of 2-3 pages
3. WHEN processing in OCR_AI mode THEN THE System SHALL extract text from 2-3 pages, send to AI, then process next batch
4. WHEN processing in AI_ONLY mode THEN THE System SHALL send 3 pages at a time to AI for direct analysis
5. WHEN batching pages THEN THE System SHALL accumulate results and combine into single Question_Bank per session
6. WHEN batching pages THEN THE System SHALL track progress and update user on pages processed

### Requirement 3: Parallel Content Generation

**User Story:** As a user, I want all five output types generated efficiently from my uploaded content, so that I receive complete study materials quickly.

#### Acceptance Criteria

1. WHEN processing a batch of pages THEN THE System SHALL generate questions, mnemonics, and cheat sheets from the same batch
2. WHEN all batches are processed THEN THE System SHALL compile one comprehensive Question_Bank from all batch results
3. WHEN all batches are processed THEN THE System SHALL compile one comprehensive Cheat_Sheet from all batch results
4. WHEN all batches are processed THEN THE System SHALL compile one comprehensive Mnemonics collection from all batch results
5. WHEN Question_Bank is complete THEN THE System SHALL create one Mock_Test using all questions without additional AI calls
6. WHEN all content is generated THEN THE System SHALL compile Notes from important questions, cheat sheets, mnemonics, and PDF summary

### Requirement 4: Mock Test Generation from Question Bank

**User Story:** As a user, I want mock tests created directly from my question bank, so that I can practice with the same questions in an interactive format without redundant AI processing.

#### Acceptance Criteria

1. WHEN Question_Bank generation is complete THEN THE System SHALL create Mock_Test using existing questions
2. WHEN creating Mock_Test THEN THE System SHALL NOT make additional AI API calls
3. WHEN creating Mock_Test THEN THE System SHALL include all questions from Question_Bank
4. WHEN creating Mock_Test THEN THE System SHALL calculate duration as 1.5 minutes per question
5. WHEN creating Mock_Test THEN THE System SHALL generate descriptive test name based on session content

### Requirement 5: Notes Compilation

**User Story:** As a user, I want comprehensive notes that combine the most important elements from all generated content, so that I have a single consolidated study resource.

#### Acceptance Criteria

1. WHEN compiling Notes THEN THE System SHALL include important questions from Question_Bank
2. WHEN compiling Notes THEN THE System SHALL include key points from Cheat_Sheets
3. WHEN compiling Notes THEN THE System SHALL include relevant Mnemonics
4. WHEN compiling Notes THEN THE System SHALL include high-level summary of PDF content
5. WHEN compiling Notes THEN THE System SHALL organize content in logical study-friendly structure

### Requirement 6: Text-Only Input Support

**User Story:** As a user, I want to generate study materials by simply typing a topic name without uploading files, so that I can quickly get questions and materials on any medical subject.

#### Acceptance Criteria

1. WHEN a user submits text input without files THEN THE System SHALL process using AI_ONLY mode by default
2. WHEN processing text-only input THEN THE System SHALL generate Question_Bank based on the topic
3. WHEN processing text-only input THEN THE System SHALL generate all five output types (questions, mock test, mnemonics, cheat sheets, notes)
4. WHEN processing text-only input THEN THE System SHALL NOT require OCR processing
5. WHEN processing text-only input THEN THE System SHALL create session record without file references

### Requirement 7: Safety Settings for Medical Content

**User Story:** As a system administrator, I want Gemini API configured to allow all medical content without blocking, so that students can study sensitive medical topics without content restrictions.

#### Acceptance Criteria

1. WHEN configuring Gemini API THEN THE System SHALL set safety settings to BLOCK_NONE for all harm categories
2. WHEN processing medical content THEN THE AI_Service SHALL NOT block content due to safety filters
3. WHEN content contains medical terminology THEN THE System SHALL process it as adult educational content
4. WHEN safety settings are applied THEN THE System SHALL log configuration for audit purposes

### Requirement 8: Robust Error Handling

**User Story:** As a user, I want clear error messages when processing fails, so that I understand what went wrong and can take appropriate action.

#### Acceptance Criteria

1. WHEN AI API fails THEN THE System SHALL capture specific error message and return to user
2. WHEN AI API rate limit is exceeded THEN THE System SHALL return message indicating resource exhaustion
3. WHEN AI API key is invalid THEN THE System SHALL return authentication error message
4. WHEN OCR processing fails THEN THE System SHALL log error and attempt AI_ONLY fallback
5. WHEN any processing step fails THEN THE System SHALL update session status to FAILED with error details
6. WHEN processing fails THEN THE System SHALL preserve partial results if any were generated
7. WHEN error occurs THEN THE System SHALL provide actionable guidance to user

### Requirement 9: Session History and Retrieval

**User Story:** As a user, I want to view my previous sessions and access all generated materials, so that I can review my study materials anytime.

#### Acceptance Criteria

1. WHEN a user requests session history THEN THE System SHALL return all sessions for that user
2. WHEN viewing a session THEN THE System SHALL display all five output types generated
3. WHEN viewing a session THEN THE System SHALL show uploaded files or input text
4. WHEN viewing a session THEN THE System SHALL show processing status and timestamps
5. WHEN viewing a session THEN THE System SHALL allow downloading or viewing each output type

### Requirement 10: Progress Tracking

**User Story:** As a user uploading large documents, I want to see real-time progress updates, so that I know how long processing will take.

#### Acceptance Criteria

1. WHEN processing starts THEN THE System SHALL initialize progress tracking at 0%
2. WHEN processing each batch THEN THE System SHALL update progress percentage
3. WHEN processing each content type THEN THE System SHALL update current step message
4. WHEN processing THEN THE System SHALL display pages processed out of total pages
5. WHEN processing completes THEN THE System SHALL update progress to 100% with completion message
