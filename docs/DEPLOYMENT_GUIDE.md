# Study Buddy App - Deployment Guide

## 🚀 Production Deployment

This guide covers the complete deployment setup for Study Buddy App with frontend on Netlify and backend on AWS with Nginx.

---

## 🏗️ Architecture Overview

```
Internet
    ↓
Netlify (Frontend)
    ↓ HTTPS API calls
Custom Domain (HTTPS)
    ↓
Nginx (Reverse Proxy)
    ↓
AWS EC2 (Backend)
    ↓
MongoDB (Database)
```

---

## 🌐 Frontend Deployment (Netlify)

### Prerequisites
- Netlify account
- GitHub repository access
- Custom domain (optional)

### Deployment Steps

#### 1. Build Configuration
Create `netlify.toml` in project root:
```toml
[build]
  publish = "frontend/out"
  command = "cd frontend && npm run build"

[build.environment]
  NODE_VERSION = "18"
  NEXT_PUBLIC_API_URL = "https://your-domain.com/api"

[[redirects]]
  from = "/api/*"
  to = "https://your-backend-domain.com/api/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

#### 2. Environment Variables
Set in Netlify dashboard:
```env
NEXT_PUBLIC_API_URL=https://your-domain.com/api
NEXT_PUBLIC_APP_NAME=Study Buddy
NEXTAUTH_SECRET=your-production-secret
```

#### 3. Deploy Process
```bash
# Connect GitHub repo to Netlify
# Auto-deploy on push to master
# Custom domain setup in Netlify DNS
```

### Live URL
- **Production**: https://study-material-generator.netlify.app/
- **Custom Domain**: Configure in Netlify settings

---

## ☁️ Backend Deployment (AWS EC2)

### Prerequisites
- AWS account with EC2 access
- Domain name for SSL
- SSH key pair

### Server Setup

#### 1. Launch EC2 Instance
```bash
# Ubuntu 22.04 LTS
# t3.medium (2 vCPU, 4GB RAM)
# Security groups: HTTP (80), HTTPS (443), SSH (22)
```

#### 2. Initial Server Configuration
```bash
# Connect to instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nginx mongodb certbot python3-certbot-nginx
```

#### 3. Application Setup
```bash
# Clone repository
git clone https://github.com/your-username/dynamous-kiro-hackathon.git
cd dynamous-kiro-hackathon/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create production environment file
sudo nano /etc/environment
```

#### 4. Environment Configuration
```env
# /etc/environment
MONGODB_URL=mongodb://localhost:27017/studybuddy_prod
DATABASE_NAME=studybuddy_prod
GOOGLE_AI_API_KEY=your-production-api-key
JWT_SECRET=your-production-jwt-secret
UPLOAD_DIR=/var/www/studybuddy/uploads
HOST=127.0.0.1
PORT=8000
DEBUG=False
```

#### 5. MongoDB Setup
```bash
# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Create production database
mongosh
use studybuddy_prod
db.createUser({
  user: "studybuddy",
  pwd: "secure-password",
  roles: ["readWrite"]
})
```

---

## 🔧 Nginx Configuration

### 1. Create Nginx Config
```bash
sudo nano /etc/nginx/sites-available/studybuddy
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # API routes
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Handle large file uploads
        client_max_body_size 100M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # Static files
    location /uploads/ {
        alias /var/www/studybuddy/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }
}
```

### 2. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/studybuddy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔒 SSL Certificate Setup

### 1. Install Certbot SSL
```bash
# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Verify SSL
```bash
# Test SSL configuration
curl -I https://your-domain.com/api/health
```

---

## 🔄 Process Management

### 1. Create Systemd Service
```bash
sudo nano /etc/systemd/system/studybuddy.service
```

```ini
[Unit]
Description=Study Buddy FastAPI App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/dynamous-kiro-hackathon/backend
Environment=PATH=/home/ubuntu/dynamous-kiro-hackathon/backend/venv/bin
ExecStart=/home/ubuntu/dynamous-kiro-hackathon/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 2. Start Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable studybuddy
sudo systemctl start studybuddy
sudo systemctl status studybuddy
```

---

## 📊 Monitoring & Logging

### 1. Application Logs
```bash
# View application logs
sudo journalctl -u studybuddy -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. System Monitoring
```bash
# Install monitoring tools
sudo apt install -y htop iotop

# Monitor resources
htop
df -h
free -h
```

---

## 🔧 Maintenance

### 1. Application Updates
```bash
# Update application
cd /home/ubuntu/dynamous-kiro-hackathon
git pull origin master
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart studybuddy
```

### 2. Database Backup
```bash
# Create backup script
sudo nano /usr/local/bin/backup-studybuddy.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mongodump --db studybuddy_prod --out /backup/studybuddy_$DATE
tar -czf /backup/studybuddy_$DATE.tar.gz /backup/studybuddy_$DATE
rm -rf /backup/studybuddy_$DATE
find /backup -name "studybuddy_*.tar.gz" -mtime +7 -delete
```

### 3. Log Rotation
```bash
sudo nano /etc/logrotate.d/studybuddy
```

```
/var/log/studybuddy/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        systemctl reload studybuddy
    endscript
}
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew --dry-run
```

#### 2. Application Not Starting
```bash
# Check service status
sudo systemctl status studybuddy

# Check logs
sudo journalctl -u studybuddy --no-pager -l
```

#### 3. Database Connection Issues
```bash
# Check MongoDB status
sudo systemctl status mongod

# Test connection
mongosh --eval "db.adminCommand('ismaster')"
```

#### 4. File Upload Issues
```bash
# Check upload directory permissions
ls -la /var/www/studybuddy/uploads/
sudo chown -R ubuntu:ubuntu /var/www/studybuddy/uploads/
sudo chmod -R 755 /var/www/studybuddy/uploads/
```

---

## 📈 Performance Optimization

### 1. Nginx Optimization
```nginx
# Add to nginx.conf
worker_processes auto;
worker_connections 1024;

# Enable gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript;
```

### 2. Application Optimization
```bash
# Use multiple workers
ExecStart=.../uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4

# Enable Redis for caching
sudo apt install redis-server
sudo systemctl enable redis-server
```

---

## 🔐 Security Checklist

- ✅ SSL/TLS encryption enabled
- ✅ Security headers configured
- ✅ Firewall rules applied
- ✅ Regular security updates
- ✅ Strong passwords and keys
- ✅ File upload restrictions
- ✅ Rate limiting enabled
- ✅ Database access restricted

---

## 📞 Support

For deployment issues:
1. Check application logs
2. Verify SSL certificates
3. Test database connectivity
4. Monitor system resources
5. Contact system administrator

---

*Deployment Guide - Study Buddy App v1.0.0*
