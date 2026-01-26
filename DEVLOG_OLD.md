# Development Log - Study Buddy App

> Kiro Hackathon Development Timeline (January 5-30, 2026)

## Project Overview

**Goal**: Build an AI-powered study companion for medical students using Kiro CLI

**Key Features**: File upload processing, topic-based generation, mock tests, mnemonics, session history

---

## Week 1: Foundation (Jan 5-11)

### Day 1-2: Project Setup
- ✅ Initialized project structure with Next.js frontend and FastAPI backend
- ✅ Set up `.kiro` configuration with steering documents
- ✅ Created product.md, tech.md, structure.md specifications
- **Time spent**: ~4 hours

### Day 3-4: Authentication System
- ✅ Implemented mobile number + OTP authentication
- ✅ Added JWT token-based session management
- ✅ Created auth_simple.py with MongoDB user storage
- **Challenge**: Handling multiple user ID formats (ObjectId vs mobile number)
- **Solution**: Normalized phone numbers and query by multiple identifiers
- **Time spent**: ~6 hours

### Day 5-7: Core Upload Infrastructure
- ✅ Built file upload endpoint with size validation
- ✅ Implemented multi-file processing
- ✅ Added processing status tracking
- **Time spent**: ~5 hours

---

## Week 2: AI Integration (Jan 12-18)

### Day 8-10: AI Service Implementation
- ✅ Integrated Google Gemini API for content generation
- ✅ Created prompts for questions, mnemonics, cheat sheets, notes
- ✅ Built file analysis with direct file upload to Gemini
- **Challenge**: JSON parsing from AI responses
- **Solution**: Multiple fallback extraction methods
- **Time spent**: ~8 hours

### Day 11-12: Processing Pipeline
- ✅ Implemented ProcessingService for coordinating generation
- ✅ Added mock test generation from questions
- ✅ Created session storage in MongoDB
- **Time spent**: ~5 hours

### Day 13-14: Text Input Feature
- ✅ Added topic-based generation (no file needed)
- ✅ Same 5 outputs generated from topic name
- **Time spent**: ~3 hours

---

## Week 3: Polish & Submission (Jan 19-30)

### Day 15-17: Frontend Completion
- ✅ Built FileUpload component with drag-and-drop
- ✅ Created ResultsViewer with tabbed interface
- ✅ Added MockTestInterface with timer and scoring
- ✅ Implemented SessionHistory component
- **Time spent**: ~8 hours

### Day 18-19: Session History Feature
- ✅ Fixed user-based session retrieval
- ✅ Added content counts to session cards
- ✅ Enabled session restoration
- **Challenge**: Matching sessions to users with different ID formats
- **Solution**: Query with array of possible user identifiers
- **Time spent**: ~4 hours

### Day 20-21: Bug Fixes & Testing
- ✅ Fixed file upload user_id association
- ✅ Resolved processing status polling issues
- ✅ Tested all 5 output generation types
- **Time spent**: ~4 hours

### Day 22: Codebase Cleanup
- ✅ Removed unused test files and documentation
- ✅ Cleaned up empty directories
- ✅ Removed unused Redis configuration
- ✅ Verified backend and frontend still work
- **Time spent**: ~1 hour

### Day 23-25: Documentation & Submission
- ✅ Created README.md with setup instructions
- ✅ Updated DEVLOG.md with timeline
- ⏳ Recording demo video
- ⏳ Final submission

---

## Technical Decisions

| Decision | Rationale |
|----------|-----------|
| FastAPI over Flask | Better async support, auto OpenAPI docs |
| MongoDB over SQL | Flexible schema for varied content types |
| Next.js App Router | Modern React patterns, server components |
| Gemini over OpenAI | Cost-effective, good medical content generation |
| Mobile OTP Auth | Tailored for Indian medical student market |

---

## Challenges & Solutions

### 1. AI Response Parsing
**Problem**: Gemini sometimes returns malformed JSON  
**Solution**: Implemented `extract_json_from_response()` with regex fallbacks

### 2. User Session Identification
**Problem**: User IDs stored as ObjectId vs mobile number  
**Solution**: Query with `$in` operator checking multiple formats

### 3. Large File Processing
**Problem**: Timeout on large PDFs  
**Solution**: Direct file upload to Gemini API instead of text extraction

### 4. Mock Test Timing
**Problem**: Frontend timer state management  
**Solution**: useRef for timer ID, proper cleanup on unmount

---

## Total Time Investment

| Phase | Hours |
|-------|-------|
| Setup & Config | 4 |
| Authentication | 6 |
| Upload System | 5 |
| AI Integration | 8 |
| Processing Pipeline | 5 |
| Text Input | 3 |
| Frontend | 8 |
| Session History | 4 |
| Bug Fixes | 4 |
| Cleanup & Docs | 3 |
| **Total** | **~50 hours** |

---

## Kiro CLI Usage

- Used Kiro for all major development tasks
- Custom prompts in `.kiro/prompts/` for code review, feature planning
- Steering documents guided architecture decisions
- Agentic mode for complex multi-file changes
