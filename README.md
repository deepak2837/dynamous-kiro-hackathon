# Study Buddy - AI-Powered Study Companion

> 🏆 **Kiro Hackathon Submission** (January 5-30, 2026)

An AI-powered study companion for medical students that transforms study materials into actionable resources including question banks, mock tests, mnemonics, cheat sheets, and compiled notes.

## Features

- **Multi-Format Upload**: PDF documents, images, scanned notes
- **Topic-Based Generation**: Enter any topic to generate study materials
- **5 Output Types**: Questions, Mock Tests, Mnemonics, Cheat Sheets, Notes
- **Session History**: All generated content saved and retrievable
- **Mobile OTP Authentication**: Secure user-based sessions

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js 14, React, TypeScript, TailwindCSS |
| Backend | FastAPI, Python 3.12 |
| Database | MongoDB |
| AI | Google Gemini API |
| Auth | JWT + OTP via Email/SMS |

## Quick Start

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

## Project Structure

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

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Register with mobile + OTP |
| `/api/v1/auth/login` | POST | Login with mobile + password |
| `/api/v1/upload/` | POST | Upload files for processing |
| `/api/v1/text-input/` | POST | Generate from topic text |
| `/api/v1/history/sessions` | GET | Get user's session history |

## Kiro Development

This project was built using Kiro CLI. Key customizations:

- **Steering docs**: `.kiro/steering/` - Product, tech, and structure specs
- **Custom prompts**: `.kiro/prompts/` - 12 reusable prompts for development
- **Development workflow**: Agentic coding with Kiro's planning and execution modes

## Demo

🎥 [Demo Video Link - Coming Soon]

## Author

Built for the Dynamous Kiro Hackathon 2026

## License

MIT
