#!/usr/bin/env python3
"""
Processing Modes Test for StudyBuddy

Tests both processing modes:
1. OCR + AI Mode
2. AI Only Mode

Uses the same PDF file for both tests to compare results.
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

class ProcessingModesTest:
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
    
    def login(self):
        """Login to the application"""
        self.log("🔐 Logging in...")
        
        try:
            self.driver.get(f"{FRONTEND_URL}/login")
            self.take_screenshot("01_login_page")
            
            # Fill credentials
            mobile_input = self.wait.until(EC.presence_of_element_located((By.NAME, "mobile")))
            mobile_input.clear()
            mobile_input.send_keys(MOBILE_NUMBER)
            
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.clear()
            password_input.send_keys(PASSWORD)
            
            # Click login
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
            login_button.click()
            
            time.sleep(3)
            
            # Check if redirected to study-buddy
            if "/study-buddy" in self.driver.current_url:
                self.log("✅ Login successful")
                return True
            else:
                self.log("❌ Login failed")
                return False
                
        except Exception as e:
            self.log(f"❌ Login error: {e}")
            return False
    
    def test_processing_mode(self, mode_name, mode_value):
        """Test a specific processing mode"""
        self.log(f"📤 Testing {mode_name}...")
        
        try:
            # Navigate to study-buddy page
            self.driver.get(f"{FRONTEND_URL}/study-buddy")
            time.sleep(2)
            
            # Find file input
            file_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
            file_input.send_keys(TEST_FILE_PATH)
            self.log("File selected")
            
            time.sleep(1)
            
            # Select processing mode
            try:
                mode_radio = self.driver.find_element(By.XPATH, f"//input[@value='{mode_value}']")
                mode_radio.click()
                self.log(f"Selected {mode_name}")
            except:
                self.log(f"⚠️ Could not find {mode_name} radio button")
            
            self.take_screenshot(f"02_{mode_value}_selected")
            
            # Click upload button
            upload_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Upload') or contains(text(), 'Process') or contains(text(), 'Search')]"))
            )
            upload_button.click()
            self.log("Upload initiated")
            
            time.sleep(2)
            self.take_screenshot(f"03_{mode_value}_upload_initiated")
            
            # Monitor processing
            processing_completed = self.monitor_processing(mode_value)
            
            if processing_completed:
                # Verify outputs
                outputs = self.verify_outputs(mode_value)
                return outputs
            else:
                self.log(f"❌ {mode_name} processing failed")
                return {}
                
        except Exception as e:
            self.log(f"❌ {mode_name} test error: {e}")
            self.take_screenshot(f"error_{mode_value}")
            return {}
    
    def monitor_processing(self, mode_value, max_wait=60):
        """Monitor processing completion"""
        self.log("⏳ Monitoring processing...")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                # Check for React errors first
                try:
                    error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Error') or contains(text(), 'error') or contains(text(), 'Failed') or contains(text(), 'failed')]")
                    if error_elements:
                        for elem in error_elements:
                            if elem.is_displayed():
                                self.log(f"⚠️ Frontend error detected: {elem.text}")
                except:
                    pass
                
                # Check browser console for errors
                try:
                    logs = self.driver.get_log('browser')
                    for log in logs:
                        if log['level'] == 'SEVERE':
                            self.log(f"⚠️ Browser error: {log['message']}")
                except:
                    pass
                
                page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                
                # Check for completion indicators
                if any(indicator in page_text for indicator in ["completed", "generated", "results"]):
                    # Check if we can see content tabs/sections
                    if any(content in page_text for content in ["questions", "mock test", "mnemonic"]):
                        self.log("✅ Processing completed")
                        self.take_screenshot(f"04_{mode_value}_completed")
                        return True
                
                # Check for failure
                if any(indicator in page_text for indicator in ["failed", "error"]):
                    self.log("❌ Processing failed")
                    self.log(f"Page content: {page_text[:500]}")
                    return False
                
                # Still processing
                if any(indicator in page_text for indicator in ["processing", "analyzing", "generating"]):
                    self.log("Still processing...")
                
                time.sleep(3)
                
            except Exception as e:
                self.log(f"Error monitoring: {e}")
                time.sleep(3)
        
        self.log("⏰ Processing timeout")
        return False
    
    def verify_outputs(self, mode_value):
        """Verify generated outputs"""
        self.log("🔍 Verifying outputs...")
        
        outputs = {
            "Questions": False,
            "Mock Tests": False,
            "Mnemonics": False,
            "Cheat Sheets": False,
            "Notes": False
        }
        
        try:
            # Check for session history loading
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            if "failed to load session history" in page_text:
                self.log("⚠️ Session history loading issue detected")
            
            # Check for each output type
            output_patterns = {
                "Questions": ["question", "mcq"],
                "Mock Tests": ["mock test", "test"],
                "Mnemonics": ["mnemonic"],
                "Cheat Sheets": ["cheat sheet", "sheet"],
                "Notes": ["notes", "note"]
            }
            
            for output_name, patterns in output_patterns.items():
                if any(pattern in page_text for pattern in patterns):
                    outputs[output_name] = True
                    self.log(f"✅ {output_name} found")
                else:
                    self.log(f"❌ {output_name} not found")
            
            self.take_screenshot(f"05_{mode_value}_outputs")
            
            # Try to click on different tabs to see if they work
            try:
                tabs = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'tab') or contains(text(), 'Questions') or contains(text(), 'Mock') or contains(text(), 'Mnemonic')]")
                for i, tab in enumerate(tabs[:3]):  # Test first 3 tabs
                    try:
                        tab.click()
                        time.sleep(1)
                        self.log(f"Clicked tab {i+1}: {tab.text}")
                        self.take_screenshot(f"06_{mode_value}_tab_{i+1}")
                    except:
                        pass
            except:
                pass
            
            return outputs
            
        except Exception as e:
            self.log(f"❌ Error verifying outputs: {e}")
            return outputs
    
    def run_test(self):
        """Run complete processing modes test"""
        self.log("=" * 60)
        self.log("🚀 Starting Processing Modes Test")
        self.log("=" * 60)
        
        try:
            # Login
            if not self.login():
                self.log("❌ Test failed at login")
                return False
            
            # Test OCR + AI Mode
            self.log("\n" + "=" * 40)
            self.log("Testing OCR + AI Mode")
            self.log("=" * 40)
            ocr_ai_results = self.test_processing_mode("OCR + AI Mode", "ocr_ai")
            
            # Wait between tests
            time.sleep(5)
            
            # Test AI Only Mode
            self.log("\n" + "=" * 40)
            self.log("Testing AI Only Mode")
            self.log("=" * 40)
            ai_only_results = self.test_processing_mode("AI Only Mode", "ai_only")
            
            # Summary
            self.log("\n" + "=" * 60)
            self.log("📊 TEST SUMMARY")
            self.log("=" * 60)
            
            self.log("OCR + AI Mode Results:")
            ocr_ai_success = sum(ocr_ai_results.values())
            for output, success in ocr_ai_results.items():
                status = "✅" if success else "❌"
                self.log(f"  {status} {output}")
            self.log(f"  Total: {ocr_ai_success}/5")
            
            self.log("\nAI Only Mode Results:")
            ai_only_success = sum(ai_only_results.values())
            for output, success in ai_only_results.items():
                status = "✅" if success else "❌"
                self.log(f"  {status} {output}")
            self.log(f"  Total: {ai_only_success}/5")
            
            # Overall result
            total_success = ocr_ai_success + ai_only_success
            self.log(f"\nOverall Success: {total_success}/10")
            
            if total_success >= 8:  # Allow some tolerance
                self.log("🎉 PROCESSING MODES TEST PASSED!")
                return True
            else:
                self.log("⚠️ Some processing modes had issues")
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
    # Check if test file exists
    if not os.path.exists(TEST_FILE_PATH):
        print(f"❌ Test file not found: {TEST_FILE_PATH}")
        sys.exit(1)
    
    # Run test
    test = ProcessingModesTest()
    success = test.run_test()
    
    sys.exit(0 if success else 1)
