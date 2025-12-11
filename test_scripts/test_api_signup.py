#!/usr/bin/env python3
"""
Test the signup API endpoint directly
"""

import requests
import json
from datetime import datetime

def test_signup_api():
    """Test the signup API endpoint"""
    
    print("🧪 Testing Signup API Endpoint")
    print("=" * 40)
    
    # Test data
    test_email = f"api.test.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
    
    signup_data = {
        "firstName": "API",
        "lastName": "Test",
        "email": test_email,
        "company": "Test Company",
        "password": "testpassword123",
        "confirmPassword": "testpassword123",
        "agreeToTerms": True
    }
    
    try:
        print(f"📝 Testing signup with email: {test_email}")
        
        # Make signup request
        response = requests.post(
            "http://localhost:8000/api/v1/auth/register",
            json=signup_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Signup successful!")
            print(f"   Message: {result.get('message')}")
            print(f"   User ID: {result.get('user_id')}")
            print(f"   Is Co-Creator: {result.get('is_co_creator')}")
            
            # Test email verification endpoint
            print(f"\n🔐 Testing email verification endpoint...")
            
            # We can't get the token from the API response, so let's test with a dummy token
            verify_response = requests.post(
                "http://localhost:8000/api/v1/auth/verify-email?token=dummy_token",
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📊 Verification Response Status: {verify_response.status_code}")
            
            if verify_response.status_code == 400:
                verify_result = verify_response.json()
                print(f"✅ Verification endpoint working (expected error): {verify_result.get('detail')}")
            else:
                print(f"❓ Unexpected verification response: {verify_response.text}")
                
        else:
            print(f"❌ Signup failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_signup_api()