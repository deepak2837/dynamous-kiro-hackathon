#!/usr/bin/env python3
"""
Selenium test script to login and test file upload
"""
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_file_upload():
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("🚀 Starting Selenium test...")
        
        # Navigate to the app
        driver.get("http://localhost:3000")
        print("✅ Navigated to app")
        
        # Wait for login form and login
        wait = WebDriverWait(driver, 10)
        
        # Find and fill mobile number
        mobile_input = wait.until(EC.presence_of_element_located((By.NAME, "mobile_number")))
        mobile_input.clear()
        mobile_input.send_keys("7045024042")
        print("✅ Entered mobile number")
        
        # Find and fill password
        password_input = driver.find_element(By.NAME, "password")
        password_input.clear()
        password_input.send_keys("Alan#walker672")
        print("✅ Entered password")
        
        # Click login button
        login_button = driver.find_element(By.TYPE, "submit")
        login_button.click()
        print("✅ Clicked login")
        
        # Wait for dashboard
        time.sleep(3)
        
        # Navigate to Study Buddy
        study_buddy_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Study Buddy")))
        study_buddy_link.click()
        print("✅ Navigated to Study Buddy")
        
        # Wait for file upload area
        time.sleep(2)
        
        # Find file input
        file_input = wait.until(EC.presence_of_element_located((By.TYPE, "file")))
        
        # Upload the PDF file
        pdf_path = "/home/unknown/Downloads/Text-to-PDF-r1p.pdf"
        if os.path.exists(pdf_path):
            file_input.send_keys(pdf_path)
            print(f"✅ Uploaded file: {pdf_path}")
        else:
            print(f"❌ File not found: {pdf_path}")
            return
        
        # Wait a moment for file to be processed
        time.sleep(2)
        
        # Find and click process button
        process_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Process') or contains(text(), 'Upload')]")))
        process_button.click()
        print("✅ Clicked process button")
        
        # Wait for processing to start
        time.sleep(5)
        
        # Check for any error messages
        try:
            error_element = driver.find_element(By.XPATH, "//*[contains(text(), 'error') or contains(text(), 'Error') or contains(text(), 'failed')]")
            print(f"❌ Error found: {error_element.text}")
        except:
            print("✅ No error messages found")
        
        # Wait to see processing status
        print("⏳ Waiting for processing...")
        time.sleep(10)
        
        print("✅ Test completed successfully")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        
        # Take screenshot for debugging
        driver.save_screenshot("test_error.png")
        print("📸 Screenshot saved as test_error.png")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_file_upload()
