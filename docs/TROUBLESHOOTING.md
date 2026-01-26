# Study Buddy App - Troubleshooting Guide

## 🔧 Common Issues & Solutions

Comprehensive troubleshooting guide for Study Buddy App users, developers, and administrators.

---

## 🚨 User Issues

### File Upload Problems

#### Issue: "File upload failed"
**Symptoms:**
- Upload progress bar stops
- Error message appears
- Files not processing

**Solutions:**
1. **Check file size** - Maximum 50MB per file
   ```
   ✅ Compress large PDFs using online tools
   ✅ Split large files into smaller parts
   ✅ Use image compression for photos
   ```

2. **Verify file format** - Only PDF, JPG, PNG, PPTX allowed
   ```
   ❌ DOC, DOCX files not supported
   ❌ TXT files not supported  
   ❌ Video files not supported
   ✅ Convert to PDF format first
   ```

3. **Check internet connection**
   ```bash
   # Test connection speed
   speedtest-cli
   
   # Check if API is accessible
   curl -I https://your-domain.com/api/health
   ```

#### Issue: "Processing stuck at 0%"
**Symptoms:**
- Upload completes but processing doesn't start
- Progress bar remains at 0%
- No error messages

**Solutions:**
1. **Refresh the page** and check session history
2. **Wait 2-3 minutes** - Large files take time to process
3. **Try uploading again** with smaller files
4. **Clear browser cache** and cookies
5. **Contact support** if issue persists

### Authentication Issues

#### Issue: "OTP not received"
**Symptoms:**
- Mobile number entered correctly
- No SMS received after 5 minutes
- Cannot proceed with login

**Solutions:**
1. **Check mobile number format**
   ```
   ✅ Correct: 9876543210
   ❌ Wrong: +91-9876543210
   ❌ Wrong: 09876543210
   ```

2. **Wait and retry**
   - Wait 2-3 minutes before requesting new OTP
   - Check spam/promotional SMS folder
   - Ensure good network coverage

3. **Alternative login methods**
   - Use password login if account exists
   - Contact admin for manual verification

#### Issue: "Invalid credentials"
**Symptoms:**
- Correct mobile number and password
- Login fails with error message
- Account exists but cannot access

**Solutions:**
1. **Reset password** using forgot password option
2. **Check for typos** in mobile number
3. **Clear browser data** and try again
4. **Contact support** for account verification

### Content Generation Issues

#### Issue: "No questions generated"
**Symptoms:**
- Processing completes successfully
- Questions tab shows empty
- Other content types may be available

**Solutions:**
1. **Check source content quality**
   ```
   ✅ Text-heavy documents work best
   ❌ Image-only files may not generate questions
   ✅ Use OCR mode for scanned documents
   ```

2. **Try different processing mode**
   - Switch from Default to OCR mode
   - Use AI-based mode for complex content

3. **Upload additional content**
   - Combine multiple files in one session
   - Add more detailed source material

#### Issue: "Poor quality questions"
**Symptoms:**
- Questions don't make sense
- Incorrect answers marked as correct
- Irrelevant content in questions

**Solutions:**
1. **Improve source material quality**
   - Use high-resolution scans
   - Ensure text is clearly readable
   - Avoid handwritten notes with poor legibility

2. **Use appropriate processing mode**
   - OCR mode for scanned documents
   - AI-based mode for complex layouts

3. **Provide feedback** to improve AI model

### Mock Test Issues

#### Issue: "Test not loading"
**Symptoms:**
- Mock test page shows loading spinner
- Questions don't appear
- Browser becomes unresponsive

**Solutions:**
1. **Check browser compatibility**
   ```
   ✅ Chrome 90+
   ✅ Firefox 88+
   ✅ Safari 14+
   ✅ Edge 90+
   ```

2. **Clear browser cache**
   ```bash
   # Chrome: Ctrl+Shift+Delete
   # Firefox: Ctrl+Shift+Delete
   # Safari: Cmd+Option+E
   ```

3. **Disable browser extensions**
   - Ad blockers may interfere
   - Privacy extensions may block content

#### Issue: "Timer not working"
**Symptoms:**
- Test starts but timer doesn't count down
- Time remaining shows incorrect values
- Auto-submit doesn't work

**Solutions:**
1. **Enable JavaScript** in browser settings
2. **Check system clock** - Ensure correct time/timezone
3. **Refresh page** and restart test
4. **Use different browser** as fallback

---

## 💻 Technical Issues

### Performance Problems

#### Issue: "Slow loading times"
**Symptoms:**
- Pages take >10 seconds to load
- Images and content load slowly
- Frequent timeouts

**Solutions:**
1. **Check internet speed**
   ```bash
   # Minimum recommended: 5 Mbps
   speedtest-cli
   ```

2. **Clear browser data**
   - Cache, cookies, local storage
   - Browser history if needed

3. **Optimize browser**
   - Close unnecessary tabs
   - Disable heavy extensions
   - Update to latest version

4. **Server-side optimization** (for admins)
   ```bash
   # Check server resources
   htop
   df -h
   free -h
   
   # Restart services if needed
   sudo systemctl restart studybuddy
   sudo systemctl restart nginx
   ```

#### Issue: "Memory usage high"
**Symptoms:**
- Browser becomes slow
- System freezes during use
- Out of memory errors

**Solutions:**
1. **Close other applications**
2. **Restart browser** periodically
3. **Increase system RAM** if possible
4. **Use mobile app** for lighter experience

### Browser Compatibility

#### Issue: "Features not working in older browsers"
**Symptoms:**
- Upload doesn't work
- Modern UI elements missing
- JavaScript errors in console

**Solutions:**
1. **Update browser** to latest version
   ```
   Minimum Requirements:
   - Chrome 90+
   - Firefox 88+
   - Safari 14+
   - Edge 90+
   ```

2. **Enable JavaScript** and cookies
3. **Disable compatibility mode** in IE/Edge
4. **Use alternative browser** if update not possible

---

## 🔧 Developer Issues

### Setup Problems

#### Issue: "MongoDB connection failed"
**Symptoms:**
```
pymongo.errors.ServerSelectionTimeoutError
Connection refused on port 27017
```

**Solutions:**
1. **Start MongoDB service**
   ```bash
   # Ubuntu/Debian
   sudo systemctl start mongod
   sudo systemctl enable mongod
   
   # macOS
   brew services start mongodb-community
   
   # Windows
   net start MongoDB
   ```

2. **Check MongoDB status**
   ```bash
   sudo systemctl status mongod
   mongosh --eval "db.adminCommand('ismaster')"
   ```

3. **Verify connection string**
   ```python
   # Check .env file
   MONGODB_URL=mongodb://localhost:27017/studybuddy
   ```

#### Issue: "AI API key not working"
**Symptoms:**
```
google.api_core.exceptions.Unauthenticated
Invalid API key provided
```

**Solutions:**
1. **Verify API key** in Google Cloud Console
2. **Check environment variable**
   ```bash
   echo $GOOGLE_AI_API_KEY
   ```

3. **Enable required APIs**
   - Generative AI API
   - Cloud Translation API (if used)

4. **Check API quotas** and billing

#### Issue: "Frontend build fails"
**Symptoms:**
```
npm ERR! Build failed with errors
Module not found errors
TypeScript compilation errors
```

**Solutions:**
1. **Clear node_modules** and reinstall
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Check Node.js version**
   ```bash
   node --version  # Should be 18+
   npm --version   # Should be 8+
   ```

3. **Fix TypeScript errors**
   ```bash
   npm run type-check
   ```

### Runtime Errors

#### Issue: "FastAPI server won't start"
**Symptoms:**
```
ImportError: No module named 'app'
Port already in use
Permission denied
```

**Solutions:**
1. **Check Python environment**
   ```bash
   which python
   pip list | grep fastapi
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Check port availability**
   ```bash
   lsof -i :8000
   # Kill process if needed
   kill -9 <PID>
   ```

4. **Run with correct permissions**
   ```bash
   # Don't run as root in production
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

#### Issue: "File upload processing fails"
**Symptoms:**
```
OCR processing timeout
File not found errors
Permission denied on uploads directory
```

**Solutions:**
1. **Check upload directory permissions**
   ```bash
   ls -la uploads/
   chmod 755 uploads/
   chown user:user uploads/
   ```

2. **Verify OCR scripts path**
   ```bash
   ls -la /home/unknown/Documents/medgloss-data-extractorfiles
   ```

3. **Check disk space**
   ```bash
   df -h
   # Clean up old files if needed
   find uploads/ -mtime +30 -delete
   ```

---

## 🚀 Deployment Issues

### Production Deployment

#### Issue: "SSL certificate errors"
**Symptoms:**
```
SSL certificate verify failed
NET::ERR_CERT_AUTHORITY_INVALID
Mixed content warnings
```

**Solutions:**
1. **Renew SSL certificate**
   ```bash
   sudo certbot renew
   sudo systemctl reload nginx
   ```

2. **Check certificate validity**
   ```bash
   sudo certbot certificates
   openssl x509 -in /etc/letsencrypt/live/domain/cert.pem -text -noout
   ```

3. **Update Nginx configuration**
   ```nginx
   # Force HTTPS redirect
   return 301 https://$server_name$request_uri;
   ```

#### Issue: "Nginx 502 Bad Gateway"
**Symptoms:**
- API calls return 502 error
- Backend service appears down
- Nginx error logs show connection refused

**Solutions:**
1. **Check backend service status**
   ```bash
   sudo systemctl status studybuddy
   sudo journalctl -u studybuddy -f
   ```

2. **Verify backend is listening**
   ```bash
   netstat -tlnp | grep :8000
   curl http://localhost:8000/health
   ```

3. **Check Nginx configuration**
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

4. **Review logs**
   ```bash
   sudo tail -f /var/log/nginx/error.log
   sudo tail -f /var/log/nginx/access.log
   ```

### Database Issues

#### Issue: "Database connection pool exhausted"
**Symptoms:**
```
pymongo.errors.ServerSelectionTimeoutError
Too many connections
Connection timeout
```

**Solutions:**
1. **Increase connection pool size**
   ```python
   # In config.py
   MONGODB_MAX_POOL_SIZE = 100
   MONGODB_MIN_POOL_SIZE = 10
   ```

2. **Check active connections**
   ```javascript
   // In MongoDB shell
   db.serverStatus().connections
   ```

3. **Restart MongoDB if needed**
   ```bash
   sudo systemctl restart mongod
   ```

#### Issue: "Database disk space full"
**Symptoms:**
```
No space left on device
Write operations failing
Database becomes read-only
```

**Solutions:**
1. **Check disk usage**
   ```bash
   df -h
   du -sh /var/lib/mongodb/
   ```

2. **Clean up old data**
   ```javascript
   // Remove old sessions (>90 days)
   db.study_sessions.deleteMany({
     created_at: { $lt: new Date(Date.now() - 90*24*60*60*1000) }
   })
   ```

3. **Compact database**
   ```javascript
   db.runCommand({ compact: "study_sessions" })
   ```

---

## 📞 Getting Help

### Self-Help Resources

#### Log Files Locations
```bash
# Application logs
tail -f logs/studybuddy.log

# System logs
sudo journalctl -u studybuddy -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log
```

#### Health Check Endpoints
```bash
# Backend health
curl https://your-domain.com/api/health

# Database connectivity
curl https://your-domain.com/api/health/db

# AI service status
curl https://your-domain.com/api/health/ai
```

### Contact Support

#### For Users
1. **Check this troubleshooting guide** first
2. **Search existing issues** in documentation
3. **Contact support** with detailed error description
4. **Provide screenshots** if applicable

#### For Developers
1. **Check logs** for detailed error messages
2. **Review configuration** files
3. **Test in development** environment first
4. **Submit bug reports** with reproduction steps

#### Information to Include
```
- Operating system and version
- Browser type and version
- Error messages (exact text)
- Steps to reproduce the issue
- Screenshots or screen recordings
- Log file excerpts (if applicable)
```

---

## 🔍 Diagnostic Tools

### Browser Developer Tools
```javascript
// Check console for errors
console.log("Debug info");

// Check network requests
// Go to Network tab in DevTools

// Check local storage
localStorage.getItem('auth_token');

// Check session storage
sessionStorage.getItem('session_data');
```

### System Monitoring
```bash
# Check system resources
htop
iotop
nethogs

# Check service status
systemctl status studybuddy
systemctl status nginx
systemctl status mongod

# Check ports
netstat -tlnp
ss -tlnp
```

### Database Diagnostics
```javascript
// MongoDB shell diagnostics
db.serverStatus()
db.stats()
db.study_sessions.stats()

// Check indexes
db.study_sessions.getIndexes()

// Explain query performance
db.study_sessions.find({user_id: ObjectId("...")}).explain("executionStats")
```

---

*Troubleshooting Guide - Study Buddy App v1.0.0*
