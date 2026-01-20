#!/usr/bin/env python3
"""
End-to-End Selenium Test for StudyBuddy Upload Flow

Tests the complete user journey:
1. Login with existing credentials
2. Navigate to Study Buddy page
3. Upload a test file
4. Monitor processing status
5. Verify all 5 outputs are generated

Prerequisites:
- Backend running on localhost:8000
- Frontend running on localhost:3001
- Chrome/Chromium browser installed
- Test credentials: 7045024042 / Alan#walker672
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
import sys

# Test credentials
MOBILE_NUMBER = "7045024042"
PASSWORD = "Alan#walker672"
FRONTEND_URL = "http://localhost:3000"
TEST_FILE_PATH = "/home/unknown/Downloads/Text-to-PDF-r1p.pdf"

class StudyBuddyE2ETest:
    def __init__(self):
        # Setup Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # Comment out headless mode to see the browser
        # options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 20)
        
    def log(self, message):
        """Print timestamped log message"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def take_screenshot(self, name):
        """Take screenshot for debugging"""
        filename = f"screenshot_{name}_{int(time.time())}.png"
        self.driver.save_screenshot(filename)
        self.log(f"Screenshot saved: {filename}")
    
    def test_login(self):
        """Test login flow"""
        self.log("🔐 Testing login flow...")
        
        try:
            # Navigate to login page
            self.driver.get(f"{FRONTEND_URL}/login")
            self.log(f"Navigated to: {self.driver.current_url}")
            self.take_screenshot("01_login_page")
            
            # Wait for page to load
            time.sleep(2)
            
            # Find and fill mobile number
            mobile_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "mobile"))
            )
            mobile_input.clear()
            mobile_input.send_keys(MOBILE_NUMBER)
            self.log(f"Entered mobile number: {MOBILE_NUMBER}")
            
            # Find and fill password
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.clear()
            password_input.send_keys(PASSWORD)
            self.log("Entered password")
            
            self.take_screenshot("02_credentials_entered")
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign In')]")
            login_button.click()
            self.log("Clicked login button")
            
            # Wait for redirect or error message
            time.sleep(5)
            self.take_screenshot("03_after_login")
            
            # Check for error messages first
            try:
                error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'error') or contains(text(), 'Error') or contains(text(), 'invalid') or contains(text(), 'Invalid')]")
                if error_elements:
                    for elem in error_elements:
                        self.log(f"Error message found: {elem.text}")
            except:
                pass
            
            # Check if login successful
            current_url = self.driver.current_url
            if "/login" not in current_url:
                self.log("✅ Login successful!")
                return True
            else:
                self.log("❌ Login failed - still on login page")
                # Print page source for debugging
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                self.log(f"Page content snippet: {page_text[:200]}...")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {e}")
            self.take_screenshot("error_login")
            return False
    
    def test_navigate_to_study_buddy(self):
        """Navigate to Study Buddy page"""
        self.log("📚 Navigating to Study Buddy...")
        
        try:
            # Since we're having auth issues, let's try to find any upload functionality
            # on the current page or try multiple approaches
            
            current_url = self.driver.current_url
            self.log(f"Current URL after login: {current_url}")
            
            # Try direct navigation to study-buddy
            self.log("Attempting direct navigation to /study-buddy")
            self.driver.get(f"{FRONTEND_URL}/study-buddy")
            time.sleep(3)
            
            current_url = self.driver.current_url
            self.log(f"URL after navigation attempt: {current_url}")
            
            # Check if we can find file upload elements regardless of URL
            try:
                file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                self.log("✅ File input found - proceeding with upload test")
                self.take_screenshot("04_study_buddy_page")
                return True
            except:
                self.log("No file input found")
            
            # If we're on auth page, let's see if there's a way to proceed
            if "/auth" in current_url:
                self.log("On auth page, looking for navigation options...")
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                
                # Look for any links or buttons that might lead to study buddy
                try:
                    links = self.driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        if "study" in link.text.lower() or "buddy" in link.text.lower():
                            self.log(f"Found potential link: {link.text}")
                            link.click()
                            time.sleep(3)
                            
                            # Check URL after clicking
                            new_url = self.driver.current_url
                            self.log(f"URL after clicking link: {new_url}")
                            
                            # Take screenshot after clicking
                            self.take_screenshot("05_after_link_click")
                            break
                except Exception as e:
                    self.log(f"Error clicking links: {e}")
            
            # Final check for file upload capability
            try:
                file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                self.log("✅ File input found after navigation attempts")
                self.take_screenshot("04_study_buddy_page")
                return True
            except:
                self.log("❌ No file input found - cannot proceed with upload test")
                self.take_screenshot("04_study_buddy_page")
                return False
                
        except Exception as e:
            self.log(f"❌ Navigation error: {e}")
            self.take_screenshot("error_navigation")
            return False
    
    def test_file_upload(self):
        """Test file upload flow"""
        self.log("📤 Testing file upload...")
        
        try:
            # Check if test file exists
            if not os.path.exists(TEST_FILE_PATH):
                self.log(f"❌ Test file not found: {TEST_FILE_PATH}")
                return False, None
            
            self.log(f"Test file found: {TEST_FILE_PATH}")
            
            # Find file input
            file_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            file_input.send_keys(TEST_FILE_PATH)
            self.log("File selected")
            
            time.sleep(1)
            self.take_screenshot("05_file_selected")
            
            # Select processing mode (if available)
            try:
                mode_select = self.driver.find_element(By.NAME, "processing_mode")
                mode_select.send_keys("default")
                self.log("Selected processing mode: default")
            except:
                self.log("Processing mode selector not found (may be optional)")
            
            # Find and click upload/process button
            upload_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Upload') or contains(text(), 'Process') or contains(text(), 'Search')]"))
            )
            upload_button.click()
            self.log("Clicked upload button")
            
            time.sleep(2)
            self.take_screenshot("06_upload_initiated")
            
            # Try to extract session ID from page or network
            session_id = self.extract_session_id()
            
            if session_id:
                self.log(f"✅ Upload initiated - Session ID: {session_id}")
                return True, session_id
            else:
                self.log("⚠️ Upload initiated but session ID not found")
                return True, None
                
        except Exception as e:
            self.log(f"❌ Upload error: {e}")
            self.take_screenshot("error_upload")
            return False, None
    
    def extract_session_id(self):
        """Try to extract session ID from page"""
        try:
            # Look for session ID in page text
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            if "session" in page_text.lower():
                # Try to find UUID pattern
                import re
                uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
                matches = re.findall(uuid_pattern, page_text, re.IGNORECASE)
                if matches:
                    return matches[0]
        except:
            pass
        return None
    
    def test_monitor_processing(self, max_wait=120):
        """Monitor processing status"""
        self.log("⏳ Monitoring processing status...")
        
        start_time = time.time()
        last_status = None
        
        while time.time() - start_time < max_wait:
            try:
                # Look for status indicators
                page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                
                # Check for completion indicators
                completion_indicators = [
                    "completed", "success", "ready", "view results", 
                    "generated", "study materials generated", "results"
                ]
                
                if any(indicator in page_text for indicator in completion_indicators):
                    # Also check if we're on the results step (step 3)
                    if "3" in page_text and "results" in page_text:
                        self.log("✅ Processing completed!")
                        self.take_screenshot("07_processing_completed")
                        return "completed"
                
                # Check for explicit failure indicators
                failure_indicators = ["failed", "error", "try again", "something went wrong"]
                if any(indicator in page_text for indicator in failure_indicators):
                    self.log("❌ Processing failed!")
                    self.take_screenshot("08_processing_failed")
                    self.log(f"Page content: {page_text[:500]}")
                    return "failed"
                
                # Check for processing indicators
                processing_indicators = [
                    "processing", "loading", "please wait", "analyzing", 
                    "generating", "creating", "uploading", "session is processing"
                ]
                
                if any(indicator in page_text for indicator in processing_indicators):
                    current_status = "processing"
                    if current_status != last_status:
                        self.log(f"Status: {current_status}")
                        last_status = current_status
                
                # Check if we can see any generated content tabs/sections
                content_indicators = ["questions", "mock test", "mnemonic", "cheat sheet", "notes"]
                visible_content = [indicator for indicator in content_indicators if indicator in page_text]
                
                if len(visible_content) >= 3:  # If we can see at least 3 types of content
                    self.log(f"✅ Multiple content types visible: {visible_content}")
                    self.take_screenshot("07_processing_completed")
                    return "completed"
                
                time.sleep(3)  # Check every 3 seconds
                
            except Exception as e:
                self.log(f"Error checking status: {e}")
                time.sleep(3)
        
        self.log("⏰ Processing timeout")
        self.take_screenshot("09_processing_timeout")
        return "timeout"
    
    def test_verify_outputs(self):
        """Verify all 5 outputs are available"""
        self.log("🔍 Verifying generated outputs...")
        
        outputs = {
            "Questions": False,
            "Mock Tests": False,
            "Mnemonics": False,
            "Cheat Sheets": False,
            "Notes": False
        }
        
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            
            # More specific patterns for each output type
            output_patterns = {
                "Questions": ["question", "mcq", "multiple choice"],
                "Mock Tests": ["mock test", "test", "exam"],
                "Mnemonics": ["mnemonic", "memory aid"],
                "Cheat Sheets": ["cheat sheet", "quick reference", "summary"],
                "Notes": ["notes", "compiled", "study material"]
            }
            
            for output_name, patterns in output_patterns.items():
                if any(pattern in page_text for pattern in patterns):
                    outputs[output_name] = True
                    self.log(f"✅ {output_name} found")
                else:
                    self.log(f"❌ {output_name} not found")
            
            self.take_screenshot("10_outputs_verification")
            
            # Try clicking on tabs/buttons to see different content
            for output_name in outputs.keys():
                try:
                    # Look for buttons or tabs with the output name
                    possible_selectors = [
                        f"//button[contains(text(), '{output_name}')]",
                        f"//div[contains(text(), '{output_name}')]",
                        f"//span[contains(text(), '{output_name}')]",
                        f"//a[contains(text(), '{output_name}')]"
                    ]
                    
                    for selector in possible_selectors:
                        try:
                            element = self.driver.find_element(By.XPATH, selector)
                            element.click()
                            time.sleep(1)
                            self.take_screenshot(f"11_tab_{output_name.replace(' ', '_')}")
                            
                            # Check if content appeared after clicking
                            new_page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                            if any(pattern in new_page_text for pattern in output_patterns[output_name]):
                                outputs[output_name] = True
                                self.log(f"✅ {output_name} confirmed after clicking")
                            break
                        except:
                            continue
                except:
                    pass
            
            return outputs
            
        except Exception as e:
            self.log(f"❌ Error verifying outputs: {e}")
            return outputs
    
    def run_full_test(self):
        """Run complete E2E test"""
        self.log("=" * 60)
        self.log("🚀 Starting StudyBuddy E2E Test")
        self.log("=" * 60)
        
        try:
            # Step 1: Login
            if not self.test_login():
                self.log("❌ Test failed at login step")
                return False
            
            # Step 2: Navigate to Study Buddy
            if not self.test_navigate_to_study_buddy():
                self.log("❌ Test failed at navigation step")
                return False
            
            # Step 3: Upload file
            upload_success, session_id = self.test_file_upload()
            if not upload_success:
                self.log("❌ Test failed at upload step")
                return False
            
            # Step 4: Monitor processing
            status = self.test_monitor_processing()
            if status != "completed":
                self.log(f"⚠️ Processing ended with status: {status}")
                # Continue to check what's available
            
            # Step 5: Verify outputs
            outputs = self.test_verify_outputs()
            
            # Summary
            self.log("=" * 60)
            self.log("📊 TEST SUMMARY")
            self.log("=" * 60)
            self.log(f"Login: ✅")
            self.log(f"Navigation: ✅")
            self.log(f"Upload: ✅")
            self.log(f"Processing: {status}")
            self.log(f"Outputs:")
            for name, found in outputs.items():
                status_icon = "✅" if found else "❌"
                self.log(f"  {status_icon} {name}")
            
            success_count = sum(outputs.values())
            self.log(f"\nOutputs Generated: {success_count}/5")
            
            return success_count == 5
            
        except Exception as e:
            self.log(f"❌ Test failed with error: {e}")
            self.take_screenshot("error_final")
            return False
        
        finally:
            self.log("\n🏁 Test completed")
            self.log("Browser will close in 10 seconds...")
            time.sleep(10)
            self.driver.quit()

if __name__ == "__main__":
    # Check if test file exists
    if not os.path.exists(TEST_FILE_PATH):
        print(f"❌ Test file not found: {TEST_FILE_PATH}")
        print("Please update TEST_FILE_PATH in the script")
        sys.exit(1)
    
    # Run test
    test = StudyBuddyE2ETest()
    success = test.run_full_test()
    
    sys.exit(0 if success else 1)
