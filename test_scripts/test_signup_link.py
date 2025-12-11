#!/usr/bin/env python3
"""
Test script to verify landing page loads and signup link works
"""

import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def test_landing_page_and_signup_link():
    """Test that landing page loads and signup link navigates correctly"""

    # Setup Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
        print("🚀 Starting test: Landing page and signup link functionality")

        # Step 1: Load the landing page
        print("📄 Loading landing page...")
        driver.get("http://localhost:3000")

        # Wait for page to load (look for header element)
        wait = WebDriverWait(driver, 10)
        header = wait.until(EC.presence_of_element_located((By.TAG_NAME, "header")))
        print("✅ Landing page loaded successfully")

        # Step 2: Find and click the "Join Co-Creators" button
        print("🔍 Looking for 'Join Co-Creators' button...")
        signup_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Join Co-Creators')]")

        if not signup_buttons:
            print("❌ ERROR: No 'Join Co-Creators' buttons found!")
            return False

        print(f"✅ Found {len(signup_buttons)} 'Join Co-Creators' button(s)")

        # Click the first (desktop) button
        print("🖱️  Clicking 'Join Co-Creators' button...")
        signup_buttons[0].click()

        # Step 3: Wait for navigation and verify we're on signup page
        print("⏳ Waiting for navigation to signup page...")
        time.sleep(2)  # Give time for navigation

        current_url = driver.current_url
        print(f"📍 Current URL: {current_url}")

        if "/signup" in current_url:
            print("✅ SUCCESS: Navigated to signup page correctly!")
            return True
        else:
            print(f"❌ ERROR: Expected to navigate to signup page, but got: {current_url}")
            return False

    except Exception as e:
        print(f"❌ ERROR during test: {str(e)}")
        return False

    finally:
        print("🧹 Cleaning up...")
        driver.quit()

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 UNITASA LANDING PAGE & SIGNUP LINK TEST")
    print("=" * 60)

    # Check if app is running
    try:
        import requests
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code != 200:
            print("❌ ERROR: Frontend app is not running on http://localhost:3000")
            print("   Please start the app with: cd frontend && npm start")
            sys.exit(1)
    except:
        print("❌ ERROR: Cannot connect to frontend app on http://localhost:3000")
        print("   Please start the app with: cd frontend && npm start")
        sys.exit(1)

    # Run the test
    success = test_landing_page_and_signup_link()

    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST PASSED: Landing page loads and signup link works!")
        sys.exit(0)
    else:
        print("💥 TEST FAILED: Issues found with landing page or signup link")
        sys.exit(1)

if __name__ == "__main__":
    main()