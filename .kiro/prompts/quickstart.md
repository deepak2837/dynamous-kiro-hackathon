# Quick Project Overview Prompt

You are providing a rapid overview of the Study Buddy App for new developers or stakeholders.

## 30-Second Summary
**Study Buddy** is an AI-powered study companion for MBBS students that transforms uploaded materials (PDFs, images, slides) into comprehensive study resources including question banks, mock tests, mnemonics, cheat sheets, and notes.

## Key Stats
- **Tech Stack**: Next.js + FastAPI + MongoDB + Google Gemini AI
- **Features**: 6 output types, 3 processing modes, session management
- **Integration**: MedGloss platform authentication
- **Target**: Indian medical students (MBBS curriculum)

## Live Demo
- **URL**: https://study-material-generator.netlify.app/
- **Test Login**: Mobile: 7045024042, Password: test_password

## Architecture
```
Frontend (Next.js) → API (FastAPI) → AI (Gemini) → Database (MongoDB)
                  ↓
            File Processing (OCR + Text Extraction)
```

## Current Status
- ✅ Core functionality complete
- ✅ AI generation working
- ✅ Authentication integrated
- ✅ Comprehensive documentation
- 🚀 Live and demo-ready

## Quick Start
1. `cd frontend && npm run dev` (port 3000)
2. `cd backend && uvicorn app.main:app --reload` (port 8000)
3. Upload files → Get AI-generated study materials

Perfect for hackathon demos and technical discussions!
