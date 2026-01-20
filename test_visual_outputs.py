#!/usr/bin/env python3
"""
Visual Output Test - Check if actual content is displayed on screen
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

MOBILE_NUMBER = "7045024042"
PASSWORD = "Alan#walker672"
FRONTEND_URL = "http://localhost:3000"
TEST_FILE_PATH = "/home/unknown/Downloads/Text-to-PDF-r1p.pdf"

def test_visual_outputs():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    wait = WebDriverWait(driver, 20)
    
    try:
        print("🔐 Logging in...")
        driver.get(f"{FRONTEND_URL}/login")
        time.sleep(2)
        
        mobile_input = wait.until(EC.presence_of_element_located((By.NAME, "mobile")))
        mobile_input.send_keys(MOBILE_NUMBER)
        
        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(PASSWORD)
        
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
        login_button.click()
        time.sleep(3)
        
        print("📋 Checking existing sessions...")
        driver.get(f"{FRONTEND_URL}/study-buddy")
        time.sleep(3)
        
        # Look for existing sessions in history
        session_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'cursor-pointer')] | //button[contains(text(), 'Session')]")
        
        if session_elements:
            print(f"Found {len(session_elements)} existing sessions")
            # Click on the first session
            session_elements[0].click()
            time.sleep(3)
            print("Clicked on existing session")
        else:
            print("No existing sessions found, creating new one...")
            # Upload new file
            file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
            file_input.send_keys(TEST_FILE_PATH)
            
            upload_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Upload') or contains(text(), 'Process')]")))
            upload_button.click()
            
            print("⏳ Waiting for processing...")
            time.sleep(10)
        
        print("🔍 Checking actual content on screen...")
        
        # Take screenshot
        driver.save_screenshot("visual_test_output.png")
        print("Screenshot saved: visual_test_output.png")
        
        # Check page content
        page_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"Page contains 'Results': {'Results' in page_text}")
        print(f"Page contains 'Questions': {'Questions' in page_text}")
        print(f"Page contains 'Mock': {'Mock' in page_text}")
        print(f"Page contains 'ResultsViewer': {'ResultsViewer' in page_text}")
        
        # Check for progress indicators
        progress_elements = driver.find_elements(By.XPATH, "//div[contains(text(), '1') and contains(text(), 'Upload')] | //div[contains(text(), '2') and contains(text(), 'Process')] | //div[contains(text(), '3') and contains(text(), 'Results')]")
        print(f"Found {len(progress_elements)} progress indicators")
        
        for elem in progress_elements:
            print(f"  Progress: {elem.text}")
        
        # Check for tabs
        tabs = driver.find_elements(By.XPATH, "//button[contains(text(), 'Questions') or contains(text(), 'Mock') or contains(text(), 'Mnemonic')]")
        print(f"Found {len(tabs)} tabs")
        
        for i, tab in enumerate(tabs):
            print(f"\n--- Clicking Tab {i+1}: {tab.text} ---")
            tab.click()
            time.sleep(2)
            
            # Get visible content
            content_area = driver.find_element(By.TAG_NAME, "body")
            visible_text = content_area.text
            
            # Check for actual question content
            if "What is" in visible_text or "Which" in visible_text or "How" in visible_text:
                print("✅ Found actual question content")
                # Print first few lines of content
                lines = visible_text.split('\n')
                for line in lines:
                    if any(word in line for word in ["What is", "Which", "How", "Q1", "Q2"]):
                        print(f"  Content: {line[:100]}...")
                        break
            else:
                print("❌ No actual question content found")
                print(f"  Page text sample: {visible_text[:200]}...")
            
            driver.save_screenshot(f"tab_{i+1}_content.png")
            print(f"Screenshot saved: tab_{i+1}_content.png")
        
        # Check if content is actually empty
        page_source = driver.page_source
        if "No questions generated" in page_source or "No content" in page_source:
            print("❌ Content is explicitly empty")
        elif len(page_source) < 5000:  # Very small page
            print("❌ Page seems too small - likely empty")
        else:
            print("✅ Page has substantial content")
            
    except Exception as e:
        print(f"Error: {e}")
        driver.save_screenshot("error_visual_test.png")
        
    finally:
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    test_visual_outputs()
