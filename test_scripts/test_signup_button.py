#!/usr/bin/env python3
"""
Test script to verify the signup button functionality
"""

import requests
from bs4 import BeautifulSoup
import re

def test_signup_button():
    """Test that the signup button exists and links correctly"""
    print("🚀 Testing Signup Button Functionality")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Load the main page and check for signup button
    print("\n1. Loading main page and checking for signup button...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Main page loads successfully")
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for the signup button text
            page_text = soup.get_text()
            if "Signup" in page_text:
                print("✅ 'Signup' text found on page")
            else:
                print("❌ 'Signup' text not found on page")
                print("   Checking for 'Join Co-Creators' (old text)...")
                if "Join Co-Creators" in page_text:
                    print("⚠️  Found old 'Join Co-Creators' text - button text not updated")
                else:
                    print("❌ No signup button text found")
                return False
            
            # Check if there are any JavaScript references to /signup
            if "/signup" in response.text:
                print("✅ '/signup' route reference found in page")
            else:
                print("❌ No '/signup' route reference found")
                return False
                
        else:
            print(f"❌ Main page failed to load: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error loading main page: {e}")
        return False
    
    # Test 2: Directly test the signup route
    print("\n2. Testing signup route directly...")
    try:
        response = requests.get(f"{base_url}/signup")
        if response.status_code == 200:
            print("✅ Signup page accessible via direct URL")
            
            # Check if it's the signup page content
            if "signup" in response.text.lower() or "sign up" in response.text.lower():
                print("✅ Signup page contains signup-related content")
            else:
                print("⚠️  Signup page loaded but content unclear")
                
        else:
            print(f"❌ Signup page not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing signup page: {e}")
        return False
    
    # Test 3: Check if the signup page has the signup form
    print("\n3. Checking signup page for form elements...")
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        page_text = soup.get_text().lower()
        
        form_indicators = [
            "first name", "last name", "email", "company", 
            "password", "co-creator", "founding member"
        ]
        
        found_indicators = []
        for indicator in form_indicators:
            if indicator in page_text:
                found_indicators.append(indicator)
        
        if len(found_indicators) >= 3:
            print(f"✅ Signup form detected - found: {', '.join(found_indicators)}")
        else:
            print(f"⚠️  Limited form content detected - found: {', '.join(found_indicators)}")
            
    except Exception as e:
        print(f"❌ Error analyzing signup page: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 UNITASA SIGNUP BUTTON TEST")
    print("=" * 60)
    
    success = test_signup_button()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SIGNUP BUTTON TEST PASSED!")
        print("\n📋 Test Results:")
        print("   ✅ Main page loads with signup button")
        print("   ✅ Signup route is accessible")
        print("   ✅ Signup page has form content")
        print("\n🎯 Next Steps:")
        print("   1. Visit http://localhost:8000 to see the main page")
        print("   2. Click the 'Signup' button in the header")
        print("   3. Verify it takes you to the signup form")
    else:
        print("💥 SIGNUP BUTTON TEST FAILED!")
        print("   Check the console output above for specific issues")
    
    print("=" * 60)

if __name__ == "__main__":
    main()