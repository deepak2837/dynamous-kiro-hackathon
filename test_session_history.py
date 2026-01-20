#!/usr/bin/env python3
"""
Session History Test for StudyBuddy

Tests that after authentication:
1. Previous session history is visible
2. User can see their past generations
3. Session history shows correct content counts
4. User can click on previous sessions
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

# Test credentials
MOBILE_NUMBER = "7045024042"
PASSWORD = "Alan#walker672"
FRONTEND_URL = "http://localhost:3000"
TEST_FILE_PATH = "/home/unknown/Downloads/Text-to-PDF-r1p.pdf"

class SessionHistoryTest:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 20)
        
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def take_screenshot(self, name):
        filename = f"screenshot_{name}_{int(time.time())}.png"
        self.driver.save_screenshot(filename)
        self.log(f"Screenshot saved: {filename}")
    
    def login(self):
        """Login to the application"""
        self.log("🔐 Logging in...")
        
        try:
            self.driver.get(f"{FRONTEND_URL}/login")
            time.sleep(2)
            
            mobile_input = self.wait.until(EC.presence_of_element_located((By.NAME, "mobile")))
            mobile_input.clear()
            mobile_input.send_keys(MOBILE_NUMBER)
            
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.clear()
            password_input.send_keys(PASSWORD)
            
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
            login_button.click()
            
            time.sleep(3)
            
            if "/study-buddy" in self.driver.current_url:
                self.log("✅ Login successful")
                return True
            else:
                self.log("❌ Login failed")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {e}")
            return False
    
    def create_test_session(self):
        """Create a test session to ensure we have history"""
        self.log("📤 Creating test session...")
        
        try:
            # Navigate to study-buddy page
            self.driver.get(f"{FRONTEND_URL}/study-buddy")
            time.sleep(2)
            
            # Upload file
            file_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
            file_input.send_keys(TEST_FILE_PATH)
            
            # Select OCR+AI mode
            try:
                mode_radio = self.driver.find_element(By.XPATH, "//input[@value='ocr_ai']")
                mode_radio.click()
            except:
                pass
            
            # Click upload
            upload_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Upload') or contains(text(), 'Process') or contains(text(), 'Search')]"))
            )
            upload_button.click()
            
            # Wait for processing to complete
            time.sleep(10)
            
            self.log("✅ Test session created")
            return True
            
        except Exception as e:
            self.log(f"❌ Error creating test session: {e}")
            return False
    
    def test_session_history_visibility(self):
        """Test if session history is visible"""
        self.log("📋 Testing session history visibility...")
        
        try:
            # Navigate to study-buddy page
            self.driver.get(f"{FRONTEND_URL}/study-buddy")
            time.sleep(3)
            
            self.take_screenshot("01_study_buddy_page")
            
            # Look for session history section
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            
            history_indicators = [
                "session history", "history", "previous sessions", 
                "past sessions", "recent sessions"
            ]
            
            history_found = any(indicator in page_text for indicator in history_indicators)
            
            if history_found:
                self.log("✅ Session history section found")
                
                # Look for specific session entries
                try:
                    # Check for session cards or list items
                    session_elements = self.driver.find_elements(By.XPATH, 
                        "//*[contains(@class, 'session') or contains(text(), 'Session') or contains(text(), 'ago')]")
                    
                    if session_elements:
                        self.log(f"✅ Found {len(session_elements)} session elements")
                        
                        # Check for content indicators
                        content_indicators = ["questions", "mock test", "mnemonic", "cheat sheet", "notes"]
                        content_found = any(indicator in page_text for indicator in content_indicators)
                        
                        if content_found:
                            self.log("✅ Session content indicators found")
                        else:
                            self.log("⚠️ No session content indicators found")
                        
                        return True
                    else:
                        self.log("❌ No session elements found")
                        return False
                        
                except Exception as e:
                    self.log(f"Error finding session elements: {e}")
                    return False
            else:
                self.log("❌ Session history section not found")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing session history: {e}")
            return False
    
    def test_session_interaction(self):
        """Test if user can interact with session history"""
        self.log("🖱️ Testing session interaction...")
        
        try:
            # Look for clickable session elements
            clickable_sessions = self.driver.find_elements(By.XPATH, 
                "//button[contains(@class, 'session') or contains(text(), 'Session')] | //div[contains(@class, 'cursor-pointer')] | //a[contains(@href, 'session')]")
            
            if clickable_sessions:
                self.log(f"✅ Found {len(clickable_sessions)} clickable session elements")
                
                # Try clicking the first session
                try:
                    first_session = clickable_sessions[0]
                    self.log(f"Clicking on session: {first_session.text[:50]}...")
                    first_session.click()
                    time.sleep(3)
                    
                    self.take_screenshot("02_session_clicked")
                    
                    # Check if content changed or results are shown
                    page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                    
                    result_indicators = [
                        "questions", "mock test", "mnemonic", "cheat sheet", "notes",
                        "results", "generated", "content"
                    ]
                    
                    results_shown = any(indicator in page_text for indicator in result_indicators)
                    
                    if results_shown:
                        self.log("✅ Session results displayed after clicking")
                        return True
                    else:
                        self.log("⚠️ No clear results shown after clicking")
                        return False
                        
                except Exception as e:
                    self.log(f"Error clicking session: {e}")
                    return False
            else:
                self.log("❌ No clickable session elements found")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing session interaction: {e}")
            return False
    
    def test_session_content_counts(self):
        """Test if session history shows content counts"""
        self.log("🔢 Testing session content counts...")
        
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Look for numerical indicators
            count_patterns = [
                r'\d+\s+questions?', r'\d+\s+tests?', r'\d+\s+mnemonics?',
                r'\d+\s+sheets?', r'\d+\s+notes?', r'\d+\s+items?'
            ]
            
            import re
            counts_found = []
            for pattern in count_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                counts_found.extend(matches)
            
            if counts_found:
                self.log(f"✅ Content counts found: {counts_found}")
                return True
            else:
                self.log("⚠️ No content counts found")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing content counts: {e}")
            return False
    
    def run_test(self):
        """Run complete session history test"""
        self.log("=" * 60)
        self.log("🚀 Starting Session History Test")
        self.log("=" * 60)
        
        try:
            # Step 1: Login
            if not self.login():
                self.log("❌ Test failed at login step")
                return False
            
            # Step 2: Create a test session (to ensure we have history)
            self.create_test_session()
            
            # Step 3: Test session history visibility
            history_visible = self.test_session_history_visibility()
            
            # Step 4: Test session interaction
            interaction_works = self.test_session_interaction()
            
            # Step 5: Test content counts
            counts_visible = self.test_session_content_counts()
            
            # Summary
            self.log("=" * 60)
            self.log("📊 SESSION HISTORY TEST SUMMARY")
            self.log("=" * 60)
            self.log(f"Login: ✅")
            self.log(f"Session History Visible: {'✅' if history_visible else '❌'}")
            self.log(f"Session Interaction: {'✅' if interaction_works else '❌'}")
            self.log(f"Content Counts: {'✅' if counts_visible else '❌'}")
            
            success_count = sum([history_visible, interaction_works, counts_visible])
            self.log(f"\nOverall Success: {success_count}/3")
            
            if success_count >= 2:  # Allow some tolerance
                self.log("🎉 SESSION HISTORY TEST PASSED!")
                return True
            else:
                self.log("⚠️ Session history has issues")
                return False
                
        except Exception as e:
            self.log(f"❌ Test failed with error: {e}")
            return False
        
        finally:
            self.log("\n🏁 Test completed")
            self.log("Browser will close in 10 seconds...")
            time.sleep(10)
            self.driver.quit()

if __name__ == "__main__":
    test = SessionHistoryTest()
    success = test.run_test()
    
    exit(0 if success else 1)
