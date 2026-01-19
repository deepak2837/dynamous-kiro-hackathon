# Study Buddy App - Quick Start Guide

## Project Overview
**Study Buddy App** - AI-powered study companion for medical students built for the Dynamous Kiro Hackathon 2026.

### Current Status (2026-01-19)
✅ **COMPLETE IMPLEMENTATION** - Both backend and frontend fully implemented
- **Backend**: FastAPI + MongoDB + AI service integration
- **Frontend**: Next.js 14 + TypeScript + comprehensive UI
- **Features**: Upload, processing, AI generation, results viewer
- **Development Time**: 1.5 hours total

### What's Built
- Multi-format file upload (PDF, images, PPTX, video links)
- Three processing modes (Default, OCR, AI-based)
- AI content generation (Questions, Tests, Mnemonics, Sheets, Notes)
- Real-time processing status with polling
- Comprehensive results viewer with tabbed interface
- Session management and history
- Responsive design with modern UI/UX

## Quick Commands

### Get Project Context
```bash
@prime  # Load complete Study Buddy App context
```

### Development Setup
```bash
# Automated setup (recommended)
./scripts/setup.sh

# Manual setup
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd ../frontend && npm install

# Start services
./scripts/start.sh  # or manually start backend + frontend
```

### Key Directories
```
dynamous-kiro-hackathon/
├── backend/app/          # FastAPI application
│   ├── main.py          # Entry point
│   ├── models/          # Database models (6 collections)
│   ├── api/             # API endpoints
│   └── services/        # Business logic (AI, file processing)
├── frontend/src/        # Next.js application
│   ├── app/             # App router pages
│   ├── components/      # React components
│   └── lib/             # API client and utilities
├── .kiro/steering/      # Project specifications
└── scripts/             # Setup and deployment scripts
```

## Next Steps (Integration Phase)

### 1. Environment Setup
```bash
# Configure backend environment
cp backend/.env.example backend/.env
# Edit with your API keys:
# - GOOGLE_AI_API_KEY
# - MONGODB_URL
# - JWT_SECRET

# Configure frontend environment  
cp frontend/.env.example frontend/.env.local
# Edit with API URL
```

### 2. Database Setup
```bash
# Start MongoDB locally
mongod --dbpath /path/to/data

# Start Redis
redis-server

# Start Celery worker
cd backend && celery -A app.tasks worker --loglevel=info
```

### 3. Testing & Integration
```bash
# Test backend
cd backend && python -m pytest
uvicorn app.main:app --reload

# Test frontend
cd frontend && npm run build
npm run dev

# Integration test
curl -X POST http://localhost:8000/api/v1/upload
```

### 4. MedGloss Integration (Planned)
- Integrate existing JWT authentication
- Connect OCR scripts from `/home/unknown/Documents/medgloss-data-extractorfiles`
- Share MongoDB database
- Implement user profile integration

## Medical Education Features

### Content Generation
- **Questions**: MBBS-oriented MCQs with difficulty classification
- **Mock Tests**: Timed tests with medical exam formats
- **Mnemonics**: India-specific medical memory aids
- **Cheat Sheets**: High-yield medical topics
- **Notes**: Compiled medical study materials

### Processing Modes
- **Default**: Fast text extraction for clean documents
- **OCR**: Enhanced extraction for scanned medical notes
- **AI-based**: Context-aware processing for complex medical content

### Medical Focus
- MBBS curriculum alignment
- India-specific medical terminology
- Medical exam preparation (NEET, AIIMS, etc.)
- High-quality medical content generation

## Architecture Overview

### Backend (FastAPI)
```python
# Key components
app/main.py              # FastAPI application
app/models/session.py    # Session management
app/services/ai_processor.py  # AI content generation
app/api/upload.py        # File upload endpoints
```

### Frontend (Next.js)
```typescript
// Key components
src/app/study-buddy/page.tsx        # Entry page
src/components/UploadSection.tsx    # File upload UI
src/components/ResultsViewer.tsx    # Results display
src/lib/api.ts                      # API client
```

### Database Schema
- `study_sessions` - Session management
- `questions` - Generated MCQs
- `mock_tests` - Timed tests
- `mnemonics` - Memory aids
- `cheat_sheets` - Study summaries
- `notes` - Compiled materials

## Development Workflow

### Feature Development
```bash
@plan-feature "new medical feature"  # Plan implementation
@execute path/to/plan.md            # Execute plan
```

### Code Review
```bash
@code-review                        # Review changes
@code-review-hackathon             # Hackathon-specific review
```

### System Review
```bash
@system-review                      # Full system analysis
```

## Hackathon Context

### Competition Details
- **Event**: Dynamous Kiro Hackathon 2026
- **Dates**: January 5-23, 2026
- **Prize Pool**: $17,000 across 10 winners
- **Theme**: Build anything that solves a real problem
- **Repository**: https://github.com/deepak2837/dynamous-kiro-hackathon

### Submission Requirements
- Complete implementation ✅
- Documentation ✅
- Demo video (pending)
- Integration testing (in progress)

## Troubleshooting

### Common Issues
```bash
# Backend won't start
mongod --version  # Check MongoDB
redis-cli ping    # Check Redis
python --version  # Check Python 3.10+

# Frontend build errors
node --version    # Check Node 18+
rm -rf node_modules && npm install

# File upload fails
# Check file size (max 50MB) and type (PDF, JPG, PNG, PPTX)
```

### Getting Help
```bash
@prime              # Load project context
@system-review      # Analyze current state
@rca "issue"        # Root cause analysis
```

## Key Files to Know

### Configuration
- `backend/.env` - Backend environment variables
- `frontend/.env.local` - Frontend environment variables
- `.kiro/steering/` - Project specifications

### Documentation
- `README.md` - Project overview
- `DEVLOG.md` - Development history
- `docs/` - Technical documentation

### Scripts
- `scripts/setup.sh` - Automated setup
- `scripts/start.sh` - Start all services
- `scripts/stop.sh` - Stop all services

## Ready to Code!

The Study Buddy App is fully implemented and ready for integration testing and deployment. Use the prompts above to navigate the codebase and continue development.

**Focus Areas:**
- Integration with MedGloss authentication
- OCR scripts integration
- Performance optimization
- Medical content quality validation
- Deployment preparation
