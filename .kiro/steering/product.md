# Study Buddy App - Product Requirements Document

## Project Overview

**Product Name**: Study Buddy App
**Purpose**: AI-powered study companion for medical students integrated with MedGloss platform
**Target Users**: MBBS students preparing for medical examinations
**Architecture**: Microservices (separate frontend/backend, later merged into existing MedGloss app)

## Problem Statement

Medical students need efficient tools to:
- Convert study materials (PDFs, images, slides, videos) into actionable study resources
- Generate practice questions from their own materials
- Create mnemonics for better retention
- Compile high-yield notes and cheat sheets
- Take mock tests based on their uploaded content

## Solution

Study Buddy App provides an AI-powered platform that:
1. Accepts multiple input formats (PDFs, images, slides, video links)
2. Processes content using OCR and AI
3. Generates study materials: question banks, mock tests, mnemonics, cheat sheets, and notes
4. Organizes outputs by session for easy retrieval
5. Provides download options for offline study

## Key Features

### 1. Multi-Format Upload
- PDF documents
- Images (scanned notes, slides)
- Presentation slides
- Video links (YouTube, educational platforms)

### 2. Processing Modes
- **Default Mode**: Direct text extraction
- **OCR Mode**: Enhanced extraction for scanned documents
- **AI-based Mode**: Context-aware intelligent processing

### 3. Output Generation
- **Question Bank**: Auto-generated MCQs with difficulty classification
- **Mock Tests**: Timed tests with auto-generated names
- **Mnemonics**: India-specific memory aids
- **Cheat Sheets**: Key topics and high-yield points
- **Notes**: Compiled study materials

### 4. Session Management
- Auto-generated session names
- Date-based organization
- History preservation
- User-specific data isolation

### 5. Download & Export
- PDF format (notes, cheat sheets, question banks)
- Image format (cheat sheets, mnemonics)
- JSON export for data portability

## User Flow

### Entry Flow
1. User clicks "Study Buddy" card on MedGloss dashboard
2. System checks authentication status
3. If authenticated → proceed to Study Buddy dashboard
4. If not → redirect to login/register

### Main Workflow
1. **Upload**: User uploads files or provides video links
2. **Configure**: Select processing mode (Default/OCR/AI-based)
3. **Process**: Click "Search/Process" button
4. **Monitor**: View processing status and progress
5. **Review**: Access generated outputs (questions, tests, mnemonics, etc.)
6. **Download**: Export materials in preferred format
7. **Repeat**: Create new sessions for additional materials

## Success Metrics

### User Engagement
- Number of sessions created per user
- Files uploaded per session
- Time spent on platform
- Return user rate

### Content Quality
- Question generation accuracy
- Mnemonic relevance score
- User satisfaction ratings
- Download frequency

### Performance
- Processing time per file
- System uptime
- API response times
- Error rates

## Integration Requirements

### MedGloss Authentication
- Reuse existing user model
- Same JWT token logic
- Same OTP verification flow
- No new authentication implementation

### Existing Services
- OCR scripts from `/home/unknown/Documents/medgloss-data-extractorfiles`
- GenAI credentials from existing configs
- MongoDB database (local instance)

## Future Enhancements

### Phase 2 Features
- Collaborative study sessions
- Share sessions between users
- Learning progress analytics
- Spaced repetition system

### Phase 3 Features
- Mobile app (React Native)
- Offline mode
- Advanced AI models
- Multi-language support

## Constraints & Assumptions

### Technical Constraints
- Local MongoDB only (no cloud database initially)
- Existing GenAI API rate limits
- File size limit: 50MB per file
- Supported file types: PDF, JPG, PNG, PPTX

### Business Constraints
- Must integrate with existing MedGloss system
- No separate authentication system
- Microservices architecture for future scalability
- Development timeline: Hackathon duration (Jan 5-23, 2026)

### Assumptions
- Users have stable internet connection
- Users are familiar with MedGloss platform
- Content is primarily in English
- Medical content follows MBBS curriculum

## Competitive Advantage

1. **Integration**: Seamless integration with existing MedGloss platform
2. **AI-Powered**: Advanced GenAI for content generation
3. **Multi-Format**: Supports various input formats
4. **India-Specific**: Mnemonics and content tailored for Indian medical students
5. **Session-Based**: Organized workflow with session management
6. **Offline Support**: Downloadable materials for offline study

## Risk Assessment

### Technical Risks
- AI generation quality variability
- OCR accuracy for poor quality scans
- Processing time for large files
- Database performance with large datasets

### Mitigation Strategies
- Implement quality checks for AI outputs
- Provide multiple processing modes
- Async processing for large files
- Database indexing and optimization

## Success Criteria

### MVP (Minimum Viable Product)
- ✅ File upload functionality
- ✅ Basic text extraction
- ✅ Question generation
- ✅ Session management
- ✅ Download functionality

### Full Release
- ✅ All processing modes working
- ✅ All output types generated
- ✅ Authentication integration complete
- ✅ Performance optimized
- ✅ Documentation complete

## Timeline

**Hackathon Duration**: January 5-23, 2026

### Week 1 (Jan 5-11)
- Core infrastructure setup
- Authentication integration
- Basic upload functionality

### Week 2 (Jan 12-18)
- Processing pipeline implementation
- AI service integration
- Output generation

### Week 3 (Jan 19-23)
- UI/UX completion
- Testing and optimization
- Documentation and submission

## Stakeholders

- **Primary Users**: MBBS students
- **Development Team**: Hackathon participants
- **Integration Partner**: MedGloss platform
- **Judges**: Dynamous Kiro Hackathon evaluators
