# Study Buddy App - System Architecture Documentation

## 🏗️ Complete System Architecture

This document provides comprehensive system architecture documentation for the Study Buddy App, including all system diagrams, component interactions, and architectural decisions.

---

## 📊 High-Level System Architecture

```mermaid
graph TB
    subgraph "Frontend (Next.js)"
        A[Study Buddy UI] --> B[Authentication]
        A --> C[File Upload]
        A --> D[Text Input]
        A --> E[Results Viewer]
        A --> F[Session History]
    end
    
    subgraph "Backend (FastAPI)"
        G[API Gateway] --> H[Auth Service]
        G --> I[Upload Service]
        G --> J[Processing Service]
        G --> K[AI Service]
    end
    
    subgraph "External Services"
        L[Google Gemini API]
        M[OTP Service]
        N[OCR Engine]
    end
    
    subgraph "Database"
        O[(MongoDB)]
    end
    
    B --> H
    C --> I
    D --> I
    I --> J
    J --> K
    K --> L
    H --> M
    J --> N
    H --> O
    I --> O
    J --> O
    K --> O
    
    E --> G
    F --> G
```

## 🔄 Application Flow Architecture

```mermaid
flowchart TD
    Start([User Opens App]) --> Auth{Authenticated?}
    
    Auth -->|No| Login[Login/Register Page]
    Login --> OTP[Enter Mobile & OTP]
    OTP --> Dashboard[Study Buddy Dashboard]
    
    Auth -->|Yes| Dashboard
    
    Dashboard --> Choice{Input Method}
    
    Choice -->|Files| Upload[File Upload Interface]
    Choice -->|Text| TextInput[Text Input Form]
    
    Upload --> FileValidation{Valid Files?}
    FileValidation -->|No| UploadError[Show Error Message]
    UploadError --> Upload
    FileValidation -->|Yes| ProcessFiles[Process Files]
    
    TextInput --> ProcessText[Process Text Input]
    
    ProcessFiles --> Extract[Text Extraction]
    ProcessText --> Extract
    
    Extract --> AIProcess[AI Content Generation]
    
    AIProcess --> Generate[Generate 5 Content Types]
    
    Generate --> Questions[📝 Questions]
    Generate --> MockTests[🎯 Mock Tests]
    Generate --> Mnemonics[🧠 Mnemonics]
    Generate --> CheatSheets[📋 Cheat Sheets]
    Generate --> Notes[📚 Notes]
    Generate --> Flashcards[🃏 Flashcards]
    
    Questions --> Results[Results Viewer]
    MockTests --> Results
    Mnemonics --> Results
    CheatSheets --> Results
    Notes --> Results
    Flashcards --> FlashcardReview[Flashcard Review System]
    
    Results --> Actions{User Action}
    Actions -->|Take Test| TestInterface[Mock Test Interface]
    Actions -->|Study Plan| StudyPlanner[Study Planner]
    Actions -->|Download| Export[Export Content]
    Actions -->|New Session| Dashboard
    Actions -->|View History| History[Session History]
    
    FlashcardReview --> SpacedRepetition[Spaced Repetition Algorithm]
    SpacedRepetition --> Results
    
    StudyPlanner --> PlanGeneration[AI Plan Generation]
    PlanGeneration --> DailySchedule[Daily Study Schedule]
    DailySchedule --> ProgressTracking[Progress Tracking]
    ProgressTracking --> Results
    
    TestInterface --> TestResults[Test Results & Analytics]
    TestResults --> Results
    
    History --> SessionDetails[Session Details]
    SessionDetails --> Results
    
    Export --> Download[Download Files]
    Download --> Results
```

## 🏛️ Technical Architecture

```mermaid
graph LR
    subgraph "Client Layer"
        A[React Components]
        B[Context API]
        C[Custom Hooks]
    end
    
    subgraph "API Layer"
        D[REST Endpoints]
        E[Authentication Middleware]
        F[File Upload Handler]
    end
    
    subgraph "Service Layer"
        G[Auth Service]
        H[File Processor]
        I[AI Service]
        J[Content Aggregator]
    end
    
    subgraph "Data Layer"
        K[MongoDB Collections]
        L[File Storage]
        M[Session Management]
    end
    
    A --> D
    B --> E
    C --> F
    
    D --> G
    E --> H
    F --> I
    
    G --> K
    H --> L
    I --> M
    J --> K
```

## 🔐 Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant O as OTP Service
    participant D as Database
    
    U->>F: Enter Mobile Number
    F->>B: POST /api/v1/auth/send-otp
    B->>O: Send OTP Request
    O-->>B: OTP Sent
    B-->>F: Success Response
    F-->>U: "OTP Sent" Message
    
    U->>F: Enter OTP & Password
    F->>B: POST /api/v1/auth/register
    B->>O: Verify OTP
    O-->>B: OTP Valid
    B->>D: Create User
    D-->>B: User Created
    B-->>F: JWT Token
    F-->>U: Login Success
```

## 📁 Processing Pipeline Architecture

```mermaid
flowchart LR
    subgraph "Input Processing"
        A[File Upload] --> B{File Type}
        B -->|PDF| C[PDF Text Extraction]
        B -->|Image| D[OCR Processing]
        B -->|PPTX| E[Slide Text Extraction]
        F[Text Input] --> G[Direct Text]
    end
    
    subgraph "AI Processing"
        C --> H[Combined Text]
        D --> H
        E --> H
        G --> H
        
        H --> I[AI Content Generation]
        
        I --> J[Question Generator]
        I --> K[Mock Test Creator]
        I --> L[Mnemonic Generator]
        I --> M[Cheat Sheet Compiler]
        I --> N[Notes Aggregator]
    end
    
    subgraph "Output Generation"
        J --> O[25 MCQs with Explanations]
        K --> P[Timed Mock Tests]
        L --> Q[India-Specific Mnemonics]
        M --> R[High-Yield Summaries]
        N --> S[Comprehensive Notes]
    end
    
    subgraph "Storage & Delivery"
        O --> T[(Database)]
        P --> T
        Q --> T
        R --> T
        S --> T
        
        T --> U[Results API]
        U --> V[Frontend Display]
    end
```

## 🎨 User Interface Flow

```mermaid
graph TD
    A[Landing Page] --> B{User Status}
    B -->|New User| C[Registration Form]
    B -->|Existing User| D[Login Form]
    
    C --> E[OTP Verification]
    D --> F[Password Login]
    E --> G[Dashboard]
    F --> G
    
    G --> H[Study Buddy Card]
    H --> I[Upload Interface]
    
    I --> J{Input Type}
    J -->|Files| K[Drag & Drop Zone]
    J -->|Text| L[Text Area Input]
    
    K --> M[File Preview]
    L --> N[Session Name Input]
    M --> N
    
    N --> O[Process Button]
    O --> P[Processing Status]
    
    P --> Q[Progress Indicator]
    Q --> R{Processing Complete?}
    R -->|No| Q
    R -->|Yes| S[Results Dashboard]
    
    S --> T[Content Tabs]
    T --> U[Questions Tab]
    T --> V[Mock Tests Tab]
    T --> W[Mnemonics Tab]
    T --> X[Cheat Sheets Tab]
    T --> Y[Notes Tab]
    
    U --> Z[Interactive Questions]
    V --> AA[Test Interface]
    W --> BB[Mnemonic Cards]
    X --> CC[Summary Sheets]
    Y --> DD[Compiled Notes]
    
    AA --> EE[Test Results]
    EE --> FF[Performance Analytics]
    
    S --> GG[Session History]
    GG --> HH[Previous Sessions]
    HH --> S
```

## 🚀 Feature Overview Architecture

```mermaid
mindmap
  root((Study Buddy))
    Authentication
      Mobile OTP
      JWT Tokens
      Session Management
      User Registration
    File Processing
      PDF Upload
      Image Upload
      PPTX Upload
      OCR Integration
      Text Extraction
    AI Generation
      Question Banks
        MCQs
        Explanations
        Difficulty Levels
        Subject Classification
      Mock Tests
        Timed Tests
        Auto Scoring
        Performance Analytics
        Question Navigation
      Mnemonics
        India Specific
        Memory Aids
        Visual Associations
        Cultural Context
      Cheat Sheets
        Key Points
        High Yield Facts
        Quick Reference
        Downloadable PDFs
      Study Notes
        Comprehensive Summary
        Organized Content
        Searchable Format
        Export Options
      Flashcards
        AI Generated
        Spaced Repetition
        Difficulty Rating
        Progress Tracking
        Review Analytics
    Study Planning
      AI Plan Generation
        Personalized Schedules
        Daily Task Breakdown
        Subject Distribution
        Progress Tracking
      Task Management
        Completion Tracking
        Status Updates
        Priority Levels
        Time Estimation
      Progress Analytics
        Completion Rates
        Study Streaks
        Performance Metrics
        Visual Charts
    Export System
      PDF Generation
        Custom Styling
        Professional Layout
        Multiple Content Types
        Batch Export
      JSON Export
        Data Portability
        API Integration
        Structured Format
        Backup Support
      Image Export
        Visual Content
        Social Sharing
        Print Ready
        High Quality
    User Experience
      Responsive Design
      Drag Drop Upload
      Real Time Progress
      Session History
      Error Handling
      Interactive UI
      Mobile Optimized
      Accessibility
```

## 📊 Data Flow Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI1[File Upload Component]
        UI2[Text Input Component]
        UI3[Results Viewer]
        UI4[Session Manager]
        UI5[Authentication Forms]
    end
    
    subgraph "API Gateway Layer"
        API1[Auth API]
        API2[Upload API]
        API3[Text Input API]
        API4[History API]
    end
    
    subgraph "Business Logic Layer"
        BL1[Authentication Service]
        BL2[File Processing Service]
        BL3[AI Content Generator]
        BL4[Session Management]
        BL5[Progress Tracker]
    end
    
    subgraph "External Services"
        EXT1[Google Gemini API]
        EXT2[OTP Service]
        EXT3[OCR Engine]
    end
    
    subgraph "Data Storage"
        DB1[(Users Collection)]
        DB2[(Sessions Collection)]
        DB3[(Questions Collection)]
        DB4[(Mock Tests Collection)]
        DB5[(Mnemonics Collection)]
        DB6[(Cheat Sheets Collection)]
        DB7[(Notes Collection)]
        FS1[File Storage]
    end
    
    UI1 --> API2
    UI2 --> API3
    UI3 --> API4
    UI4 --> API4
    UI5 --> API1
    
    API1 --> BL1
    API2 --> BL2
    API3 --> BL2
    API4 --> BL4
    
    BL1 --> EXT2
    BL1 --> DB1
    BL2 --> EXT3
    BL2 --> BL3
    BL2 --> FS1
    BL3 --> EXT1
    BL3 --> DB3
    BL3 --> DB4
    BL3 --> DB5
    BL3 --> DB6
    BL3 --> DB7
    BL4 --> DB2
    BL5 --> DB2
```

## 🔄 Content Generation Workflow

```mermaid
stateDiagram-v2
    [*] --> FileUpload: User uploads files
    [*] --> TextInput: User enters text
    
    FileUpload --> FileValidation: Validate files
    FileValidation --> FileProcessing: Valid files
    FileValidation --> Error: Invalid files
    Error --> FileUpload: Retry
    
    FileProcessing --> TextExtraction: Extract text
    TextInput --> TextProcessing: Process input
    
    TextExtraction --> ContentAnalysis: Analyze content
    TextProcessing --> ContentAnalysis: Analyze content
    
    ContentAnalysis --> AIGeneration: Send to AI
    
    state AIGeneration {
        [*] --> QuestionGen: Generate Questions
        [*] --> MockTestGen: Generate Mock Tests
        [*] --> MnemonicGen: Generate Mnemonics
        [*] --> CheatSheetGen: Generate Cheat Sheets
        [*] --> NotesGen: Generate Notes
        [*] --> FlashcardGen: Generate Flashcards
        
        QuestionGen --> QuestionsReady
        MockTestGen --> MockTestsReady
        MnemonicGen --> MnemonicsReady
        CheatSheetGen --> CheatSheetsReady
        NotesGen --> NotesReady
        FlashcardGen --> FlashcardsReady
    }
    
    QuestionsReady --> ResultsCompilation
    MockTestsReady --> ResultsCompilation
    MnemonicsReady --> ResultsCompilation
    CheatSheetsReady --> ResultsCompilation
    NotesReady --> ResultsCompilation
    FlashcardsReady --> ResultsCompilation
    
    ResultsCompilation --> SessionSaved: Save to database
    SessionSaved --> ResultsDisplay: Display to user
    ResultsDisplay --> [*]: Session complete
```

## 🃏 Flashcard System Flow

```mermaid
flowchart TD
    SessionContent[Session Content] --> FlashcardGen[AI Flashcard Generator]
    
    FlashcardGen --> CreateCards[Create Flashcards]
    CreateCards --> StoreDB[(Store in Database)]
    
    StoreDB --> UserAccess[User Access Flashcards]
    UserAccess --> ReviewInterface[Flashcard Review Interface]
    
    ReviewInterface --> ShowQuestion[Show Question]
    ShowQuestion --> UserThinks[User Thinks]
    UserThinks --> RevealAnswer[Reveal Answer]
    
    RevealAnswer --> UserRating{User Rates Difficulty}
    UserRating -->|Easy| EasySchedule[Next Review: 4 days]
    UserRating -->|Medium| MediumSchedule[Next Review: 2 days]
    UserRating -->|Hard| HardSchedule[Next Review: 1 day]
    
    EasySchedule --> UpdateSpacing[Update Spaced Repetition]
    MediumSchedule --> UpdateSpacing
    HardSchedule --> UpdateSpacing
    
    UpdateSpacing --> NextCard{More Cards?}
    NextCard -->|Yes| ShowQuestion
    NextCard -->|No| SessionComplete[Review Session Complete]
    
    SessionComplete --> Analytics[Show Progress Analytics]
    Analytics --> UserAccess
```

## 📅 Study Planner Flow

```mermaid
flowchart TD
    UserInput[User Inputs Plan Config] --> ConfigValidation{Valid Config?}
    ConfigValidation -->|No| ShowError[Show Validation Error]
    ShowError --> UserInput
    
    ConfigValidation -->|Yes| GatherContent[Gather Session Content]
    GatherContent --> ContentAnalysis[Analyze Available Content]
    
    ContentAnalysis --> AIPlanning[AI Study Plan Generation]
    
    AIPlanning --> BasicPlan[Generate Basic Plan Structure]
    BasicPlan --> WeeklySchedules[Generate Weekly Schedules]
    WeeklySchedules --> DailyTasks[Convert to Daily Tasks]
    
    DailyTasks --> TaskValidation[Validate Tasks & Subjects]
    TaskValidation --> CreatePlan[Create StudyPlan Object]
    
    CreatePlan --> SaveDB[(Save to Database)]
    SaveDB --> InitProgress[Initialize Progress Tracking]
    
    InitProgress --> DisplayPlan[Display Study Plan]
    DisplayPlan --> UserInteraction{User Action}
    
    UserInteraction -->|Mark Complete| UpdateTask[Update Task Status]
    UserInteraction -->|View Progress| ShowProgress[Show Progress Analytics]
    UserInteraction -->|Modify Plan| EditPlan[Edit Plan Settings]
    
    UpdateTask --> RecalculateProgress[Recalculate Progress]
    RecalculateProgress --> SaveProgress[(Update Progress DB)]
    SaveProgress --> DisplayPlan
    
    ShowProgress --> ProgressCharts[Show Charts & Stats]
    ProgressCharts --> DisplayPlan
    
    EditPlan --> UserInput
```

## 📥 Export System Flow

```mermaid
flowchart TD
    UserRequest[User Requests Export] --> SelectContent{Select Content Type}
    
    SelectContent -->|Questions| ExportQuestions[Export Questions]
    SelectContent -->|Flashcards| ExportFlashcards[Export Flashcards]
    SelectContent -->|Notes| ExportNotes[Export Notes]
    SelectContent -->|Cheat Sheets| ExportCheatSheets[Export Cheat Sheets]
    SelectContent -->|Mnemonics| ExportMnemonics[Export Mnemonics]
    SelectContent -->|Study Plan| ExportStudyPlan[Export Study Plan]
    
    ExportQuestions --> FormatChoice{Choose Format}
    ExportFlashcards --> FormatChoice
    ExportNotes --> FormatChoice
    ExportCheatSheets --> FormatChoice
    ExportMnemonics --> FormatChoice
    ExportStudyPlan --> FormatChoice
    
    FormatChoice -->|PDF| GeneratePDF[Generate PDF Document]
    FormatChoice -->|JSON| GenerateJSON[Generate JSON Export]
    FormatChoice -->|Image| GenerateImage[Generate Image Export]
    
    GeneratePDF --> PDFStyling[Apply Custom PDF Styling]
    PDFStyling --> TempFile[Create Temporary File]
    
    GenerateJSON --> JSONFormat[Format as JSON]
    JSONFormat --> TempFile
    
    GenerateImage --> ImageGeneration[Generate Image]
    ImageGeneration --> TempFile
    
    TempFile --> FileValidation{File Created?}
    FileValidation -->|No| ExportError[Show Export Error]
    FileValidation -->|Yes| ServeFile[Serve File for Download]
    
    ServeFile --> CleanupFile[Schedule File Cleanup]
    CleanupFile --> DownloadComplete[Download Complete]
    
    ExportError --> UserRequest
    DownloadComplete --> UserRequest
```

---

## 🏗️ Architectural Decisions

### Technology Stack Rationale

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Frontend** | Next.js 14 + React 18 | Modern React patterns, server components, excellent TypeScript support |
| **Backend** | FastAPI + Python 3.12 | High performance async API, automatic OpenAPI docs, excellent for AI integration |
| **Database** | MongoDB | Flexible schema for varied medical content types, excellent for session-based data |
| **AI Service** | Google Gemini API | Cost-effective, excellent medical content generation, good JSON response handling |
| **Authentication** | JWT + Mobile OTP | Secure, stateless, perfect for Indian medical student market |
| **Styling** | TailwindCSS | Utility-first, responsive design, excellent for medical education UI |

### Scalability Considerations

- **Horizontal Scaling**: Stateless API design allows multiple backend instances
- **Database Optimization**: Proper indexing and connection pooling for medical content queries
- **Caching Strategy**: Redis for session data and frequently accessed medical content
- **File Storage**: Configurable local/S3 storage for medical documents
- **AI Service**: Rate limiting and retry mechanisms for reliable medical content generation

### Security Architecture

- **Authentication**: JWT tokens with mobile OTP verification
- **Authorization**: User-specific data isolation for medical study sessions
- **Data Protection**: Encrypted sensitive data, secure environment variables
- **API Security**: Rate limiting, input validation, CORS configuration
- **File Security**: Upload validation, size limits, secure file storage

---

## 📈 Performance Optimization

### Backend Optimizations
- **Async Processing**: All I/O operations use async/await patterns
- **Database Indexing**: Optimized queries for medical content retrieval
- **Connection Pooling**: Efficient database connection management
- **Caching**: Redis caching for frequently accessed medical data

### Frontend Optimizations
- **Code Splitting**: Dynamic imports for medical education components
- **Image Optimization**: Next.js automatic image optimization
- **Bundle Optimization**: Tree shaking and minification
- **Lazy Loading**: Components loaded on demand for better performance

### AI Service Optimizations
- **Request Batching**: Multiple content types generated in single AI call
- **Response Caching**: Cache similar medical content requests
- **Error Handling**: Robust retry mechanisms for AI service reliability
- **Rate Limiting**: Respect AI service limits while maintaining performance

---

*This architecture documentation provides complete system understanding for developers, administrators, and medical education professionals working with the Study Buddy App.*
