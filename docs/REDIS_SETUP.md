# Redis Installation and Setup Guide

## 🚀 Redis Setup (Optional)

Redis is configured but disabled by default. Follow these steps to enable caching.

### Installation

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS
```bash
brew install redis
brew services start redis
```

#### Windows (WSL)
```bash
# Install in WSL Ubuntu
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

### Configuration

#### 1. Enable Redis in Environment
```bash
# Edit backend/.env
ENABLE_REDIS_CACHE=true
REDIS_URL=redis://localhost:6379
```

#### 2. Install Python Dependencies
```bash
cd backend
pip install redis==5.0.1
```

#### 3. Verify Redis Connection
```bash
redis-cli ping
# Should return: PONG
```

### Features Enabled with Redis

- **Session Caching**: Faster session retrieval
- **AI Response Caching**: Avoid regenerating same content
- **User Data Caching**: Improved performance for user sessions
- **Rate Limiting**: Enhanced rate limiting with Redis backend

### Production Configuration

```bash
# Production Redis settings
REDIS_URL=redis://your-redis-server:6379
REDIS_PASSWORD=your-secure-password
REDIS_DB=0
REDIS_TIMEOUT=5
```

### Monitoring Redis

```bash
# Check Redis status
redis-cli info

# Monitor Redis commands
redis-cli monitor

# Check memory usage
redis-cli info memory
```

### Disable Redis

To disable Redis caching:
```bash
# Set in .env
ENABLE_REDIS_CACHE=false
```

Application will work normally without Redis - all caching will be bypassed gracefully.
