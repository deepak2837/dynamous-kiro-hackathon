# Study Buddy - AI-Powered Study Companion

> 🏆 **Kiro Hackathon Submission** (January 5-30, 2026)

An AI-powered study companion for medical students that transforms study materials into actionable resources including question banks, mock tests, mnemonics, cheat sheets, and compiled notes.

## 🎯 Features

- **Multi-Format Upload**: PDF documents, images, scanned notes
- **Topic-Based Generation**: Enter any topic to generate study materials
- **5 Output Types**: Questions, Mock Tests, Mnemonics, Cheat Sheets, Notes
- **Session History**: All generated content saved and retrievable
- **Mobile OTP Authentication**: Secure user-based sessions

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
    
    Questions --> Results[Results Viewer]
    MockTests --> Results
    Mnemonics --> Results
    CheatSheets --> Results
    Notes --> Results
    
    Results --> Actions{User Action}
    Actions -->|Take Test| TestInterface[Mock Test Interface]
    Actions -->|Download| Export[Export Content]
    Actions -->|New Session| Dashboard
    Actions -->|View History| History[Session History]
    
    TestInterface --> TestResults[Test Results & Analytics]
    TestResults --> Results
    
    History --> SessionDetails[Session Details]
    SessionDetails --> Results
    
    Export --> Download[Download Files]
    Download --> Results
```

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
    User Experience
      Responsive Design
      Drag Drop Upload
      Real Time Progress
      Session History
      Error Handling
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
        API1[/api/v1/auth/*]
        API2[/api/v1/upload/*]
        API3[/api/v1/text-input/*]
        API4[/api/v1/history/*]
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
        
        QuestionGen --> QuestionsReady
        MockTestGen --> MockTestsReady
        MnemonicGen --> MnemonicsReady
        CheatSheetGen --> CheatSheetsReady
        NotesGen --> NotesReady
    }
    
    QuestionsReady --> ResultsCompilation
    MockTestsReady --> ResultsCompilation
    MnemonicsReady --> ResultsCompilation
    CheatSheetsReady --> ResultsCompilation
    NotesReady --> ResultsCompilation
    
    ResultsCompilation --> SessionSaved: Save to database
    SessionSaved --> ResultsDisplay: Display to user
    ResultsDisplay --> [*]: Session complete
```

## 💻 Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js 14, React, TypeScript, TailwindCSS |
| Backend | FastAPI, Python 3.12 |
| Database | MongoDB |
| AI | Google Gemini API |
| Auth | JWT + OTP via Email/SMS |

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

## 🎯 Component Interaction Flow

```mermaid
graph TD
    subgraph "Frontend Components"
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
    
    subgraph "Backend Services"
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
    
    subgraph "External Services"
        AA[Google Gemini]
        BB[OTP Service]
        CC[OCR Engine]
    end
    
    subgraph "Database"
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

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- MongoDB running on `localhost:27017`

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

Open http://localhost:3000

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
└── .kiro/
    ├── steering/          # Project docs (product, tech, structure)
    ├── prompts/           # Custom Kiro commands
    └── documentation/     # Kiro CLI reference
```

## 🔗 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Register with mobile + OTP |
| `/api/v1/auth/login` | POST | Login with mobile + password |
| `/api/v1/upload/` | POST | Upload files for processing |
| `/api/v1/text-input/` | POST | Generate from topic text |
| `/api/v1/history/sessions` | GET | Get user's session history |

## 🛠️ Kiro Development

This project was built using Kiro CLI. Key customizations:

- **Steering docs**: `.kiro/steering/` - Product, tech, and structure specs
- **Custom prompts**: `.kiro/prompts/` - 12 reusable prompts for development
- **Development workflow**: Agentic coding with Kiro's planning and execution modes

## 🎥 Demo

🎥 [Demo Video Link - Coming Soon]

## 👨‍💻 Author

Built for the Dynamous Kiro Hackathon 2026

## 📄 License

MIT
