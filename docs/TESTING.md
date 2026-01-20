# Study Buddy App - Testing Guide

## Overview

This document describes the testing strategy and available test suites for the Study Buddy App.

## Test Types

### 1. Unit Tests
Test individual functions and components in isolation.

### 2. Integration Tests
Test API endpoints and database operations.

### 3. End-to-End Tests
Test complete user workflows from start to finish.

---

## End-to-End Testing

### E2E API Test (`test_full_flow.py`)

**Purpose**: Tests the complete upload and processing flow via API calls.

**What it tests:**
- User authentication (login)
- File upload via API
- Processing status monitoring
- Verification of all 5 output types (questions, mock tests, mnemonics, cheat sheets, notes)

**Prerequisites:**
- Backend running on `localhost:8000`
- Test user registered with credentials:
  - Mobile: `7045024042`
  - Password: `Alan#walker672`
- Test PDF file at: `/home/unknown/Downloads/Text-to-PDF-r1p.pdf`

**Usage:**
```bash
python test_full_flow.py
```

**Expected Output:**
```
🔐 Logging in test user...
✅ Login successful - Token: eyJhbGciOiJIUzI1NiIs...
📤 Uploading Text-to-PDF-r1p.pdf...
✅ Upload successful!
   Session ID: 442ee11d-5691-4b8f-aebb-c9b862027ab7
   Files uploaded: 1
⏳ Waiting for processing...
   Status: processing
✅ Processing completed!
🔍 Verifying generated content...
   Questions: ✅ (25 items)
   Mock Tests: ✅ (2 items)
   Mnemonics: ✅ (5 items)
   Cheat Sheets: ✅ (1 items)
   Notes: ✅ (1 items)
📊 RESULTS: 5/5 features working
🎉 ALL TESTS PASSED!
```

---

### E2E Browser Test (`test_e2e_selenium.py`)

**Purpose**: Tests the complete user journey through the browser using Selenium WebDriver.

**What it tests:**
1. **Login Flow**: Navigate to login page, enter credentials, submit form
2. **Navigation**: Access Study Buddy page after authentication
3. **File Upload**: Select file, choose processing mode, initiate upload
4. **Processing Monitoring**: Track processing status in real-time
5. **Output Verification**: Verify all 5 output types are displayed

**Prerequisites:**
- Backend running on `localhost:8000`
- Frontend running on `localhost:3001`
- Chrome/Chromium browser installed
- Selenium WebDriver: `pip install selenium`
- Test user credentials: `7045024042` / `Alan#walker672`
- Test PDF file at: `/home/unknown/Downloads/Text-to-PDF-r1p.pdf`

**Configuration:**
Edit these constants in the script if needed:
```python
MOBILE_NUMBER = "7045024042"
PASSWORD = "Alan#walker672"
FRONTEND_URL = "http://localhost:3001"
TEST_FILE_PATH = "/home/unknown/Downloads/Text-to-PDF-r1p.pdf"
```

**Usage:**
```bash
# Run with visible browser (default)
python test_e2e_selenium.py

# To run headless, uncomment this line in the script:
# options.add_argument('--headless')
```

**Features:**
- **Visual Testing**: Browser window visible by default for debugging
- **Screenshots**: Automatic screenshots at each step saved as `screenshot_*.png`
- **Detailed Logging**: Timestamped logs for each action
- **Error Handling**: Screenshots captured on errors
- **Tab Navigation**: Tests clicking through result tabs

**Expected Output:**
```
============================================================
🚀 Starting StudyBuddy E2E Test
============================================================
[11:30:45] 🔐 Testing login flow...
[11:30:46] Navigated to: http://localhost:3001/login
[11:30:46] Screenshot saved: screenshot_01_login_page_1737356446.png
[11:30:48] Entered mobile number: 7045024042
[11:30:48] Entered password
[11:30:48] Screenshot saved: screenshot_02_credentials_entered_1737356448.png
[11:30:48] Clicked login button
[11:30:51] Screenshot saved: screenshot_03_after_login_1737356451.png
[11:30:51] ✅ Login successful!
[11:30:51] 📚 Navigating to Study Buddy...
[11:30:53] Screenshot saved: screenshot_04_study_buddy_page_1737356453.png
[11:30:53] Current URL: http://localhost:3001/study-buddy
[11:30:53] ✅ Successfully navigated to Study Buddy
[11:30:53] 📤 Testing file upload...
[11:30:53] Test file found: /home/unknown/Downloads/Text-to-PDF-r1p.pdf
[11:30:54] File selected
[11:30:55] Screenshot saved: screenshot_05_file_selected_1737356455.png
[11:30:55] Selected processing mode: default
[11:30:55] Clicked upload button
[11:30:57] Screenshot saved: screenshot_06_upload_initiated_1737356457.png
[11:30:57] ✅ Upload initiated - Session ID: 442ee11d-5691-4b8f-aebb-c9b862027ab7
[11:30:57] ⏳ Monitoring processing status...
[11:31:02] Status: processing
[11:31:32] ✅ Processing completed!
[11:31:32] Screenshot saved: screenshot_07_processing_completed_1737356492.png
[11:31:32] 🔍 Verifying generated outputs...
[11:31:32] ✅ Questions found
[11:31:32] ✅ Mock Tests found
[11:31:32] ✅ Mnemonics found
[11:31:32] ✅ Cheat Sheets found
[11:31:32] ✅ Notes found
[11:31:32] Screenshot saved: screenshot_10_outputs_verification_1737356492.png
============================================================
📊 TEST SUMMARY
============================================================
Login: ✅
Navigation: ✅
Upload: ✅
Processing: completed
Outputs:
  ✅ Questions
  ✅ Mock Tests
  ✅ Mnemonics
  ✅ Cheat Sheets
  ✅ Notes

Outputs Generated: 5/5

🏁 Test completed
Browser will close in 10 seconds...
```

**Screenshots Generated:**
- `screenshot_01_login_page_*.png` - Login page loaded
- `screenshot_02_credentials_entered_*.png` - Credentials filled
- `screenshot_03_after_login_*.png` - After login submission
- `screenshot_04_study_buddy_page_*.png` - Study Buddy page
- `screenshot_05_file_selected_*.png` - File selected for upload
- `screenshot_06_upload_initiated_*.png` - Upload button clicked
- `screenshot_07_processing_completed_*.png` - Processing finished
- `screenshot_10_outputs_verification_*.png` - Results page
- `screenshot_11_tab_*.png` - Individual result tabs
- `screenshot_error_*.png` - Error states (if any)

---

## Test Comparison

| Feature | API Test | Browser Test |
|---------|----------|--------------|
| **Speed** | Fast (~30s) | Slower (~2-3 min) |
| **UI Testing** | ❌ No | ✅ Yes |
| **Visual Verification** | ❌ No | ✅ Screenshots |
| **User Journey** | ❌ API only | ✅ Complete UX |
| **Debugging** | Logs only | Logs + Screenshots |
| **CI/CD Friendly** | ✅ Yes | ⚠️ Requires browser |
| **Dependencies** | requests | selenium + browser |

---

## Running Tests in CI/CD

### API Test (Recommended for CI)
```yaml
# .github/workflows/test.yml
- name: Run E2E API Test
  run: |
    python test_full_flow.py
```

### Browser Test (Requires Headless Setup)
```yaml
# .github/workflows/test.yml
- name: Install Chrome
  run: |
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
    sudo apt-get update
    sudo apt-get install google-chrome-stable

- name: Run E2E Browser Test
  run: |
    # Enable headless mode in script
    python test_e2e_selenium.py
```

---

## Troubleshooting

### API Test Issues

**Login fails:**
- Verify test user exists in database
- Check credentials in script
- Ensure backend is running on port 8000

**Upload fails:**
- Check test file path exists
- Verify file size is under 50MB
- Check backend logs for errors

**Processing timeout:**
- Increase wait time in script
- Check AI service credentials
- Review backend processing logs

### Browser Test Issues

**Chrome not found:**
```bash
# Install Chrome on Ubuntu
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f
```

**Selenium not installed:**
```bash
pip install selenium
```

**Element not found:**
- Check if frontend is running on correct port
- Review screenshots to see actual page state
- Verify element selectors match current UI

**Test file not found:**
- Update `TEST_FILE_PATH` in script
- Ensure file exists and is readable

**Frontend not on port 3001:**
- Update `FRONTEND_URL` in script
- Or change frontend port to 3001

---

## Best Practices

### For Development
1. Run API test first (faster feedback)
2. Run browser test for UI changes
3. Keep test credentials separate from production
4. Review screenshots when tests fail

### For CI/CD
1. Use API test in every commit
2. Run browser test on pull requests
3. Store screenshots as artifacts
4. Set appropriate timeouts for CI environment

### Test Data Management
1. Use dedicated test user account
2. Keep test files small (<5MB)
3. Clean up test sessions periodically
4. Don't commit test credentials to repo

---

## Future Enhancements

- [ ] Add test for multiple file upload
- [ ] Test different processing modes (OCR, AI-based)
- [ ] Test download functionality
- [ ] Test session history
- [ ] Add performance benchmarks
- [ ] Test error scenarios (invalid files, network errors)
- [ ] Add visual regression testing
- [ ] Test mobile responsive design

---

## Contributing

When adding new features:
1. Update relevant test scripts
2. Add new test cases if needed
3. Update this documentation
4. Ensure all tests pass before submitting PR
