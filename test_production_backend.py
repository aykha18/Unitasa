#!/usr/bin/env python3
"""
Test script to check production backend health and diagnose issues
"""

import os
import requests
import json
from datetime import datetime

def test_backend_health():
    """Test basic backend health"""
    try:
        print("[TEST] Testing backend health...")
        response = requests.get("https://unitasa.in/health", timeout=10)
        print(f"Health check status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Backend is healthy: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"[FAIL] Health check failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] Health check error: {e}")
        return False

def test_registration_endpoint():
    """Test user registration endpoint"""
    try:
        print("\n[TEST] Testing registration endpoint...")

        # Test data
        test_user = {
            "firstName": "Test",
            "lastName": "User",
            "email": f"test_{int(datetime.now().timestamp())}@example.com",
            "company": "Test Company",
            "password": "TestPassword123!",
            "confirmPassword": "TestPassword123!",
            "agreeToTerms": True
        }

        response = requests.post(
            "https://unitasa.in/api/v1/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        print(f"Registration status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Registration successful: {data.get('message', 'success')}")
            return True
        else:
            print(f"[FAIL] Registration failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw response: {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] Registration test error: {e}")
        return False

def test_cors_debug():
    """Test CORS debug endpoint"""
    try:
        print("\n[TEST] Testing CORS configuration...")
        response = requests.get("https://unitasa.in/cors-debug", timeout=10)
        print(f"CORS debug status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("[PASS] CORS configuration:")
            print(f"   Allowed origins: {data.get('allowed_origins', [])}")
            print(f"   Environment: {data.get('environment', 'unknown')}")
            return True
        else:
            print(f"[FAIL] CORS debug failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"[ERROR] CORS debug error: {e}")
        return False

def test_routes_debug():
    """Test routes debug endpoint"""
    try:
        print("\n[TEST] Testing routes configuration...")
        response = requests.get("https://unitasa.in/debug/routes", timeout=10)
        print(f"Routes debug status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Total routes: {data.get('total_routes', 0)}")

            # Check for auth routes
            routes = data.get('routes', [])
            auth_routes = [r for r in routes if 'auth' in r.get('path', '')]
            print(f"   Auth routes found: {len(auth_routes)}")

            for route in auth_routes:
                if 'register' in route.get('path', ''):
                    print(f"   [FOUND] Registration route: {route.get('path')} - {route.get('methods', [])}")

            return True
        else:
            print(f"[FAIL] Routes debug failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"[ERROR] Routes debug error: {e}")
        return False

def main():
    """Run all tests"""
    print("Production Backend Diagnostic Tool")
    print("=" * 50)

    results = []

    # Test basic health
    results.append(("Health Check", test_backend_health()))

    # Test CORS
    results.append(("CORS Config", test_cors_debug()))

    # Test routes
    results.append(("Routes Config", test_routes_debug()))

    # Test registration
    results.append(("User Registration", test_registration_endpoint()))

    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"   {test_name}: {status}")

    failed_tests = [name for name, success in results if not success]
    if failed_tests:
        print(f"\n[WARNING] Failed tests: {', '.join(failed_tests)}")
        print("\n[TROUBLESHOOTING] Suggestions:")
        print("   1. Check DATABASE_URL environment variable")
        print("   2. Check GOOGLE_CLIENT_ID environment variable")
        print("   3. Check email service configuration")
        print("   4. Check database connectivity")
        print("   5. Check server logs for detailed error messages")
    else:
        print("\n[SUCCESS] All tests passed! Backend is working correctly.")

if __name__ == "__main__":
    main()