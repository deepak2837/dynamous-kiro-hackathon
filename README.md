# Study Buddy App - AI-Powered Study Companion for Medical Students

🎓 **Transform your study materials into comprehensive learning resources** - An AI-powered application that converts PDFs, images, slides, and videos into question banks, mock tests, mnemonics, cheat sheets, and notes.

> **🏆 Built for**: Dynamous Kiro Hackathon 2026 | **💰 Prize Pool**: $17,000

## Project Overview

Study Buddy App is an intelligent study companion designed specifically for medical students (MBBS-oriented). It leverages AI to automatically generate high-quality study materials from uploaded content, helping students prepare more efficiently for their examinations.

### Key Features

- 📤 **Multi-Format Upload**: PDFs, images, slides, and video links
- 🤖 **AI-Powered Processing**: Three processing modes (Default, OCR, AI-based)
- 📝 **Question Bank Generation**: Auto-generated MCQs with difficulty classification
- 📊 **Mock Tests**: Timed tests with auto-generated names
- 🧠 **Mnemonics**: India-specific memory aids for better retention
- 📋 **Cheat Sheets**: Key topics and high-yield points
- 📖 **Compiled Notes**: Important questions, summaries, and mnemonics
- 💾 **Download Options**: PDF and image formats for offline study
- 🔐 **Secure**: Integrated with MedGloss authentication system

## About the Hackathon

The **Kiro Hackathon** is a coding competition where developers build real-world applications using the Kiro CLI. This project demonstrates AI-powered development and solves a real problem for medical students.

- **📅 Dates**: January 5-23, 2026
- **💰 Prize Pool**: $17,000 across 10 winners
- **🎯 Theme**: Open - build anything that solves a real problem
- **🔗 More Info**: [dynamous.ai/kiro-hackathon](https://dynamous.ai/kiro-hackathon)

## Tech Stack

### Frontend
- **Framework**: Next.js 14+ with React 18+
- **Styling**: TailwindCSS
- **State Management**: React Context API
- **HTTP Client**: Axios
- **File Upload**: React Dropzone

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: MongoDB (local instance)
- **AI/ML**: Google GenAI API
- **Authentication**: JWT (MedGloss integration)
- **Task Queue**: Celery + Redis
- **File Processing**: PyPDF2, Pillow, OpenCV
- **OCR**: Existing MedGloss OCR scripts

### Infrastructure
- MongoDB 6.0+
- Redis 7.0+
- Local file storage

## Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Frontend  │────────▶│   Backend   │────────▶│   MongoDB   │
│  (Next.js)  │         │  (FastAPI)  │         │             │
└─────────────┘         └─────────────┘         └─────────────┘
                               │
                               ▼
                        ┌─────────────┐
                        │   GenAI     │
                        │     API     │
                        └─────────────┘
```

**Microservices Architecture**: Separate frontend and backend services designed for future integration into the existing MedGloss platform.

## How It Works

### 1. Upload
Users upload study materials:
- PDF documents
- Images (scanned notes, slides)
- Presentation files
- Video links (YouTube, educational platforms)

### 2. Process
Choose from three processing modes:
- **Default Mode**: Fast direct text extraction
- **OCR Mode**: Enhanced extraction for scanned documents
- **AI-based Mode**: Context-aware intelligent processing

### 3. Generate
AI automatically creates:
- **Question Banks**: MCQs with difficulty levels and explanations
- **Mock Tests**: Timed tests with scoring
- **Mnemonics**: India-specific memory aids
- **Cheat Sheets**: Key topics and high-yield points
- **Notes**: Compiled study materials

### 4. Study & Download
- View all generated materials in organized sessions
- Download in PDF or image format
- Access history of all past sessions

## Prerequisites

Before you begin, ensure you have:

- **Node.js** 18+ and npm
- **Python** 3.10+
- **MongoDB** 6.0+ (running locally)
- **Redis** 7.0+ (running locally)
- **Google GenAI API** credentials
- **Git** for version control

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/deepak2837/dynamous-kiro-hackathon.git
cd dynamous-kiro-hackathon
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials

# Start the backend server
uvicorn app.main:app --reload
```

Backend will run on `http://localhost:8000`

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env.local
# Edit .env.local with your API URL

# Start the development server
npm run dev
```

Frontend will run on `http://localhost:3000`

### 4. Start Supporting Services

```bash
# Start MongoDB (if not running)
mongod --dbpath /path/to/data

# Start Redis (if not running)
redis-server

# Start Celery worker (in backend directory)
celery -A app.tasks worker --loglevel=info
```

## Environment Configuration

### Backend (.env)
```env
# Database
MONGODB_URL=mongodb://localhost:27017/medgloss
DATABASE_NAME=medgloss

# AI Service
GOOGLE_AI_API_KEY=your_api_key_here
GENAI_PROJECT_ID=your_project_id

# Authentication (use existing MedGloss credentials)
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_EXPIRY=86400

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=52428800  # 50MB

# OCR Scripts Path
OCR_SCRIPTS_PATH=/path/to/medgloss-data-extractorfiles

# Redis
REDIS_URL=redis://localhost:6379
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=StudyBuddy
NEXTAUTH_SECRET=your_nextauth_secret
```

## Project Structure

```
dynamous-kiro-hackathon/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # App router pages
│   │   ├── components/      # React components
│   │   ├── lib/             # Utilities
│   │   └── types/           # TypeScript types
│   └── package.json
│
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/             # API routes
│   │   ├── models/          # Database models
│   │   ├── services/        # Business logic
│   │   └── utils/           # Utilities
│   └── requirements.txt
│
├── docs/                     # Documentation
├── .kiro/                    # Kiro CLI configuration
│   └── steering/            # Project specifications
├── README.md
└── DEVLOG.md                # Development log
```

## API Documentation

### Main Endpoints

#### Upload Files
```
POST /api/v1/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

#### Get Processing Status
```
GET /api/v1/process/{session_id}
Authorization: Bearer <token>
```

#### Get Results
```
GET /api/v1/questions/{session_id}
GET /api/v1/mock-tests/{session_id}
GET /api/v1/mnemonics/{session_id}
GET /api/v1/cheat-sheets/{session_id}
GET /api/v1/notes/{session_id}
```

Full API documentation available at `http://localhost:8000/docs` when backend is running.

## Usage Example

1. **Login**: Authenticate using existing MedGloss credentials
2. **Navigate**: Click on "Study Buddy" card
3. **Upload**: Drag and drop your study materials
4. **Select Mode**: Choose processing mode (Default/OCR/AI-based)
5. **Process**: Click "Search/Process" button
6. **Wait**: Monitor processing progress
7. **Review**: Access generated questions, tests, mnemonics, etc.
8. **Download**: Export materials for offline study

## Development Workflow

### Using Kiro CLI

This project is optimized for development with Kiro CLI:

```bash
# Load project context
@prime

# Plan new features
@plan-feature

# Execute implementation
@execute

# Review code quality
@code-review
```

### Testing

```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
pytest

# Integration tests
pytest tests/integration
```

## Integration with MedGloss

Study Buddy App is designed to integrate seamlessly with the existing MedGloss platform:

- **Authentication**: Reuses MedGloss JWT + OTP system
- **Database**: Shares MongoDB instance
- **User Model**: References existing user collection
- **OCR**: Integrates existing OCR scripts

## Features in Detail

### Question Bank Generation
- Auto-generated MCQs from uploaded content
- Difficulty classification (Easy/Medium/Hard)
- Medical subject categorization
- Detailed explanations for each question
- Compatible with existing MedGloss question format

### Mock Tests
- Auto-generated test names ("Curated Mock Test", "Master Blaster Test")
- Timed tests with configurable duration
- Scoring and performance analytics
- Follows existing MedGloss mock test UI

### Mnemonics
- Content-specific mnemonics
- India-specific for better cultural relevance
- Text-based (primary) and image-generated (optional)
- Key term highlighting

### Cheat Sheets
- Key topics extraction
- High-yield points for exam preparation
- Concise explanations
- Download as PDF or image

### Notes Compilation
- Important questions
- Cheat sheet summaries
- Relevant mnemonics
- Organized by topics and difficulty

## Performance Optimization

- **Async Processing**: Large files processed in background
- **Caching**: AI responses cached for similar content
- **Database Indexing**: Optimized queries on user_id and session_id
- **File Cleanup**: Automatic removal of old files (30 days)

## Security

- JWT authentication on all endpoints
- File type and size validation
- User-specific data isolation
- Rate limiting (100 requests/minute per user)
- Secure file storage outside web root

## Troubleshooting

### Backend won't start
- Ensure MongoDB is running: `mongod --version`
- Check Redis is running: `redis-cli ping`
- Verify Python version: `python --version` (should be 3.10+)

### Frontend build errors
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (should be 18+)

### File upload fails
- Check file size (max 50MB)
- Verify file type (PDF, JPG, PNG, PPTX only)
- Ensure uploads directory exists and is writable

### AI generation issues
- Verify GenAI API credentials in .env
- Check API quota and rate limits
- Review logs for specific error messages

## Contributing

This is a hackathon project, but contributions and suggestions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Roadmap

### Current Phase (Hackathon)
- [x] Project setup and specifications
- [ ] Core infrastructure implementation
- [ ] Processing pipeline development
- [ ] Frontend UI development
- [ ] Integration and testing
- [ ] Documentation completion

### Future Enhancements
- Collaborative study sessions
- Learning progress analytics
- Mobile app (React Native)
- Offline mode
- Multi-language support
- Advanced AI models

## License

MIT License - see LICENSE file for details

## Acknowledgments

- **Dynamous & Kiro**: For organizing the hackathon
- **MedGloss**: For existing authentication and OCR infrastructure
- **Google GenAI**: For AI capabilities
- **Open Source Community**: For amazing tools and libraries

## Contact

- **Developer**: Deepak
- **Email**: peenu000@gmail.com
- **Repository**: https://github.com/deepak2837/dynamous-kiro-hackathon

---

**Built with ❤️ for medical students preparing for their dreams**
