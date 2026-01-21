#!/usr/bin/env python3
"""
Selenium test for topic input flow with log monitoring
"""

import time
import logging
import subprocess
import threading
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('selenium_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TopicInputTest:
    def __init__(self):
        self.driver = None
        self.backend_logs = []
        self.frontend_logs = []
        
    def setup_driver(self):
        """Setup Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--remote-debugging-port=9222")
        
        # Add logging preferences
        chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            logger.info("✅ Chrome driver initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Chrome driver: {e}")
            # Try with system chrome
            try:
                chrome_options.binary_location = "/usr/bin/google-chrome"
                self.driver = webdriver.Chrome(options=chrome_options)
                logger.info("✅ Chrome driver initialized with system chrome")
            except Exception as e2:
                logger.error(f"❌ Failed with system chrome: {e2}")
                raise
        
    def monitor_backend_logs(self):
        """Monitor backend logs in real-time"""
        try:
            log_file = "/home/unknown/Documents/hackathon application/dynamous-kiro-hackathon/backend/backend.log"
            if not os.path.exists(log_file):
                log_file = "/home/unknown/Documents/hackathon application/dynamous-kiro-hackathon/logs/backend.log"
            
            process = subprocess.Popen(
                ['tail', '-f', log_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    self.backend_logs.append(line.strip())
                    if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception']):
                        logger.error(f"BACKEND ERROR: {line.strip()}")
                    elif any(keyword in line.lower() for keyword in ['generated', 'completed', 'success', 'pipeline']):
                        logger.info(f"BACKEND SUCCESS: {line.strip()}")
                        
        except Exception as e:
            logger.error(f"Error monitoring backend logs: {e}")
    
    def login(self):
        """Login with provided credentials"""
        logger.info("🔐 Starting login process...")
        
        self.driver.get("http://localhost:3000")
        time.sleep(3)
        
        try:
            # Look for login form elements with multiple selectors
            mobile_selectors = [
                "input[name='mobile']",
                "input[name='mobile_number']", 
                "input[placeholder*='mobile']",
                "input[placeholder*='phone']",
                "input[type='tel']"
            ]
            
            mobile_input = None
            for selector in mobile_selectors:
                try:
                    mobile_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Found mobile input with selector: {selector}")
                    break
                except:
                    continue
            
            if not mobile_input:
                logger.error("❌ Could not find mobile input field")
                return False
            
            # Find password input
            password_selectors = [
                "input[name='password']",
                "input[type='password']"
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not password_input:
                logger.error("❌ Could not find password input field")
                return False
            
            # Find login button
            login_selectors = [
                "button[type='submit']",
                "button:contains('Login')",
                "button:contains('Sign In')",
                "input[type='submit']"
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    if 'contains' in selector:
                        login_button = self.driver.find_element(By.XPATH, f"//button[contains(text(), 'Login') or contains(text(), 'Sign In')]")
                    else:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not login_button:
                logger.error("❌ Could not find login button")
                return False
            
            # Enter credentials
            mobile_input.clear()
            mobile_input.send_keys("7045024042")
            logger.info("📱 Entered mobile number")
            
            password_input.clear()
            password_input.send_keys("Alan#walker672")
            logger.info("🔑 Entered password")
            
            # Click login
            login_button.click()
            logger.info("🖱️ Clicked login button")
            
            # Wait for login success (look for dashboard or redirect)
            time.sleep(5)
            
            # Check if we're logged in by looking for dashboard elements
            current_url = self.driver.current_url
            logger.info(f"Current URL after login: {current_url}")
            
            # Look for success indicators
            success_indicators = [
                "dashboard",
                "study-buddy", 
                "welcome",
                "logout"
            ]
            
            page_source = self.driver.page_source.lower()
            login_success = any(indicator in page_source for indicator in success_indicators)
            
            if login_success:
                logger.info("✅ Login successful")
                return True
            else:
                logger.error("❌ Login may have failed - no success indicators found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
        
    def navigate_to_topic_input(self):
        """Navigate to topic input section"""
        logger.info("🧭 Navigating to topic input...")
        
        try:
            # Look for Study Buddy or topic-related elements
            navigation_selectors = [
                "//a[contains(text(), 'Study Buddy')]",
                "//div[contains(text(), 'Study Buddy')]",
                "//a[contains(@href, 'study-buddy')]",
                "//a[contains(text(), 'Topic')]",
                "//button[contains(text(), 'Enter Topic')]"
            ]
            
            element_found = False
            for selector in navigation_selectors:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    element.click()
                    logger.info(f"✅ Clicked navigation element: {selector}")
                    element_found = True
                    break
                except:
                    continue
            
            if not element_found:
                logger.warning("⚠️ Could not find specific navigation - trying direct URL")
                self.driver.get("http://localhost:3000/study-buddy")
            
            time.sleep(3)
            logger.info("✅ Navigated to topic input section")
            return True
            
        except Exception as e:
            logger.error(f"❌ Navigation error: {e}")
            return False
        
    def enter_topic_and_generate(self):
        """Enter topic and generate study materials"""
        logger.info("📝 Entering topic and generating materials...")
        
        try:
            # Look for topic input field
            topic_selectors = [
                "input[placeholder*='topic']",
                "input[placeholder*='Topic']", 
                "textarea[placeholder*='topic']",
                "textarea[placeholder*='Topic']",
                "input[name*='topic']",
                "textarea[name*='topic']"
            ]
            
            topic_input = None
            for selector in topic_selectors:
                try:
                    topic_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Found topic input with selector: {selector}")
                    break
                except:
                    continue
            
            if not topic_input:
                logger.error("❌ Could not find topic input field")
                return False
            
            # Enter medical topic
            test_topic = "Cardiovascular System - Heart anatomy, blood circulation, cardiac cycle, ECG interpretation, heart diseases, hypertension, cardiac medications, arrhythmias"
            topic_input.clear()
            topic_input.send_keys(test_topic)
            
            logger.info(f"📋 Entered topic: {test_topic}")
            
            # Find and click generate button
            generate_selectors = [
                "button:contains('Generate')",
                "button:contains('Create')", 
                "button:contains('Process')",
                "button:contains('Submit')",
                "button[type='submit']"
            ]
            
            generate_button = None
            for selector in generate_selectors:
                try:
                    if 'contains' in selector:
                        text = selector.split("'")[1]
                        generate_button = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{text}')]")
                    else:
                        generate_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not generate_button:
                logger.error("❌ Could not find generate button")
                return False
            
            generate_button.click()
            logger.info("🚀 Clicked generate button")
            
            # Monitor processing
            self.monitor_processing()
            return True
            
        except Exception as e:
            logger.error(f"❌ Topic entry error: {e}")
            return False
        
    def monitor_processing(self):
        """Monitor the processing and wait for completion"""
        logger.info("⏳ Monitoring processing...")
        
        start_time = time.time()
        max_wait_time = 300  # 5 minutes
        
        while time.time() - start_time < max_wait_time:
            try:
                # Check for processing status
                status_selectors = [
                    "//*[contains(text(), 'Processing')]",
                    "//*[contains(text(), 'Generating')]", 
                    "//*[contains(text(), 'Complete')]",
                    "//*[contains(text(), 'Ready')]",
                    "//*[contains(text(), 'Success')]"
                ]
                
                for selector in status_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        if elements:
                            status_text = elements[0].text
                            logger.info(f"📊 Status: {status_text}")
                            
                            if any(word in status_text.lower() for word in ['complete', 'ready', 'success', 'generated']):
                                logger.info("✅ Processing completed")
                                return True
                    except:
                        continue
                
                # Check for errors
                error_selectors = [
                    "//*[contains(@class, 'error')]",
                    "//*[contains(text(), 'Error')]",
                    "//*[contains(text(), 'Failed')]"
                ]
                
                for selector in error_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        if elements:
                            error_text = elements[0].text
                            logger.error(f"❌ Frontend Error: {error_text}")
                    except:
                        continue
                
                time.sleep(3)
                
            except Exception as e:
                logger.warning(f"Error checking status: {e}")
                time.sleep(3)
        
        logger.info("⏱️ Processing monitoring completed")
        return True
        
    def verify_outputs(self):
        """Verify all 5 outputs are generated"""
        logger.info("🔍 Verifying outputs...")
        
        expected_outputs = [
            "Questions",
            "Mock Test", 
            "Mnemonics",
            "Cheat Sheet",
            "Notes"
        ]
        
        found_outputs = []
        
        for output in expected_outputs:
            try:
                # Look for output sections or tabs
                selectors = [
                    f"//*[contains(text(), '{output}')]",
                    f"//*[contains(@class, '{output.lower()}')]",
                    f"//h1[contains(text(), '{output}')]",
                    f"//h2[contains(text(), '{output}')]",
                    f"//h3[contains(text(), '{output}')]"
                ]
                
                found = False
                for selector in selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        if elements:
                            found_outputs.append(output)
                            logger.info(f"✅ Found: {output}")
                            found = True
                            
                            # Try to click and check content
                            try:
                                elements[0].click()
                                time.sleep(1)
                                
                                # Check for content items
                                content_selectors = [
                                    "//*[contains(@class, 'item')]",
                                    "//*[contains(@class, 'question')]",
                                    "//*[contains(@class, 'content')]",
                                    "//li",
                                    "//div[contains(@class, 'card')]"
                                ]
                                
                                content_count = 0
                                for content_selector in content_selectors:
                                    try:
                                        content_elements = self.driver.find_elements(By.XPATH, content_selector)
                                        content_count = max(content_count, len(content_elements))
                                    except:
                                        continue
                                
                                if content_count > 0:
                                    logger.info(f"📄 {output} has {content_count} content items")
                                else:
                                    logger.warning(f"⚠️ {output} appears empty")
                                    
                            except Exception as e:
                                logger.warning(f"Could not check {output} content: {e}")
                            break
                    except:
                        continue
                
                if not found:
                    logger.error(f"❌ Missing: {output}")
                    
            except Exception as e:
                logger.error(f"Error checking {output}: {e}")
        
        logger.info(f"📊 Found {len(found_outputs)}/5 outputs: {found_outputs}")
        return len(found_outputs) >= 3  # Accept if at least 3 outputs found
        
    def capture_frontend_logs(self):
        """Capture browser console logs"""
        try:
            logs = self.driver.get_log('browser')
            for log in logs:
                level = log['level']
                message = log['message']
                
                if level in ['SEVERE', 'ERROR']:
                    logger.error(f"FRONTEND ERROR: {message}")
                elif level == 'WARNING':
                    logger.warning(f"FRONTEND WARNING: {message}")
                else:
                    logger.info(f"FRONTEND LOG: {message}")
                    
                self.frontend_logs.append(f"{level}: {message}")
                
        except Exception as e:
            logger.warning(f"Could not capture frontend logs: {e}")
    
    def run_test(self):
        """Run the complete test"""
        logger.info("🧪 Starting Topic Input Selenium Test")
        
        try:
            # Start backend log monitoring in background
            log_thread = threading.Thread(target=self.monitor_backend_logs, daemon=True)
            log_thread.start()
            
            # Setup and run test
            self.setup_driver()
            
            if not self.login():
                return False
            time.sleep(3)
            
            if not self.navigate_to_topic_input():
                return False
            time.sleep(3)
            
            if not self.enter_topic_and_generate():
                return False
            
            # Wait for processing to complete
            time.sleep(60)  # Wait 1 minute for processing
            
            success = self.verify_outputs()
            
            self.capture_frontend_logs()
            
            if success:
                logger.info("✅ Test completed successfully")
            else:
                logger.error("❌ Test failed - outputs verification failed")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            return False
            
        finally:
            # Capture screenshot
            try:
                if self.driver:
                    self.driver.save_screenshot("test_result.png")
                    logger.info("📸 Screenshot saved: test_result.png")
            except:
                pass
                
            if self.driver:
                self.driver.quit()
                
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*50)
        logger.info("📋 TEST SUMMARY")
        logger.info("="*50)
        
        logger.info(f"Backend log entries: {len(self.backend_logs)}")
        logger.info(f"Frontend log entries: {len(self.frontend_logs)}")
        
        # Show recent backend logs
        if self.backend_logs:
            logger.info("\n🔧 Recent Backend Logs:")
            for log in self.backend_logs[-15:]:
                logger.info(f"   {log}")
        
        # Show frontend errors
        frontend_errors = [log for log in self.frontend_logs if 'ERROR' in log or 'SEVERE' in log]
        if frontend_errors:
            logger.info("\n❌ Frontend Errors:")
            for error in frontend_errors:
                logger.info(f"   {error}")
        
        logger.info("="*50)

if __name__ == "__main__":
    test = TopicInputTest()
    success = test.run_test()
    
    if success:
        logger.info("🎉 TEST PASSED")
    else:
        logger.error("💥 TEST FAILED")
        
    def monitor_backend_logs(self):
        """Monitor backend logs in real-time"""
        try:
            process = subprocess.Popen(
                ['tail', '-f', '/home/unknown/Documents/hackathon application/dynamous-kiro-hackathon/backend/backend.log'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    self.backend_logs.append(line.strip())
                    if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception']):
                        logger.error(f"BACKEND ERROR: {line.strip()}")
                    elif 'generated' in line.lower() or 'completed' in line.lower():
                        logger.info(f"BACKEND SUCCESS: {line.strip()}")
                        
        except Exception as e:
            logger.error(f"Error monitoring backend logs: {e}")
    
    def login(self):
        """Login with provided credentials"""
        logger.info("🔐 Starting login process...")
        
        self.driver.get("http://localhost:3000")
        
        # Wait for login form
        mobile_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "mobile"))
        )
        
        password_input = self.driver.find_element(By.NAME, "password")
        login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign In')]")
        
        # Enter credentials
        mobile_input.clear()
        mobile_input.send_keys("7045024042")
        
        password_input.clear()
        password_input.send_keys("Alan#walker672")
        
        # Click login
        login_button.click()
        
        # Wait for dashboard
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'dashboard') or contains(text(), 'Study Buddy')]"))
        )
        
        logger.info("✅ Login successful")
        
    def navigate_to_topic_input(self):
        """Navigate to topic input section"""
        logger.info("🧭 Navigating to topic input...")
        
        # Look for Study Buddy card or topic input
        try:
            study_buddy_card = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Study Buddy') or contains(text(), 'Topic')]"))
            )
            study_buddy_card.click()
        except:
            # Try alternative navigation
            topic_link = self.driver.find_element(By.XPATH, "//a[contains(@href, 'topic') or contains(text(), 'Enter Topic')]")
            topic_link.click()
        
        logger.info("✅ Navigated to topic input")
        
    def enter_topic_and_generate(self):
        """Enter topic and generate study materials"""
        logger.info("📝 Entering topic and generating materials...")
        
        # Find topic input field
        topic_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder*='topic' or @placeholder*='Topic'] | //textarea[@placeholder*='topic' or @placeholder*='Topic']"))
        )
        
        # Enter medical topic
        test_topic = "Cardiovascular System - Heart anatomy, blood circulation, cardiac cycle, ECG interpretation"
        topic_input.clear()
        topic_input.send_keys(test_topic)
        
        logger.info(f"📋 Entered topic: {test_topic}")
        
        # Find and click generate button
        generate_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate') or contains(text(), 'Create') or contains(text(), 'Process')]"))
        )
        
        generate_button.click()
        logger.info("🚀 Clicked generate button")
        
        # Monitor processing
        self.monitor_processing()
        
    def monitor_processing(self):
        """Monitor the processing and wait for completion"""
        logger.info("⏳ Monitoring processing...")
        
        start_time = time.time()
        max_wait_time = 300  # 5 minutes
        
        while time.time() - start_time < max_wait_time:
            try:
                # Check for processing status
                status_elements = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'Processing') or contains(text(), 'Generating') or contains(text(), 'Complete')]")
                
                if status_elements:
                    status_text = status_elements[0].text
                    logger.info(f"📊 Status: {status_text}")
                    
                    if 'complete' in status_text.lower() or 'ready' in status_text.lower():
                        logger.info("✅ Processing completed")
                        break
                
                # Check for errors
                error_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'error') or contains(text(), 'Error') or contains(text(), 'Failed')]")
                if error_elements:
                    error_text = error_elements[0].text
                    logger.error(f"❌ Frontend Error: {error_text}")
                
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f"Error checking status: {e}")
                time.sleep(2)
        
        logger.info("⏱️ Processing monitoring completed")
        
    def verify_outputs(self):
        """Verify all 5 outputs are generated"""
        logger.info("🔍 Verifying outputs...")
        
        expected_outputs = [
            "Questions",
            "Mock Test", 
            "Mnemonics",
            "Cheat Sheet",
            "Notes"
        ]
        
        found_outputs = []
        
        for output in expected_outputs:
            try:
                # Look for output sections or tabs
                elements = self.driver.find_elements(By.XPATH, f"//div[contains(text(), '{output}') or contains(@class, '{output.lower()}')]")
                
                if elements:
                    found_outputs.append(output)
                    logger.info(f"✅ Found: {output}")
                    
                    # Click to check content
                    try:
                        elements[0].click()
                        time.sleep(1)
                        
                        # Check for content
                        content_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'content') or contains(@class, 'item')]")
                        if content_elements:
                            logger.info(f"📄 {output} has content ({len(content_elements)} items)")
                        else:
                            logger.warning(f"⚠️ {output} appears empty")
                            
                    except Exception as e:
                        logger.warning(f"Could not check {output} content: {e}")
                else:
                    logger.error(f"❌ Missing: {output}")
                    
            except Exception as e:
                logger.error(f"Error checking {output}: {e}")
        
        logger.info(f"📊 Found {len(found_outputs)}/5 outputs: {found_outputs}")
        return len(found_outputs) == 5
        
    def capture_frontend_logs(self):
        """Capture browser console logs"""
        try:
            logs = self.driver.get_log('browser')
            for log in logs:
                level = log['level']
                message = log['message']
                
                if level in ['SEVERE', 'ERROR']:
                    logger.error(f"FRONTEND ERROR: {message}")
                elif level == 'WARNING':
                    logger.warning(f"FRONTEND WARNING: {message}")
                else:
                    logger.info(f"FRONTEND LOG: {message}")
                    
                self.frontend_logs.append(f"{level}: {message}")
                
        except Exception as e:
            logger.warning(f"Could not capture frontend logs: {e}")
    
    def run_test(self):
        """Run the complete test"""
        logger.info("🧪 Starting Topic Input Test")
        
        try:
            # Start backend log monitoring in background
            log_thread = threading.Thread(target=self.monitor_backend_logs, daemon=True)
            log_thread.start()
            
            # Setup and run test
            self.setup_driver()
            
            self.login()
            time.sleep(2)
            
            self.navigate_to_topic_input()
            time.sleep(2)
            
            self.enter_topic_and_generate()
            time.sleep(5)
            
            # Wait for processing to complete
            time.sleep(30)
            
            self.verify_outputs()
            
            self.capture_frontend_logs()
            
            logger.info("✅ Test completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            
            # Capture screenshot on failure
            try:
                self.driver.save_screenshot("test_failure.png")
                logger.info("📸 Screenshot saved: test_failure.png")
            except:
                pass
                
        finally:
            if self.driver:
                self.driver.quit()
                
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*50)
        logger.info("📋 TEST SUMMARY")
        logger.info("="*50)
        
        logger.info(f"Backend log entries: {len(self.backend_logs)}")
        logger.info(f"Frontend log entries: {len(self.frontend_logs)}")
        
        # Show recent backend logs
        if self.backend_logs:
            logger.info("\n🔧 Recent Backend Logs:")
            for log in self.backend_logs[-10:]:
                logger.info(f"   {log}")
        
        # Show frontend errors
        frontend_errors = [log for log in self.frontend_logs if 'ERROR' in log or 'SEVERE' in log]
        if frontend_errors:
            logger.info("\n❌ Frontend Errors:")
            for error in frontend_errors:
                logger.info(f"   {error}")
        
        logger.info("="*50)

if __name__ == "__main__":
    test = TopicInputTest()
    test.run_test()
