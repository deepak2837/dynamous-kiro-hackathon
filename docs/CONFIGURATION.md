# Study Buddy App - Configuration Reference

## ⚙️ Configuration Management

Complete reference for all configuration options, environment variables, and settings for Study Buddy App.

---

## 📁 Configuration Files

### Frontend Configuration

#### `frontend/.env.local`
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Study Buddy

# Authentication
NEXTAUTH_SECRET=your-nextauth-secret-here
NEXTAUTH_URL=http://localhost:3000

# Feature Flags
NEXT_PUBLIC_ENABLE_MOCK_TESTS=true
NEXT_PUBLIC_ENABLE_FLASHCARDS=true
NEXT_PUBLIC_ENABLE_STUDY_PLANNER=true

# File Upload Limits
NEXT_PUBLIC_MAX_FILE_SIZE=52428800
NEXT_PUBLIC_MAX_FILES_PER_UPLOAD=10
NEXT_PUBLIC_ALLOWED_FILE_TYPES=pdf,jpg,jpeg,png,pptx

# UI Configuration
NEXT_PUBLIC_THEME=light
NEXT_PUBLIC_LANGUAGE=en
```

#### `frontend/next.config.js`
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['localhost', 'your-domain.com'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
      },
    ]
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
```

### Backend Configuration

#### `backend/.env`
```env
# Database Configuration
MONGODB_URL=mongodb://localhost:27017/studybuddy
DATABASE_NAME=studybuddy
MONGODB_MIN_POOL_SIZE=5
MONGODB_MAX_POOL_SIZE=50

# AI Service Configuration
GOOGLE_AI_API_KEY=your-google-ai-api-key
GENAI_PROJECT_ID=your-project-id
GENAI_MODEL=gemini-1.5-pro
GENAI_TEMPERATURE=0.7
GENAI_MAX_TOKENS=8192

# Authentication Configuration
JWT_SECRET=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24
JWT_REFRESH_EXPIRY_DAYS=30

# OTP Configuration
OTP_EXPIRY_MINUTES=5
OTP_LENGTH=6
OTP_SERVICE_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# File Storage Configuration
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=52428800
MAX_FILES_PER_UPLOAD=10
ALLOWED_FILE_TYPES=pdf,jpg,jpeg,png,pptx
FILE_CLEANUP_DAYS=90

# OCR Configuration
OCR_SCRIPTS_PATH=/home/unknown/Documents/medgloss-data-extractorfiles
OCR_TIMEOUT_SECONDS=300
OCR_MAX_RETRIES=3

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
RELOAD=true
WORKERS=1

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=20

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=./logs/studybuddy.log
LOG_ROTATION=daily
LOG_RETENTION_DAYS=30

# Email Configuration (Optional)
ENABLE_EMAIL_NOTIFICATIONS=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=studybuddy@yourapp.com

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_TIMEOUT=5

# Monitoring Configuration
ENABLE_METRICS=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30

# Security Configuration
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
CORS_CREDENTIALS=true
TRUSTED_HOSTS=localhost,127.0.0.1,your-domain.com
```

---

## 🏗️ Production Configuration

### Production Environment Variables

#### Frontend Production (`.env.production`)
```env
NEXT_PUBLIC_API_URL=https://your-domain.com/api
NEXT_PUBLIC_APP_NAME=Study Buddy
NEXTAUTH_SECRET=production-secret-key
NEXTAUTH_URL=https://study-material-generator.netlify.app
NODE_ENV=production
```

#### Backend Production (`.env.production`)
```env
# Database
MONGODB_URL=mongodb://localhost:27017/studybuddy_prod
DATABASE_NAME=studybuddy_prod

# Security
DEBUG=false
JWT_SECRET=production-jwt-secret-key
CORS_ORIGINS=https://study-material-generator.netlify.app

# Performance
WORKERS=4
RELOAD=false

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/studybuddy/app.log

# File Storage
UPLOAD_DIR=/var/www/studybuddy/uploads
```

---

## 🔧 Application Settings

### AI Processing Configuration

#### Question Generation Settings
```python
# backend/app/config.py
QUESTION_GENERATION = {
    "default_count": 25,
    "max_count": 50,
    "min_count": 5,
    "difficulty_distribution": {
        "easy": 0.3,
        "medium": 0.5,
        "hard": 0.2
    },
    "subjects": [
        "Anatomy", "Physiology", "Biochemistry", 
        "Pathology", "Pharmacology", "Microbiology",
        "Medicine", "Surgery", "Pediatrics", "Gynecology"
    ],
    "bloom_taxonomy": [
        "Remember", "Understand", "Apply", 
        "Analyze", "Evaluate", "Create"
    ]
}
```

#### Mock Test Configuration
```python
MOCK_TEST_CONFIG = {
    "default_duration": 60,  # minutes
    "questions_per_test": 25,
    "auto_submit": True,
    "show_results_immediately": True,
    "allow_review": True,
    "randomize_questions": True,
    "randomize_options": True
}
```

#### Flashcard Configuration
```python
FLASHCARD_CONFIG = {
    "spaced_repetition": {
        "algorithm": "SM2",
        "initial_interval": 1,  # days
        "initial_ease": 2.5,
        "min_ease": 1.3,
        "max_ease": 5.0
    },
    "review_limits": {
        "new_cards_per_day": 20,
        "review_cards_per_day": 100,
        "max_review_time": 30  # minutes
    }
}
```

### File Processing Configuration

#### Upload Restrictions
```python
FILE_CONFIG = {
    "max_file_size": 52428800,  # 50MB
    "max_files_per_upload": 10,
    "allowed_extensions": [".pdf", ".jpg", ".jpeg", ".png", ".pptx"],
    "allowed_mime_types": [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    ],
    "virus_scan": False,  # Enable in production
    "auto_cleanup_days": 90
}
```

#### OCR Processing
```python
OCR_CONFIG = {
    "default_language": "eng",
    "supported_languages": ["eng", "hin"],
    "confidence_threshold": 60,
    "preprocessing": {
        "deskew": True,
        "denoise": True,
        "enhance_contrast": True
    },
    "timeout_seconds": 300,
    "max_retries": 3
}
```

---

## 🔒 Security Configuration

### Authentication Settings
```python
AUTH_CONFIG = {
    "jwt": {
        "secret_key": "your-secret-key",
        "algorithm": "HS256",
        "access_token_expire_minutes": 1440,  # 24 hours
        "refresh_token_expire_days": 30
    },
    "password": {
        "min_length": 8,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_special_chars": False
    },
    "otp": {
        "length": 6,
        "expiry_minutes": 5,
        "max_attempts": 3,
        "cooldown_minutes": 1
    }
}
```

### CORS Configuration
```python
CORS_CONFIG = {
    "allow_origins": [
        "http://localhost:3000",
        "https://study-material-generator.netlify.app"
    ],
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["*"],
    "expose_headers": ["X-Total-Count"]
}
```

### Rate Limiting
```python
RATE_LIMIT_CONFIG = {
    "default": "100/minute",
    "upload": "10/minute",
    "auth": "5/minute",
    "ai_processing": "20/hour",
    "download": "50/minute"
}
```

---

## 📊 Monitoring Configuration

### Logging Configuration
```python
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "json": {
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/studybuddy.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "json",
            "level": "INFO"
        }
    },
    "loggers": {
        "studybuddy": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        }
    }
}
```

### Health Check Configuration
```python
HEALTH_CHECK_CONFIG = {
    "enabled": True,
    "endpoint": "/health",
    "checks": {
        "database": True,
        "ai_service": True,
        "file_storage": True,
        "redis": False  # Optional
    },
    "timeout_seconds": 5,
    "cache_ttl": 30
}
```

---

## 🎛️ Feature Flags

### Frontend Feature Flags
```typescript
// frontend/src/lib/config.ts
export const FEATURE_FLAGS = {
  ENABLE_MOCK_TESTS: process.env.NEXT_PUBLIC_ENABLE_MOCK_TESTS === 'true',
  ENABLE_FLASHCARDS: process.env.NEXT_PUBLIC_ENABLE_FLASHCARDS === 'true',
  ENABLE_STUDY_PLANNER: process.env.NEXT_PUBLIC_ENABLE_STUDY_PLANNER === 'true',
  ENABLE_DARK_MODE: process.env.NEXT_PUBLIC_ENABLE_DARK_MODE === 'true',
  ENABLE_ANALYTICS: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === 'true',
  ENABLE_NOTIFICATIONS: process.env.NEXT_PUBLIC_ENABLE_NOTIFICATIONS === 'true'
}
```

### Backend Feature Flags
```python
# backend/app/config.py
FEATURE_FLAGS = {
    "ENABLE_EMAIL_NOTIFICATIONS": os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "false").lower() == "true",
    "ENABLE_REDIS_CACHE": os.getenv("ENABLE_REDIS_CACHE", "false").lower() == "true",
    "ENABLE_METRICS": os.getenv("ENABLE_METRICS", "true").lower() == "true",
    "ENABLE_AI_CONTENT_FILTER": os.getenv("ENABLE_AI_CONTENT_FILTER", "true").lower() == "true",
    "ENABLE_FILE_VIRUS_SCAN": os.getenv("ENABLE_FILE_VIRUS_SCAN", "false").lower() == "true"
}
```

---

## 🔄 Environment-Specific Configurations

### Development Environment
```bash
# Quick development setup
export NODE_ENV=development
export DEBUG=true
export LOG_LEVEL=DEBUG
export RELOAD=true
export WORKERS=1
```

### Testing Environment
```bash
# Testing configuration
export NODE_ENV=test
export DATABASE_NAME=studybuddy_test
export JWT_SECRET=test-secret
export UPLOAD_DIR=./test_uploads
export LOG_LEVEL=ERROR
```

### Production Environment
```bash
# Production optimization
export NODE_ENV=production
export DEBUG=false
export LOG_LEVEL=WARNING
export WORKERS=4
export RELOAD=false
export ENABLE_METRICS=true
```

---

## 📋 Configuration Validation

### Environment Variable Validation
```python
# backend/app/config.py
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    mongodb_url: str
    jwt_secret: str
    google_ai_api_key: str
    
    @validator('jwt_secret')
    def jwt_secret_must_be_strong(cls, v):
        if len(v) < 32:
            raise ValueError('JWT secret must be at least 32 characters')
        return v
    
    @validator('mongodb_url')
    def mongodb_url_must_be_valid(cls, v):
        if not v.startswith('mongodb://'):
            raise ValueError('Invalid MongoDB URL')
        return v
    
    class Config:
        env_file = ".env"
```

### Configuration Checklist

#### Development Checklist
- ✅ MongoDB running locally
- ✅ Environment variables set
- ✅ API keys configured
- ✅ File upload directory exists
- ✅ OCR scripts accessible

#### Production Checklist
- ✅ Strong JWT secret (32+ characters)
- ✅ Production database configured
- ✅ HTTPS enabled
- ✅ CORS origins restricted
- ✅ File upload limits set
- ✅ Logging configured
- ✅ Monitoring enabled
- ✅ Backup strategy in place

---

## 🛠️ Configuration Management Tools

### Environment Variable Management
```bash
# Use direnv for automatic environment loading
echo "export MONGODB_URL=mongodb://localhost:27017/studybuddy" >> .envrc
echo "export JWT_SECRET=your-secret-key" >> .envrc
direnv allow
```

### Configuration Validation Script
```bash
#!/bin/bash
# scripts/validate-config.sh

echo "Validating configuration..."

# Check required environment variables
required_vars=("MONGODB_URL" "JWT_SECRET" "GOOGLE_AI_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing required variable: $var"
        exit 1
    else
        echo "✅ $var is set"
    fi
done

# Test database connection
python -c "
import pymongo
import os
try:
    client = pymongo.MongoClient(os.getenv('MONGODB_URL'))
    client.admin.command('ismaster')
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

echo "✅ Configuration validation complete"
```

---

*Configuration Reference - Study Buddy App v1.0.0*
