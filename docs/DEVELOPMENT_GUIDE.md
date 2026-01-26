# Study Buddy App - Development Guide

## 👨‍💻 Developer Onboarding & Workflows

Complete guide for developers working on Study Buddy App - from setup to deployment.

---

## 🚀 Quick Start

### Prerequisites
```bash
# Required software versions
Node.js >= 18.0.0
Python >= 3.10
MongoDB >= 6.0
Git >= 2.30
```

### Initial Setup
```bash
# 1. Clone repository
git clone https://github.com/your-username/dynamous-kiro-hackathon.git
cd dynamous-kiro-hackathon

# 2. Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your values

# 3. Setup frontend
cd ../frontend
npm install
cp .env.local.example .env.local  # Edit with your values

# 4. Start services
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload

# Terminal 2: Frontend  
cd frontend && npm run dev

# Terminal 3: MongoDB
mongod

# Access: http://localhost:3000
```

---

## 🏗️ Project Architecture

### Directory Structure
```
dynamous-kiro-hackathon/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── api/            # API route handlers
│   │   ├── services/       # Business logic
│   │   ├── models/         # Database models
│   │   ├── utils/          # Utility functions
│   │   └── main.py         # FastAPI app entry
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # Next.js React frontend
│   ├── src/
│   │   ├── app/           # Next.js app router
│   │   ├── components/    # React components
│   │   ├── lib/           # Utility libraries
│   │   ├── types/         # TypeScript types
│   │   └── contexts/      # React contexts
│   ├── public/            # Static assets
│   └── package.json       # Node dependencies
│
├── docs/                  # Documentation
├── .kiro/                 # Kiro CLI configuration
└── README.md              # Project overview
```

### Technology Stack
```
Frontend:  Next.js 14 + React 18 + TypeScript + TailwindCSS
Backend:   FastAPI + Python 3.10 + Motor (async MongoDB)
Database:  MongoDB 6.0
AI:        Google Gemini API
Auth:      JWT + OTP verification
Deployment: Netlify (frontend) + AWS EC2 (backend)
```

---

## 🔧 Development Workflow

### Git Workflow
```bash
# 1. Create feature branch
git checkout -b feature/new-feature-name

# 2. Make changes and commit
git add .
git commit -m "feat: add new feature description"

# 3. Push and create PR
git push origin feature/new-feature-name
# Create Pull Request on GitHub

# 4. After review, merge to main
git checkout main
git pull origin main
git branch -d feature/new-feature-name
```

### Commit Message Convention
```
feat: add new feature
fix: bug fix
docs: documentation changes
style: formatting changes
refactor: code refactoring
test: add or update tests
chore: maintenance tasks

Examples:
feat: add flashcard spaced repetition algorithm
fix: resolve file upload timeout issue
docs: update API documentation for mock tests
```

### Code Review Process
1. **Self-review** - Check your own code first
2. **Automated checks** - Ensure tests pass
3. **Peer review** - At least one team member review
4. **Documentation** - Update docs if needed
5. **Testing** - Manual testing in development environment

---

## 🧪 Testing Strategy

### Backend Testing
```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_upload.py

# Run with verbose output
pytest -v
```

### Frontend Testing
```bash
# Run all tests
cd frontend
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

### Test Structure
```python
# Backend test example
# tests/test_upload.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_pdf_file():
    """Test PDF file upload functionality."""
    with open("test_files/sample.pdf", "rb") as f:
        response = client.post(
            "/api/v1/upload",
            files={"files": ("sample.pdf", f, "application/pdf")},
            headers={"Authorization": "Bearer test_token"}
        )
    
    assert response.status_code == 200
    assert "session_id" in response.json()
```

```typescript
// Frontend test example
// src/components/__tests__/FileUpload.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import FileUpload from '../FileUpload'

describe('FileUpload Component', () => {
  test('renders upload interface', () => {
    render(<FileUpload />)
    expect(screen.getByText('Upload Files')).toBeInTheDocument()
  })

  test('handles file selection', () => {
    render(<FileUpload />)
    const fileInput = screen.getByLabelText('file-input')
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })
    
    fireEvent.change(fileInput, { target: { files: [file] } })
    expect(screen.getByText('test.pdf')).toBeInTheDocument()
  })
})
```

---

## 🔍 Code Quality Standards

### Python Code Style
```python
# Use Black for formatting
black app/

# Use isort for imports
isort app/

# Use flake8 for linting
flake8 app/

# Use mypy for type checking
mypy app/
```

### TypeScript Code Style
```bash
# Use Prettier for formatting
npx prettier --write src/

# Use ESLint for linting
npx eslint src/

# Type checking
npx tsc --noEmit
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.0-alpha.4
    hooks:
      - id: prettier
        files: \.(js|ts|tsx|json|css|md)$
```

---

## 🐛 Debugging Guide

### Backend Debugging
```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debugger
import pdb; pdb.set_trace()

# FastAPI debug mode
uvicorn app.main:app --reload --log-level debug

# Check logs
tail -f logs/studybuddy.log
```

### Frontend Debugging
```typescript
// Browser DevTools
console.log('Debug info:', data)
console.table(arrayData)
debugger; // Breakpoint

// React DevTools
// Install React Developer Tools browser extension

// Next.js debugging
// Set DEBUG=* in environment
```

### Database Debugging
```javascript
// MongoDB shell debugging
db.setLogLevel(2) // Enable query logging

// Explain query performance
db.study_sessions.find({user_id: ObjectId("...")}).explain("executionStats")

// Check slow queries
db.setProfilingLevel(2, { slowms: 100 })
db.system.profile.find().sort({ts: -1}).limit(5)
```

---

## 📦 Dependency Management

### Backend Dependencies
```bash
# Add new dependency
pip install package-name
pip freeze > requirements.txt

# Development dependencies
pip install -r requirements-dev.txt

# Security audit
pip-audit

# Update dependencies
pip-review --local --interactive
```

### Frontend Dependencies
```bash
# Add new dependency
npm install package-name

# Add dev dependency
npm install --save-dev package-name

# Security audit
npm audit
npm audit fix

# Update dependencies
npm update
npx npm-check-updates -u
```

---

## 🚀 Deployment Process

### Development Deployment
```bash
# Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build
npm start
```

### Production Deployment

#### Backend (AWS EC2)
```bash
# 1. Setup server
ssh -i key.pem ubuntu@your-server-ip

# 2. Clone and setup
git clone https://github.com/your-repo.git
cd dynamous-kiro-hackathon/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure systemd service
sudo cp studybuddy.service /etc/systemd/system/
sudo systemctl enable studybuddy
sudo systemctl start studybuddy

# 4. Setup Nginx
sudo cp nginx.conf /etc/nginx/sites-available/studybuddy
sudo ln -s /etc/nginx/sites-available/studybuddy /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

#### Frontend (Netlify)
```bash
# 1. Build configuration
# netlify.toml already configured

# 2. Environment variables
# Set in Netlify dashboard

# 3. Deploy
git push origin main
# Auto-deploys via Netlify GitHub integration
```

---

## 🔧 Environment Configuration

### Development Environment
```bash
# Backend .env
DEBUG=true
LOG_LEVEL=DEBUG
MONGODB_URL=mongodb://localhost:27017/studybuddy_dev
GOOGLE_AI_API_KEY=your-dev-api-key

# Frontend .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Study Buddy (Dev)
```

### Production Environment
```bash
# Backend .env
DEBUG=false
LOG_LEVEL=WARNING
MONGODB_URL=mongodb://localhost:27017/studybuddy_prod
GOOGLE_AI_API_KEY=your-prod-api-key

# Frontend .env.production
NEXT_PUBLIC_API_URL=https://your-domain.com/api
NEXT_PUBLIC_APP_NAME=Study Buddy
```

---

## 📊 Performance Optimization

### Backend Optimization
```python
# Database query optimization
# Use indexes for frequent queries
await collection.create_index([("user_id", 1), ("created_at", -1)])

# Async operations
async def process_multiple_files(files):
    tasks = [process_file(file) for file in files]
    return await asyncio.gather(*tasks)

# Caching
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(data):
    return result
```

### Frontend Optimization
```typescript
// Code splitting
const LazyComponent = lazy(() => import('./HeavyComponent'))

// Memoization
const MemoizedComponent = memo(({ data }) => {
  return <div>{data}</div>
})

// Image optimization
import Image from 'next/image'
<Image src="/image.jpg" alt="Description" width={500} height={300} />
```

---

## 🔒 Security Best Practices

### Backend Security
```python
# Input validation
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    mobile: str
    
    @validator('mobile')
    def validate_mobile(cls, v):
        if not re.match(r'^[0-9]{10}$', v):
            raise ValueError('Invalid mobile number')
        return v

# SQL injection prevention (MongoDB)
# Use parameterized queries
await collection.find({"user_id": ObjectId(user_id)})

# Rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@limiter.limit("5/minute")
async def sensitive_endpoint():
    pass
```

### Frontend Security
```typescript
// XSS prevention
import DOMPurify from 'dompurify'
const cleanHTML = DOMPurify.sanitize(userInput)

// CSRF protection
// Next.js handles this automatically with SameSite cookies

// Secure API calls
const response = await fetch('/api/endpoint', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
```

---

## 📚 Learning Resources

### Documentation
- **FastAPI**: https://fastapi.tiangolo.com/
- **Next.js**: https://nextjs.org/docs
- **MongoDB**: https://docs.mongodb.com/
- **React**: https://react.dev/

### Medical Education Context
- **MBBS Curriculum**: Understanding Indian medical education
- **Medical Terminology**: Proper medical language usage
- **Exam Patterns**: NEET, AIIMS, state medical exams

### AI/ML Resources
- **Google Gemini**: https://ai.google.dev/docs
- **Prompt Engineering**: Best practices for medical content
- **Content Generation**: Techniques for educational material

---

## 🤝 Contributing Guidelines

### Getting Started
1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** for your changes
4. **Make your changes** following code standards
5. **Write tests** for new functionality
6. **Update documentation** as needed
7. **Submit a pull request** with clear description

### Code Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact considered
- [ ] Medical accuracy verified (for content features)

### Issue Reporting
```markdown
## Bug Report Template
**Description**: Brief description of the issue
**Steps to Reproduce**: 
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**: What should happen
**Actual Behavior**: What actually happens
**Environment**: OS, browser, versions
**Screenshots**: If applicable
```

---

## 📞 Support & Communication

### Development Team
- **Lead Developer**: Contact for architecture decisions
- **Frontend Team**: React/Next.js related issues
- **Backend Team**: FastAPI/Python related issues
- **DevOps Team**: Deployment and infrastructure

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **Pull Requests**: Code review and discussion
- **Documentation**: Updates and improvements
- **Team Meetings**: Weekly sync and planning

---

*Development Guide - Study Buddy App v1.0.0*
