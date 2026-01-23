<p align="center">
  <img src="https://img.shields.io/badge/Hackathon-Kiro%202026-ff69b4?style=for-the-badge&logo=github" alt="Kiro Hackathon 2026"/>
  <img src="https://img.shields.io/badge/Status-Live-brightgreen?style=for-the-badge" alt="Status"/>
  <img src="https://img.shields.io/badge/AI%20Powered-Gemini-4285F4?style=for-the-badge&logo=google" alt="AI Powered"/>
</p>

<h1 align="center">
  🎓 Study Buddy
  <br/>
  <sub>AI-Powered Study Companion for Medical Students</sub>
</h1>

<p align="center">
  <strong>Transform your study materials into actionable resources with the power of AI</strong>
</p>

<p align="center">
  <a href="https://study-material-generator.netlify.app/">
    <img src="https://img.shields.io/badge/🚀%20LIVE%20DEMO-study--material--generator.netlify.app-success?style=for-the-badge&labelColor=000000" alt="Live Demo"/>
  </a>
</p>

---

## 🌐 Live Application

<table align="center">
  <tr>
    <td align="center">
      <h3>🔗 Live Website</h3>
      <a href="https://study-material-generator.netlify.app/">
        <strong>https://study-material-generator.netlify.app/</strong>
      </a>
    </td>
  </tr>
  <tr>
    <td align="center">
      <h3>🔐 Test Credentials</h3>
      <code>Mobile: 1234567890</code> | <code>Password: test_password</code>
    </td>
  </tr>
</table>

---

## 📚 Documentation

<table>
  <tr>
    <td align="center" width="25%">
      <a href="docs/FRONTEND_DOCUMENTATION.md">
        <img src="https://img.shields.io/badge/Frontend-Documentation-3b82f6?style=for-the-badge" alt="Frontend Docs"/>
      </a>
      <br/>
      <sub>Components, State, UI/UX</sub>
    </td>
    <td align="center" width="25%">
      <a href="docs/BACKEND_DOCUMENTATION.md">
        <img src="https://img.shields.io/badge/Backend-Documentation-10b981?style=for-the-badge" alt="Backend Docs"/>
      </a>
      <br/>
      <sub>Architecture, Services, DB</sub>
    </td>
    <td align="center" width="25%">
      <a href="docs/API_DOCUMENTATION.md">
        <img src="https://img.shields.io/badge/API-Documentation-f59e0b?style=for-the-badge" alt="API Docs"/>
      </a>
      <br/>
      <sub>Endpoints, Auth, Examples</sub>
    </td>
    <td align="center" width="25%">
      <a href="docs/TEST_DOCUMENTATION.md">
        <img src="https://img.shields.io/badge/Test-Documentation-ef4444?style=for-the-badge" alt="Test Docs"/>
      </a>
      <br/>
      <sub>Testing Guide, CI/CD</sub>
    </td>
  </tr>
</table>

---

## 🏆 Kiro Hackathon Submission

> **January 5-30, 2026** | Built with ❤️ using Kiro CLI

Study Buddy is an **AI-powered study companion** specifically designed for medical students. It transforms study materials—whether PDFs, images, or topic text—into comprehensive, actionable resources including:

| 📝 Question Banks | 🎯 Mock Tests | 🧠 Mnemonics | 📋 Cheat Sheets | 📚 Notes | 🃏 Flashcards |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 25+ MCQs per session | Timed tests with analytics | India-specific memory aids | High-yield summaries | Comprehensive notes | Spaced repetition |

---

## ✨ Key Features

<table>
<tr>
<td width="50%">

### 📤 Smart Input Processing
- **Multi-Format Upload**: PDF, Images (JPG/PNG), PPTX
- **Topic-Based Generation**: Enter any topic to generate materials
- **OCR Integration**: Extract text from scanned documents
- **Batch Processing**: Upload multiple files at once

</td>
<td width="50%">

### 🤖 AI-Powered Generation
- **Question Banks**: 25+ MCQs with detailed explanations
- **Mock Tests**: Timed assessments with auto-scoring
- **Mnemonics**: Culturally relevant memory aids
- **Cheat Sheets**: High-yield facts & quick references
- **Study Notes**: Comprehensive, organized summaries

</td>
</tr>
<tr>
<td width="50%">

### 🃏 Flashcard System
- **AI-Generated Cards**: Automatic flashcard creation
- **Spaced Repetition**: SM-2 algorithm for optimal retention
- **Difficulty Rating**: Easy/Medium/Hard classifications
- **Progress Tracking**: Visual analytics & review history

</td>
<td width="50%">

### 📅 Study Planner
- **AI Plan Generation**: Personalized study schedules
- **Daily Task Breakdown**: Structured daily goals
- **Progress Tracking**: Completion rates & streaks
- **Subject Distribution**: Balanced topic coverage

</td>
</tr>
<tr>
<td width="50%">

### 📥 Export System
- **PDF Generation**: Professional, styled documents
- **JSON Export**: Data portability & backups
- **Image Export**: Visual content for sharing
- **Batch Downloads**: Export all content at once

</td>
<td width="50%">

### 🔐 Security & Authentication
- **Mobile OTP**: Secure phone verification
- **JWT Tokens**: Session management
- **Rate Limiting**: API protection (100 req/min)
- **Input Validation**: Comprehensive security checks

</td>
</tr>
</table>

---

## 📊 System Architecture

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

---

## 🔄 Application Flow

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

---

## 🏗️ Technical Architecture

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

---

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

---

## 📁 Processing Pipeline

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

---

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

---

## 🚀 Feature Overview

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

---

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

---

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

---

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

---

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

---

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

## 💻 Tech Stack

<table align="center">
  <tr>
    <th>Layer</th>
    <th>Technology</th>
    <th>Purpose</th>
  </tr>
  <tr>
    <td><strong>Frontend</strong></td>
    <td>
      <img src="https://img.shields.io/badge/Next.js-14-black?logo=next.js" alt="Next.js"/>
      <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react" alt="React"/>
      <img src="https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript" alt="TypeScript"/>
      <img src="https://img.shields.io/badge/TailwindCSS-3-06B6D4?logo=tailwindcss" alt="TailwindCSS"/>
    </td>
    <td>Modern, responsive UI with type safety</td>
  </tr>
  <tr>
    <td><strong>Backend</strong></td>
    <td>
      <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi" alt="FastAPI"/>
      <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python" alt="Python"/>
      <img src="https://img.shields.io/badge/Uvicorn-ASGI-499848" alt="Uvicorn"/>
    </td>
    <td>High-performance async API server</td>
  </tr>
  <tr>
    <td><strong>Database</strong></td>
    <td>
      <img src="https://img.shields.io/badge/MongoDB-6.0-47A248?logo=mongodb" alt="MongoDB"/>
      <img src="https://img.shields.io/badge/Motor-Async-47A248" alt="Motor"/>
    </td>
    <td>Flexible document storage</td>
  </tr>
  <tr>
    <td><strong>AI</strong></td>
    <td>
      <img src="https://img.shields.io/badge/Google%20Gemini-API-4285F4?logo=google" alt="Gemini"/>
    </td>
    <td>Advanced content generation</td>
  </tr>
  <tr>
    <td><strong>Auth</strong></td>
    <td>
      <img src="https://img.shields.io/badge/JWT-Tokens-000000?logo=jsonwebtokens" alt="JWT"/>
      <img src="https://img.shields.io/badge/OTP-SMS/Email-FF6B6B" alt="OTP"/>
    </td>
    <td>Secure authentication</td>
  </tr>
  <tr>
    <td><strong>Deployment</strong></td>
    <td>
      <img src="https://img.shields.io/badge/Netlify-Frontend-00C7B7?logo=netlify" alt="Netlify"/>
      <img src="https://img.shields.io/badge/AWS%20EC2-Backend-FF9900?logo=amazonaws" alt="AWS"/>
    </td>
    <td>Scalable cloud hosting</td>
  </tr>
</table>

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Register with mobile + OTP |
| `/api/v1/auth/login` | POST | Login with mobile + password |
| `/api/v1/upload/` | POST | Upload files for processing |
| `/api/v1/text-input/` | POST | Generate from topic text |
| `/api/v1/flashcards/{session_id}` | GET | Get session flashcards |
| `/api/v1/study-planner/generate-plan` | POST | Generate AI study plan |
| `/api/v1/download/{type}/{id}` | GET | Export/download content |
| `/api/v1/sessions` | GET | Get user's session history |

> 📖 **[Complete API Documentation](docs/API_DOCUMENTATION.md)** for detailed endpoints, request/response formats, and examples

---

## 🔌 API Flow Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as API Gateway
    participant Auth as Auth Service
    participant File as File Service
    participant AI as AI Service
    participant DB as Database
    participant Ext as External APIs
    
    Note over U,Ext: Authentication Flow
    U->>F: Login Request
    F->>API: POST /auth/login
    API->>Auth: Validate Credentials
    Auth->>DB: Check User
    DB-->>Auth: User Data
    Auth->>Ext: Send OTP
    Ext-->>Auth: OTP Sent
    Auth-->>API: OTP Response
    API-->>F: Login Status
    F-->>U: Show OTP Input
    
    U->>F: Enter OTP
    F->>API: POST /auth/verify
    API->>Auth: Verify OTP
    Auth->>Ext: Validate OTP
    Ext-->>Auth: OTP Valid
    Auth-->>API: JWT Token
    API-->>F: Auth Success
    F-->>U: Dashboard Access
    
    Note over U,Ext: File Processing Flow
    U->>F: Upload Files
    F->>API: POST /upload (with JWT)
    API->>Auth: Validate Token
    Auth-->>API: Token Valid
    API->>File: Process Files
    File->>File: Extract Text
    File->>AI: Generate Content
    AI->>Ext: Call Gemini API
    Ext-->>AI: AI Response
    AI->>DB: Store Results
    DB-->>AI: Stored
    AI-->>File: Processing Complete
    File-->>API: Session Created
    API-->>F: Session ID
    F-->>U: Processing Started
    
    Note over U,Ext: Results Retrieval
    U->>F: View Results
    F->>API: GET /results/{session_id}
    API->>Auth: Validate Token
    Auth-->>API: Token Valid
    API->>DB: Fetch Results
    DB-->>API: Session Data
    API-->>F: Results Data
    F-->>U: Display Results
```

---

## 🎯 Component Interaction Flow

```mermaid
graph TD
    subgraph FrontendComponents[Frontend Components]
        A[App Layout] --> B[Auth Provider]
        B --> C[Dashboard]
        C --> D[Study Buddy Card]
        D --> E[Upload Interface]
        E --> F[File Upload]
        E --> G[Text Input]
        F --> H[Processing Status]
        G --> H
        H --> I[Results Viewer]
        I --> J[Question Viewer]
        I --> K[Mock Test Interface]
        I --> L[Mnemonics Display]
        I --> M[Cheat Sheets]
        I --> N[Notes Viewer]
        K --> O[Test Results]
        C --> P[Session History]
    end
    
    subgraph BackendServices[Backend Services]
        Q[FastAPI App] --> R[Auth Middleware]
        R --> S[Upload Handler]
        R --> T[History Handler]
        S --> U[File Processor]
        U --> V[Text Extractor]
        V --> W[AI Service]
        W --> X[Content Generator]
        X --> Y[Database Writer]
        T --> Z[Session Manager]
        Z --> Y
    end
    
    subgraph ExternalServices[External Services]
        AA[Google Gemini]
        BB[OTP Service]
        CC[OCR Engine]
    end
    
    subgraph Database
        DD[(MongoDB)]
    end
    
    F --> S
    G --> S
    J --> T
    P --> T
    W --> AA
    R --> BB
    V --> CC
    Y --> DD
    Z --> DD
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required software
- Python 3.12+
- Node.js 18+
- MongoDB running on localhost:27017
```

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # Edit with your API keys

# Run server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

🌐 Open **http://localhost:3000**

---

## ⚙️ Configuration Options

### File Storage Configuration
```bash
# Local file storage (default)
FILE_STORAGE_TYPE=local
UPLOAD_DIR=./uploads

# AWS S3 storage
FILE_STORAGE_TYPE=s3
AWS_S3_BUCKET=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

### Rate Limiting & Security
```bash
# Rate limiting (requests per minute per user)
RATE_LIMIT_PER_MINUTE=100

# File upload limits
MAX_FILE_SIZE=52428800  # 50MB in bytes
MAX_FILES_PER_UPLOAD=10
ALLOWED_FILE_TYPES=pdf,jpg,jpeg,png,pptx

# Security settings
JWT_EXPIRY_HOURS=24
OTP_EXPIRY_MINUTES=5
```

### Mock Test Features
- **Timed Tests**: Configurable duration (default: 60 minutes)
- **Auto-Scoring**: Immediate results with detailed analytics
- **Question Navigation**: Jump to any question, mark for review
- **Performance Analytics**: Score breakdown, time per question
- **Retry Capability**: Retake tests multiple times
- **Progress Tracking**: Track improvement over time

### Email Notification System
```bash
# Email service configuration
ENABLE_EMAIL_NOTIFICATIONS=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=studybuddy@yourapp.com

# Notification settings
NOTIFY_ON_COMPLETION=true
NOTIFY_ON_ERROR=true
EMAIL_TEMPLATE_PATH=./templates/emails/
```

**Email Features:**
- **Processing Complete**: Notify when AI generation is finished
- **Error Alerts**: Notify if processing fails
- **Custom Templates**: Professional email templates
- **User Preference**: Users can opt-in/out of notifications
- **Session Links**: Direct links to view results

---

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── services/      # AI, processing, auth services
│   │   ├── config.py      # App configuration
│   │   └── main.py        # FastAPI app
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/           # Next.js pages
│       ├── components/    # React components
│       └── contexts/      # Auth context
├── docs/
│   ├── API_DOCUMENTATION.md       # API reference
│   ├── BACKEND_DOCUMENTATION.md   # Backend architecture
│   ├── FRONTEND_DOCUMENTATION.md  # Frontend guide
│   └── TEST_DOCUMENTATION.md      # Testing guide
└── .kiro/
    ├── steering/          # Project docs (product, tech, structure)
    ├── prompts/           # Custom Kiro commands
    └── documentation/     # Kiro CLI reference
```

---

## 🛠️ Kiro Development

This project was built using **Kiro CLI**. Key customizations:

- **Steering docs**: `.kiro/steering/` - Product, tech, and structure specs
- **Custom prompts**: `.kiro/prompts/` - 12 reusable prompts for development
- **Development workflow**: Agentic coding with Kiro's planning and execution modes

---

## 📈 Performance & Scalability

| Metric | Value |
|--------|-------|
| **Processing Time** | 2-5 minutes per session |
| **Concurrent Users** | Tested up to 100 |
| **API Response Time** | < 200ms (avg) |
| **File Upload Limit** | 50MB per file, 200MB total |
| **Rate Limit** | 100 requests/minute/user |

---

## 🎥 Demo

Coming soon! Stay tuned for video walkthrough.

---

## 👨‍💻 Author

<p align="center">
  <strong>Deepak Yadav</strong>
  <br/>
  Built with ❤️ for the <strong>Dynamous Kiro Hackathon 2026</strong>
</p>

---

## 📄 License

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge" alt="MIT License"/>
</p>

---

<p align="center">
  <sub>© 2026 Study Buddy | AI-Powered Study Companion</sub>
</p>
