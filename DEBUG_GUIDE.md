# 🐛 VS Code Debugging Guide

## How to Debug Request Flow from Frontend to Backend

### 1. 🎯 Key Breakpoint Locations

**File Upload Flow:**
- `backend/app/api/v1/endpoints/upload.py:42` - Upload request received
- `backend/app/api/v1/endpoints/upload.py:152` - Session data ready to save
- `backend/app/services/file_upload_processing_service.py:33` - File processing starts

**Text Input Flow:**
- `backend/app/api/v1/endpoints/text_input.py:32` - Text input request received  
- `backend/app/api/v1/endpoints/text_input.py:68` - Session ready to save
- `backend/app/services/processing.py:320` - Text processing starts

### 2. 🔴 How to Set Breakpoints in VS Code

1. **Open the file** in VS Code
2. **Click the left margin** next to the line number (red dot appears)
3. **Start debugging** with F5
4. **Make request** from frontend
5. **Code will pause** at breakpoint

### 3. 🎮 Debugging Controls

- **F10** - Step Over (next line)
- **F11** - Step Into (enter function)
- **Shift+F11** - Step Out (exit function)
- **F5** - Continue execution
- **Shift+F5** - Stop debugging

### 4. 🔍 What to Inspect

**At Upload Endpoint:**
- `files` - Uploaded files
- `processing_mode` - AI_ONLY mode
- `user_id` - User identifier

**At Session Save:**
- `session.dict()` - Complete session data
- `session_id` - Generated session ID
- `session_name` - Auto-generated name

**At Processing Service:**
- `session_data` - Retrieved from database
- `files` - File paths to process
- `combined_content` - Extracted text

### 5. 📋 Request Flow Trace

```
Frontend Request
    ↓
upload.py:42 (BREAKPOINT 1) ← Request received
    ↓
File validation & processing
    ↓
upload.py:152 (BREAKPOINT 2) ← Session save
    ↓
Background processing starts
    ↓
file_upload_processing_service.py:33 (BREAKPOINT 3) ← Processing
    ↓
AI content generation
    ↓
Results saved to database
```

### 6. 🚀 Start Debugging

1. **Set breakpoints** at the marked locations
2. **Press F5** in VS Code to start debugging
3. **Upload a file** from frontend
4. **Watch code execution** step by step with F10/F11
