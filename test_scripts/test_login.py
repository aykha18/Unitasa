#!/usr/bin/env python3
"""
Test the login API endpoint with the provided credentials
"""

import requests
import json

def test_login():
    """Test the login API endpoint"""

    print("Testing Login API Endpoint")
    print("=" * 40)

    login_data = {
        "email": "newtest@example.com",
        "password": "testpassword123",
        "remember_me": False
    }

    try:
        print(f"Testing login with email: {login_data['email']}")

        # Make login request
        response = requests.post(
            "http://localhost:8001/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )

        print(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Login successful!")
            print(f"   Message: {result.get('message')}")
            print(f"   User: {result.get('user', {}).get('email')}")
            print(f"   Token Type: {result.get('token_type')}")
        else:
            print(f"Login failed: {response.status_code}")
            try:
                error_result = response.json()
                print(f"   Error: {error_result.get('detail', response.text)}")
            except:
                print(f"   Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("Could not connect to the API server. Make sure it's running on http://localhost:8001")
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    test_login()