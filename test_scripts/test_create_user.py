#!/usr/bin/env python3
"""
Create a test user for login testing
"""

import requests
import json

def create_test_user():
    """Create a test user"""

    print("Creating test user...")
    print("=" * 40)

    user_data = {
        "firstName": "Test",
        "lastName": "User",
        "email": "test2@example.com",
        "company": "Test Company",
        "password": "password",
        "confirmPassword": "password",
        "agreeToTerms": True
    }

    try:
        response = requests.post(
            "http://localhost:8001/api/v1/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )

        print(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"User created successfully!")
            print(f"User ID: {result.get('user_id')}")
            print(f"Message: {result.get('message')}")
        else:
            try:
                error_result = response.json()
                print(f"Error: {error_result.get('detail', response.text)}")
            except:
                print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("Could not connect to the API server. Make sure it's running on http://localhost:8001")
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    create_test_user()