#!/usr/bin/env python3
"""
Simple login test to debug the issue
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Test credentials
MOBILE_NUMBER = "7045024042"
PASSWORD = "Alan#walker672"
FRONTEND_URL = "http://localhost:3000"

def test_login():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    wait = WebDriverWait(driver, 20)
    
    try:
        print("Navigating to login page...")
        driver.get(f"{FRONTEND_URL}/login")
        time.sleep(3)
        
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Check if elements exist
        try:
            mobile_input = driver.find_element(By.NAME, "mobile")
            print("✅ Mobile input found")
        except:
            print("❌ Mobile input not found")
            
        try:
            password_input = driver.find_element(By.NAME, "password")
            print("✅ Password input found")
        except:
            print("❌ Password input not found")
            
        try:
            login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
            print("✅ Login button found")
        except:
            print("❌ Login button not found")
            
        # Try to fill and submit
        mobile_input = wait.until(EC.presence_of_element_located((By.NAME, "mobile")))
        mobile_input.clear()
        mobile_input.send_keys(MOBILE_NUMBER)
        print("Mobile number entered")
        
        password_input = driver.find_element(By.NAME, "password")
        password_input.clear()
        password_input.send_keys(PASSWORD)
        print("Password entered")
        
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
        login_button.click()
        print("Login button clicked")
        
        time.sleep(5)
        
        print(f"After login URL: {driver.current_url}")
        
        # Check for any error messages
        page_text = driver.find_element(By.TAG_NAME, "body").text
        if "error" in page_text.lower() or "invalid" in page_text.lower():
            print(f"Error found: {page_text[:200]}")
        
        if "/study-buddy" in driver.current_url:
            print("✅ Login successful - redirected to study-buddy")
        else:
            print("❌ Login failed - not redirected")
            
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    test_login()
