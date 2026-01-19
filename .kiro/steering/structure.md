# Study Buddy App - Project Structure

## Directory Organization

```
dynamous-kiro-hackathon/
│
├── frontend/                           # Next.js Frontend Application
│   ├── src/
│   │   ├── app/                       # Next.js App Router
│   │   │   ├── layout.tsx            # Root layout
│   │   │   ├── page.tsx              # Home page
│   │   │   └── study-buddy/          # Study Buddy feature
│   │   │       ├── page.tsx          # Entry page with card
│   │   │       ├── dashboard/        # Main dashboard
│   │   │       │   └── page.tsx
│   │   │       └── results/          # Results pages
│   │   │           ├── questions/
│   │   │           ├── mock-tests/
│   │   │           ├── mnemonics/
│   │   │           ├── cheat-sheets/
│   │   │           └── notes/
│   │   │
│   │   ├── components/               # React Components
│   │   │   ├── ui/                   # Base UI components
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   └── Modal.tsx
│   │   │   ├── StudyBuddyCard.tsx   # Entry card component
│   │   │   ├── UploadSection.tsx    # File upload UI
│   │   │   ├── ProcessingStatus.tsx # Progress indicator
│   │   │   ├── ResultsViewer.tsx    # Results container
│   │   │   ├── QuestionBankViewer.tsx
│   │   │   ├── MockTestViewer.tsx
│   │   │   ├── MnemonicsViewer.tsx
│   │   │   ├── CheatSheetsViewer.tsx
│   │   │   ├── NotesViewer.tsx
│   │   │   └── SessionManager.tsx   # Session history
│   │   │
│   │   ├── lib/                      # Utilities and helpers
│   │   │   ├── api.ts               # API client
│   │   │   ├── auth.ts              # Auth helpers
│   │   │   ├── utils.ts             # General utilities
│   │   │   └── constants.ts         # App constants
│   │   │
│   │   ├── types/                    # TypeScript types
│   │   │   ├── index.ts
│   │   │   ├── api.ts
│   │   │   └── models.ts
│   │   │
│   │   ├── hooks/                    # Custom React hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useUpload.ts
│   │   │   └── useSession.ts
│   │   │
│   │   └── styles/                   # Global styles
│   │       └── globals.css
│   │
│   ├── public/                       # Static assets
│   │   ├── images/
│   │   └── icons/
│   │
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── .env.local
│
├── backend/                           # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py                   # FastAPI app entry
│   │   ├── config.py                 # Configuration
│   │   │
│   │   ├── models/                   # Database models
│   │   │   ├── __init__.py
│   │   │   ├── session.py
│   │   │   ├── question.py
│   │   │   ├── mock_test.py
│   │   │   ├── mnemonic.py
│   │   │   ├── cheat_sheet.py
│   │   │   └── note.py
│   │   │
│   │   ├── schemas/                  # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── session.py
│   │   │   ├── question.py
│   │   │   └── response.py
│   │   │
│   │   ├── services/                 # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── file_processor.py    # File handling
│   │   │   ├── ai_processor.py      # AI generation
│   │   │   ├── ocr_service.py       # OCR integration
│   │   │   ├── export_service.py    # PDF/Image export
│   │   │   └── session_service.py   # Session management
│   │   │
│   │   ├── api/                      # API routes
│   │   │   ├── __init__.py
│   │   │   ├── upload.py            # Upload endpoints
│   │   │   ├── process.py           # Processing endpoints
│   │   │   ├── questions.py         # Question endpoints
│   │   │   ├── mock_tests.py        # Mock test endpoints
│   │   │   ├── mnemonics.py         # Mnemonic endpoints
│   │   │   ├── cheat_sheets.py      # Cheat sheet endpoints
│   │   │   ├── notes.py             # Notes endpoints
│   │   │   └── download.py          # Download endpoints
│   │   │
│   │   ├── utils/                    # Utilities
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # JWT validation
│   │   │   ├── helpers.py           # Helper functions
│   │   │   ├── validators.py        # Input validation
│   │   │   └── exceptions.py        # Custom exceptions
│   │   │
│   │   ├── db/                       # Database
│   │   │   ├── __init__.py
│   │   │   ├── mongodb.py           # MongoDB connection
│   │   │   └── repositories/        # Data access layer
│   │   │       ├── session_repo.py
│   │   │       ├── question_repo.py
│   │   │       └── ...
│   │   │
│   │   └── tasks/                    # Celery tasks
│   │       ├── __init__.py
│   │       ├── process_files.py
│   │       └── generate_outputs.py
│   │
│   ├── tests/                        # Test suite
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   │
│   ├── uploads/                      # File storage (gitignored)
│   ├── downloads/                    # Generated files (gitignored)
│   │
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── .env
│   └── .env.example
│
├── docs/                              # Documentation
│   ├── API.md                        # API documentation
│   ├── SETUP.md                      # Setup instructions
│   ├── ARCHITECTURE.md               # Architecture overview
│   ├── DEPLOYMENT.md                 # Deployment guide
│   └── CONTRIBUTING.md               # Contribution guidelines
│
├── .kiro/                            # Kiro CLI configuration
│   ├── steering/
│   │   ├── product.md               # Product requirements
│   │   ├── tech.md                  # Technical specs
│   │   └── structure.md             # This file
│   ├── prompts/
│   └── settings/
│
├── scripts/                          # Utility scripts
│   ├── setup.sh                     # Initial setup
│   ├── seed_db.py                   # Database seeding
│   └── cleanup.sh                   # Cleanup old files
│
├── .gitignore
├── README.md                         # Project overview
├── DEVLOG.md                         # Development log
├── LICENSE
└── docker-compose.yml               # Docker setup (optional)
```

## Component Responsibilities

### Frontend Components

#### Core Components
- **StudyBuddyCard**: Entry point card on main dashboard
- **UploadSection**: File upload interface with drag-and-drop
- **ProcessingStatus**: Real-time processing progress display
- **SessionManager**: View and manage past sessions

#### Viewer Components
- **QuestionBankViewer**: Display generated questions with filters
- **MockTestViewer**: Interactive mock test interface
- **MnemonicsViewer**: Display mnemonics with search
- **CheatSheetsViewer**: Render cheat sheets with download options
- **NotesViewer**: Compiled notes display

#### UI Components
- **Button**: Reusable button component
- **Card**: Container component
- **Input**: Form input component
- **Modal**: Modal dialog component

### Backend Services

#### File Processing
- **FileProcessor**: Handle file uploads and text extraction
- **OCRService**: Integrate existing OCR scripts
- **ExportService**: Generate PDFs and images

#### AI Processing
- **AIProcessor**: Interface with GenAI API
  - Question generation
  - Mnemonic creation
  - Cheat sheet compilation
  - Notes generation

#### Data Management
- **SessionService**: Manage study sessions
- **Repositories**: Database access layer for each model

### API Routes

#### Upload & Processing
- `POST /api/v1/upload` - Upload files
- `GET /api/v1/process/{session_id}` - Get processing status

#### Results
- `GET /api/v1/questions/{session_id}` - Get questions
- `GET /api/v1/mock-tests/{session_id}` - Get mock tests
- `GET /api/v1/mnemonics/{session_id}` - Get mnemonics
- `GET /api/v1/cheat-sheets/{session_id}` - Get cheat sheets
- `GET /api/v1/notes/{session_id}` - Get notes

#### Downloads
- `GET /api/v1/download/{type}/{id}` - Download resource

## Data Flow

### Upload Flow
```
User (Frontend)
    ↓ [Upload files]
UploadSection Component
    ↓ [POST /api/v1/upload]
Upload API Route
    ↓ [Validate & Store]
FileProcessor Service
    ↓ [Create session]
SessionService
    ↓ [Queue task]
Celery Task Queue
    ↓ [Return session_id]
Frontend (Display status)
```

### Processing Flow
```
Celery Worker
    ↓ [Retrieve files]
FileProcessor
    ↓ [Extract text]
OCRService (if needed)
    ↓ [Send to AI]
AIProcessor
    ↓ [Generate outputs]
Multiple Services (parallel)
    ├── Question generation
    ├── Mock test creation
    ├── Mnemonic generation
    ├── Cheat sheet creation
    └── Notes compilation
    ↓ [Store in DB]
Repositories
    ↓ [Update status]
SessionService
```

### Results Flow
```
User (Frontend)
    ↓ [Request results]
ResultsViewer Component
    ↓ [GET /api/v1/{resource}/{session_id}]
API Route
    ↓ [Fetch from DB]
Repository
    ↓ [Return data]
Frontend (Display)
```

## File Organization Principles

### Frontend
- **App Router**: Use Next.js 14+ app directory structure
- **Components**: Organize by feature, then by type
- **Colocation**: Keep related files close (component + styles + tests)
- **Barrel Exports**: Use index files for clean imports

### Backend
- **Layered Architecture**: API → Service → Repository → Database
- **Separation of Concerns**: Each layer has single responsibility
- **Dependency Injection**: Services receive dependencies
- **Type Safety**: Use Pydantic for validation

## Naming Conventions

### Frontend
- **Components**: PascalCase (e.g., `StudyBuddyCard.tsx`)
- **Utilities**: camelCase (e.g., `formatDate.ts`)
- **Types**: PascalCase with descriptive names (e.g., `SessionResponse`)
- **Hooks**: camelCase with `use` prefix (e.g., `useAuth.ts`)

### Backend
- **Files**: snake_case (e.g., `file_processor.py`)
- **Classes**: PascalCase (e.g., `FileProcessor`)
- **Functions**: snake_case (e.g., `process_pdf`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_FILE_SIZE`)

## Configuration Files

### Frontend
- **package.json**: Dependencies and scripts
- **next.config.js**: Next.js configuration
- **tailwind.config.js**: Tailwind CSS configuration
- **tsconfig.json**: TypeScript configuration
- **.env.local**: Environment variables (gitignored)

### Backend
- **requirements.txt**: Python dependencies
- **requirements-dev.txt**: Development dependencies
- **.env**: Environment variables (gitignored)
- **.env.example**: Example environment variables (committed)

## Development Workflow

### Initial Setup
1. Clone repository
2. Install frontend dependencies: `cd frontend && npm install`
3. Install backend dependencies: `cd backend && pip install -r requirements.txt`
4. Setup MongoDB and Redis
5. Configure environment variables
6. Run database migrations/setup

### Development
1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Start Celery worker: `celery -A app.tasks worker --loglevel=info`
4. Start Redis: `redis-server`

### Testing
1. Frontend tests: `cd frontend && npm test`
2. Backend tests: `cd backend && pytest`
3. Integration tests: `pytest tests/integration`

### Deployment
1. Build frontend: `npm run build`
2. Setup production environment
3. Configure reverse proxy (Nginx)
4. Setup process manager (PM2/Supervisor)
5. Configure SSL certificates

## Integration Points

### MedGloss Integration
- **Authentication**: Use existing JWT validation
- **User Model**: Reference existing user collection
- **Database**: Share MongoDB instance
- **Frontend**: Integrate as new route in existing app

### External Services
- **OCR Scripts**: Located at `/home/unknown/Documents/medgloss-data-extractorfiles`
- **GenAI API**: Use existing credentials
- **MongoDB**: Local instance at `mongodb://localhost:27017`

## Security Considerations

### File Storage
- Store uploads outside web root
- Generate unique filenames (UUID)
- Validate file types and sizes
- Automatic cleanup of old files

### API Security
- JWT authentication on all endpoints
- Rate limiting per user
- Input validation with Pydantic
- CORS configuration

### Data Security
- User-specific data isolation
- Encrypted sensitive data
- Secure environment variables
- Regular security audits

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Session data in Redis
- File storage on shared filesystem/S3
- Load balancer for multiple instances

### Database Scaling
- Proper indexing
- Connection pooling
- Read replicas for heavy queries
- Sharding for large datasets

### Caching Strategy
- Redis for session data
- Cache AI responses
- CDN for static assets
- Database query caching

## Monitoring & Logging

### Logging
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Separate log files per service
- Log rotation and retention

### Monitoring
- API response times
- Error rates
- Processing queue length
- Database performance
- File storage usage

## Documentation Standards

### Code Documentation
- Docstrings for all functions/classes
- Inline comments for complex logic
- Type hints in Python
- JSDoc comments in TypeScript

### API Documentation
- OpenAPI/Swagger for backend
- Request/response examples
- Error code documentation
- Authentication requirements

### User Documentation
- Setup instructions
- Usage guides
- Troubleshooting
- FAQ section
