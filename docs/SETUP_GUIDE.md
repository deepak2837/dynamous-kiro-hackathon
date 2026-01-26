# Study Buddy App - Complete Setup & Deployment Guide

## 🚀 Quick Start Guide

This comprehensive guide covers everything from local development setup to production deployment of the Study Buddy App.

---

## 📋 Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Operating System** | Ubuntu 20.04+ / macOS 10.15+ / Windows 10+ | Ubuntu 22.04 LTS |
| **Node.js** | 18.0+ | 20.0+ LTS |
| **Python** | 3.10+ | 3.12+ |
| **MongoDB** | 6.0+ | 7.0+ |
| **Memory** | 8GB RAM | 16GB RAM |
| **Storage** | 20GB free | 50GB free |
| **Network** | Stable internet | High-speed broadband |

### Required Software Installation

#### 1. Node.js & npm
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS (using Homebrew)
brew install node@20

# Windows (using Chocolatey)
choco install nodejs

# Verify installation
node --version  # Should be 20.x+
npm --version   # Should be 10.x+
```

#### 2. Python & pip
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-pip python3.12-venv

# macOS (using Homebrew)
brew install python@3.12

# Windows (download from python.org)
# Download Python 3.12+ installer and run

# Verify installation
python3 --version  # Should be 3.12+
pip3 --version     # Should be 23.x+
```

#### 3. MongoDB
```bash
# Ubuntu/Debian
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# macOS (using Homebrew)
brew tap mongodb/brew
brew install mongodb-community@7.0

# Start MongoDB service
sudo systemctl start mongod  # Ubuntu
brew services start mongodb/brew/mongodb-community@7.0  # macOS

# Verify installation
mongosh --version  # Should connect successfully
```

#### 4. Git
```bash
# Ubuntu/Debian
sudo apt install git

# macOS (usually pre-installed)
git --version

# Windows (download from git-scm.com)
# Download Git installer and run

# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 🏗️ Development Environment Setup

### 1. Clone Repository
```bash
# Clone the Study Buddy App repository
git clone https://github.com/deepak2837/dynamous-kiro-hackathon.git
cd dynamous-kiro-hackathon

# Verify project structure
ls -la
# Should see: backend/ frontend/ docs/ .kiro/ README.md
```

### 2. Backend Setup

#### Environment Configuration
```bash
cd backend

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi   # Should show FastAPI version
```

#### Environment Variables Setup
```bash
# Create environment file
cp .env.example .env

# Edit environment variables
nano .env  # or use your preferred editor
```

**Required Environment Variables:**
```bash
# Database Configuration
MONGODB_URL=mongodb://localhost:27017/studybuddy
DATABASE_NAME=studybuddy

# AI Service Configuration
GEMINI_API_KEY=your_google_gemini_api_key_here
GOOGLE_CLOUD_PROJECT_ID=your_project_id

# Authentication Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_here_change_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# File Storage Configuration
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=52428800
STORAGE_MODE=LOCAL

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# OTP Configuration
DEFAULT_OTP_METHOD=sms
FAST2SMS_API_KEY=your_fast2sms_api_key

# Security Configuration
ENABLE_RATE_LIMITING=true
ENABLE_UPLOAD_RESTRICTIONS=true
UPLOAD_COOLDOWN_MINUTES=5
```

#### Database Setup
```bash
# Start MongoDB service (if not already running)
sudo systemctl start mongod  # Ubuntu
brew services start mongodb/brew/mongodb-community@7.0  # macOS

# Connect to MongoDB and create database
mongosh
use studybuddy
db.createCollection("users")
db.createCollection("study_sessions")
db.createCollection("questions")
db.createCollection("mock_tests")
db.createCollection("mnemonics")
db.createCollection("cheat_sheets")
db.createCollection("notes")
db.createCollection("flashcards")
exit
```

#### Start Backend Server
```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Verify backend is running
curl http://localhost:8000/health
# Should return: {"status": "healthy", "service": "StudyBuddy", "version": "1.0.0"}
```

### 3. Frontend Setup

#### Install Dependencies
```bash
# Open new terminal and navigate to frontend
cd frontend

# Install Node.js dependencies
npm install

# Verify installation
npm list next  # Should show Next.js version
```

#### Environment Configuration
```bash
# Create environment file
cp .env.local.example .env.local

# Edit environment variables
nano .env.local
```

**Required Frontend Environment Variables:**
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=StudyBuddy

# Authentication Configuration
NEXTAUTH_SECRET=your_nextauth_secret_here
NEXTAUTH_URL=http://localhost:3000

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_DEBUG=true
```

#### Start Frontend Server
```bash
# Development server with hot reload
npm run dev

# Production build and start
npm run build
npm run start

# Verify frontend is running
curl http://localhost:3000
# Should return HTML content
```

### 4. Full Application Verification

#### Health Check Script
```bash
#!/bin/bash
# health_check.sh

echo "🏥 Study Buddy App Health Check"
echo "================================"

# Check MongoDB
echo "📊 Checking MongoDB..."
if mongosh --eval "db.adminCommand('ping')" --quiet; then
    echo "✅ MongoDB: Running"
else
    echo "❌ MongoDB: Not running"
    exit 1
fi

# Check Backend
echo "🔧 Checking Backend API..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Backend API: Running"
else
    echo "❌ Backend API: Not running"
    exit 1
fi

# Check Frontend
echo "🎨 Checking Frontend..."
if curl -s http://localhost:3000 | grep -q "Study Buddy"; then
    echo "✅ Frontend: Running"
else
    echo "❌ Frontend: Not running"
    exit 1
fi

echo "🎉 All services are running successfully!"
echo "📱 Access the app at: http://localhost:3000"
```

```bash
# Make script executable and run
chmod +x health_check.sh
./health_check.sh
```

---

## 🧪 Testing Setup

### Backend Testing
```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_auth.py -v

# Run with coverage
pip install pytest-cov
python -m pytest tests/ --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Frontend Testing
```bash
cd frontend

# Install test dependencies
npm install --save-dev jest @testing-library/react @testing-library/jest-dom

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

---

## 🚀 Production Deployment

### 1. Server Preparation

#### Ubuntu Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y nginx certbot python3-certbot-nginx

# Create application user
sudo useradd -m -s /bin/bash studybuddy
sudo usermod -aG sudo studybuddy

# Switch to application user
sudo su - studybuddy
```

#### Install Production Dependencies
```bash
# Install Node.js (production)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python (production)
sudo apt install python3.12 python3.12-pip python3.12-venv

# Install MongoDB (production)
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Install PM2 for process management
sudo npm install -g pm2
```

### 2. Application Deployment

#### Deploy Backend
```bash
# Clone repository
git clone https://github.com/deepak2837/dynamous-kiro-hackathon.git
cd dynamous-kiro-hackathon/backend

# Create production virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create production environment file
cp .env.example .env
# Edit with production values

# Create PM2 ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'studybuddy-backend',
    script: 'venv/bin/uvicorn',
    args: 'app.main:app --host 0.0.0.0 --port 8000 --workers 4',
    cwd: '/home/studybuddy/dynamous-kiro-hackathon/backend',
    env: {
      NODE_ENV: 'production'
    }
  }]
}
EOF

# Start backend with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

#### Deploy Frontend
```bash
cd ../frontend

# Install dependencies
npm ci --only=production

# Create production environment file
cp .env.local.example .env.local
# Edit with production values

# Build application
npm run build

# Create PM2 config for frontend
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'studybuddy-frontend',
    script: 'npm',
    args: 'start',
    cwd: '/home/studybuddy/dynamous-kiro-hackathon/frontend',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    }
  }]
}
EOF

# Start frontend with PM2
pm2 start ecosystem.config.js
pm2 save
```

### 3. Nginx Configuration

#### Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/studybuddy
```

```nginx
# Study Buddy App Nginx Configuration
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Increase timeout for file uploads
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # File uploads
    client_max_body_size 100M;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript;
}
```

#### Enable Site and SSL
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/studybuddy /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Enable SSL with Let's Encrypt
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal setup
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 4. Database Production Setup

#### MongoDB Production Configuration
```bash
# Create MongoDB configuration
sudo nano /etc/mongod.conf
```

```yaml
# MongoDB Production Configuration
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true

systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

net:
  port: 27017
  bindIp: 127.0.0.1

processManagement:
  timeZoneInfo: /usr/share/zoneinfo

security:
  authorization: enabled

setParameter:
  authenticationMechanisms: SCRAM-SHA-1,SCRAM-SHA-256
```

#### Create Database User
```bash
# Connect to MongoDB
mongosh

# Create admin user
use admin
db.createUser({
  user: "admin",
  pwd: "secure_admin_password",
  roles: ["userAdminAnyDatabase", "dbAdminAnyDatabase", "readWriteAnyDatabase"]
})

# Create application user
use studybuddy
db.createUser({
  user: "studybuddy_user",
  pwd: "secure_app_password",
  roles: ["readWrite"]
})

exit
```

#### Update Application Configuration
```bash
# Update backend .env file
nano /home/studybuddy/dynamous-kiro-hackathon/backend/.env
```

```bash
# Production MongoDB URL
MONGODB_URL=mongodb://studybuddy_user:secure_app_password@localhost:27017/studybuddy
```

### 5. Monitoring and Logging

#### Setup Log Rotation
```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/studybuddy
```

```bash
/home/studybuddy/dynamous-kiro-hackathon/backend/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 studybuddy studybuddy
    postrotate
        pm2 reload studybuddy-backend
    endscript
}
```

#### Setup Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Setup PM2 monitoring
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 30

# Monitor application
pm2 monit
```

---

## 🔧 Configuration Management

### Environment-Specific Configurations

#### Development Configuration
```bash
# backend/.env.development
DEBUG=true
LOG_LEVEL=DEBUG
ENABLE_CORS=true
ALLOWED_ORIGINS=["http://localhost:3000"]
```

#### Production Configuration
```bash
# backend/.env.production
DEBUG=false
LOG_LEVEL=INFO
ENABLE_CORS=false
ALLOWED_ORIGINS=["https://your-domain.com"]
```

### Feature Flags
```bash
# Feature toggles
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_STUDY_PLANNER=true
ENABLE_FLASHCARDS=true
ENABLE_EXPORT_FEATURES=true
ENABLE_ANALYTICS=false
```

---

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Backend Issues
```bash
# Issue: MongoDB connection failed
# Solution: Check MongoDB service and credentials
sudo systemctl status mongod
mongosh -u studybuddy_user -p

# Issue: Import errors
# Solution: Verify virtual environment and dependencies
source venv/bin/activate
pip list | grep fastapi

# Issue: Port already in use
# Solution: Kill process using port
sudo lsof -i :8000
sudo kill -9 <PID>
```

#### Frontend Issues
```bash
# Issue: Build failures
# Solution: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Issue: Environment variables not loaded
# Solution: Check .env.local file
cat .env.local
npm run dev
```

#### Database Issues
```bash
# Issue: Authentication failed
# Solution: Recreate database user
mongosh
use studybuddy
db.dropUser("studybuddy_user")
# Recreate user with correct credentials
```

### Performance Optimization

#### Backend Optimization
```bash
# Use production ASGI server
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Enable database indexing
mongosh studybuddy
db.study_sessions.createIndex({"user_id": 1, "created_at": -1})
db.questions.createIndex({"session_id": 1})
```

#### Frontend Optimization
```bash
# Analyze bundle size
npm install --save-dev @next/bundle-analyzer
npm run analyze

# Enable compression
# Already configured in Nginx
```

---

## 📊 Monitoring and Maintenance

### Health Monitoring
```bash
# Create health check script
cat > /home/studybuddy/health_check.sh << EOF
#!/bin/bash
# Health check for Study Buddy App

# Check backend
if ! curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "Backend unhealthy - restarting"
    pm2 restart studybuddy-backend
fi

# Check frontend
if ! curl -s http://localhost:3000 | grep -q "Study Buddy"; then
    echo "Frontend unhealthy - restarting"
    pm2 restart studybuddy-frontend
fi

# Check MongoDB
if ! mongosh --eval "db.adminCommand('ping')" --quiet; then
    echo "MongoDB unhealthy - restarting"
    sudo systemctl restart mongod
fi
EOF

chmod +x /home/studybuddy/health_check.sh

# Add to crontab
crontab -e
# Add: */5 * * * * /home/studybuddy/health_check.sh
```

### Backup Strategy
```bash
# Create backup script
cat > /home/studybuddy/backup.sh << EOF
#!/bin/bash
BACKUP_DIR="/home/studybuddy/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup MongoDB
mongodump --db studybuddy --out $BACKUP_DIR/mongodb_$DATE

# Backup application files
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /home/studybuddy/dynamous-kiro-hackathon

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /home/studybuddy/backup.sh

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /home/studybuddy/backup.sh
```

---

*This comprehensive setup and deployment guide ensures successful installation and operation of the Study Buddy App in both development and production environments.*
