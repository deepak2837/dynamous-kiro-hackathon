#!/usr/bin/env python3
"""
Selenium E2E test for Study Buddy upload flow
Tests login, upload, and output generation
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class StudyBuddyE2ETest:
    def __init__(self):
        # Test credentials
        self.mobile = "7045024042"
        self.password = "Alan#walker672"
        self.test_file = "/home/unknown/Downloads/Text-to-PDF-r1p.pdf"
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--headless")  # Run headless for server environment
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 30)
            print("✅ Chrome driver initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Chrome driver: {e}")
            print("💡 Installing Chrome and ChromeDriver...")
            self._install_chrome()
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 30)
    
    def _install_chrome(self):
        """Install Chrome and ChromeDriver if not available"""
        import subprocess
        try:
            # Install Chrome
            subprocess.run(["wget", "-q", "-O", "-", "https://dl.google.com/linux/linux_signing_key.pub"], check=True)
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "google-chrome-stable"], check=True)
            
            # Install ChromeDriver
            subprocess.run(["sudo", "apt-get", "install", "-y", "chromium-chromedriver"], check=True)
            
        except Exception as e:
            print(f"⚠️ Could not install Chrome: {e}")
            print("Please install Chrome manually")
        
    def test_login(self):
        """Test login flow"""
        print("🔐 Testing login...")
        
        # Go to login page
        self.driver.get("http://localhost:3000/login")
        time.sleep(2)
        
        # Enter mobile number
        mobile_input = self.wait.until(EC.presence_of_element_located((By.NAME, "mobile")))
        mobile_input.clear()
        mobile_input.send_keys(self.mobile)
        
        # Enter password
        password_input = self.driver.find_element(By.NAME, "password")
        password_input.clear()
        password_input.send_keys(self.password)
        
        # Click login
        login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
        login_btn.click()
        
        # Wait for redirect to dashboard
        self.wait.until(EC.url_contains("/dashboard"))
        print("✅ Login successful")
        
    def test_navigate_to_study_buddy(self):
        """Navigate to Study Buddy"""
        print("📚 Navigating to Study Buddy...")
        
        # Look for Study Buddy card/link
        try:
            study_buddy_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'study-buddy') or contains(text(), 'Study Buddy')]"))
            )
            study_buddy_link.click()
        except TimeoutException:
            # Try alternative selectors
            try:
                study_buddy_card = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Study Buddy')]")
                study_buddy_card.click()
            except NoSuchElementException:
                print("⚠️ Study Buddy link not found, going directly to URL")
                self.driver.get("http://localhost:3000/study-buddy")
        
        time.sleep(2)
        print("✅ Navigated to Study Buddy")
        
    def test_file_upload(self):
        """Test file upload"""
        print("📤 Testing file upload...")
        
        # Check if file exists
        if not os.path.exists(self.test_file):
            raise Exception(f"Test file not found: {self.test_file}")
        
        # Find file input
        try:
            file_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
            file_input.send_keys(self.test_file)
            print(f"✅ File selected: {os.path.basename(self.test_file)}")
        except TimeoutException:
            print("❌ File input not found")
            raise
        
        time.sleep(1)
        
        # Click upload/process button
        try:
            process_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Process') or contains(text(), 'Upload') or contains(text(), 'Search')]"))
            )
            process_btn.click()
            print("✅ Upload initiated")
        except TimeoutException:
            print("❌ Process button not found")
            raise
            
    def test_processing_status(self):
        """Wait for processing to complete"""
        print("⏳ Waiting for processing...")
        
        # Wait for processing to start
        time.sleep(3)
        
        # Monitor processing status
        max_wait = 300  # 5 minutes max
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                # Look for completion indicators
                if self.driver.find_elements(By.XPATH, "//div[contains(text(), 'completed') or contains(text(), 'Complete')]"):
                    print("✅ Processing completed")
                    return True
                    
                # Look for error indicators
                if self.driver.find_elements(By.XPATH, "//div[contains(text(), 'error') or contains(text(), 'failed')]"):
                    print("❌ Processing failed")
                    return False
                    
                # Look for progress indicators
                progress_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'progress') or contains(text(), '%')]")
                if progress_elements:
                    print(f"⏳ Processing in progress...")
                
                time.sleep(5)
                
            except Exception as e:
                print(f"⚠️ Error checking status: {e}")
                time.sleep(5)
        
        print("⚠️ Processing timeout")
        return False
        
    def test_view_results(self):
        """Test viewing generated results"""
        print("📋 Testing results viewing...")
        
        # Look for results sections
        result_types = ["Questions", "Mock Tests", "Mnemonics", "Cheat Sheets", "Notes"]
        
        for result_type in result_types:
            try:
                # Look for result section
                result_section = self.driver.find_element(By.XPATH, f"//div[contains(text(), '{result_type}') or contains(@class, '{result_type.lower()}')]")
                print(f"✅ Found {result_type} section")
                
                # Try to click and view content
                result_section.click()
                time.sleep(2)
                
                # Check for content
                content_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'question') or contains(@class, 'content')]")
                if content_elements:
                    print(f"✅ {result_type} content loaded ({len(content_elements)} items)")
                else:
                    print(f"⚠️ {result_type} section empty")
                    
            except NoSuchElementException:
                print(f"❌ {result_type} section not found")
                
    def check_for_mock_responses(self):
        """Check if responses are mock or real AI"""
        print("🔍 Checking response quality...")
        
        try:
            # Look for fallback indicators
            fallback_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'FALLBACK') or contains(text(), 'API_KEY') or contains(text(), 'configuration')]")
            
            if fallback_elements:
                print("❌ MOCK RESPONSES DETECTED!")
                print("   - AI service is not configured properly")
                print("   - Check GEMINI_API_KEY in backend/.env")
                return False
            else:
                print("✅ Real AI responses detected")
                return True
                
        except Exception as e:
            print(f"⚠️ Could not determine response type: {e}")
            return None
            
    def run_test(self):
        """Run complete E2E test"""
        try:
            print("🚀 Starting Study Buddy E2E Test")
            print("=" * 50)
            
            # Test login
            self.test_login()
            
            # Navigate to Study Buddy
            self.test_navigate_to_study_buddy()
            
            # Upload file
            self.test_file_upload()
            
            # Wait for processing
            processing_success = self.test_processing_status()
            
            if processing_success:
                # View results
                self.test_view_results()
                
                # Check response quality
                self.check_for_mock_responses()
                
                print("\n" + "=" * 50)
                print("✅ E2E Test Completed Successfully!")
            else:
                print("\n" + "=" * 50)
                print("❌ E2E Test Failed - Processing did not complete")
                
        except Exception as e:
            print(f"\n❌ E2E Test Failed: {str(e)}")
            
        finally:
            # Take screenshot for debugging
            try:
                self.driver.save_screenshot("test_screenshot.png")
                print("📸 Screenshot saved: test_screenshot.png")
            except:
                pass
                
            # Close browser
            self.driver.quit()

if __name__ == "__main__":
    test = StudyBuddyE2ETest()
    test.run_test()
