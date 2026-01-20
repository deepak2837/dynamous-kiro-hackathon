# Fix AI Service Configuration

## Problem
Your Study Buddy app is returning mock responses instead of real AI-generated content because the AI service is not properly configured.

## Root Cause
The `GEMINI_API_KEY` in your `.env` file is either missing or set to a placeholder value, causing the AI service to fail and fall back to mock questions.

## Solution

### Step 1: Get a Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### Step 2: Configure the API Key
1. Open `backend/.env` file
2. Replace this line:
   ```
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```
   With your actual API key:
   ```
   GEMINI_API_KEY=AIzaSyD...your_actual_key_here
   ```

### Step 3: Test the Configuration
```bash
# Run the test script
python test_ai_config.py
```

### Step 4: Restart the Backend
```bash
cd backend
# Stop the current backend (Ctrl+C)
# Then restart:
uvicorn app.main:app --reload
```

### Step 5: Test Upload
1. Upload a PDF file
2. You should now see real AI-generated questions instead of mock responses

## Verification
- ✅ Real questions will have medical content and proper explanations
- ❌ Mock questions will say "FALLBACK" and mention configuration errors

## Troubleshooting

### If you still get mock responses:
1. Check the backend logs for error messages
2. Verify your API key is valid
3. Ensure you have internet connectivity
4. Check if you've exceeded API quotas

### Common errors:
- `API_KEY_INVALID`: Your API key is incorrect
- `QUOTA_EXCEEDED`: You've hit the free tier limits
- `PERMISSION_DENIED`: API key doesn't have proper permissions

## API Usage Notes
- Gemini API has a free tier with generous limits
- Each question generation uses ~1-2 API calls
- Processing a 10-page PDF typically uses 20-50 API calls
