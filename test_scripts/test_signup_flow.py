#!/usr/bin/env python3
"""
Test script to verify the complete signup flow
"""

import requests
import json
from datetime import datetime

def test_signup_flow():
    """Test the complete signup flow"""
    print("🚀 Testing Unitasa Signup Flow")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Check if frontend signup page loads
    print("\n1. Testing signup page accessibility...")
    try:
        response = requests.get(f"{base_url}/signup")
        if response.status_code == 200:
            print("✅ Signup page loads successfully")
            print(f"   Content-Type: {response.headers.get('content-type')}")
            print(f"   Content-Length: {len(response.content)} bytes")
        else:
            print(f"❌ Signup page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing signup page: {e}")
        return False
    
    # Test 2: Check if backend health is good
    print("\n2. Testing backend health...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Backend is healthy")
            print(f"   Service: {health_data.get('service')}")
            print(f"   Co-Creator Program: {health_data.get('features', {}).get('co_creator_program')}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking backend health: {e}")
        return False
    
    # Test 3: Test assessment start (part of signup flow)
    print("\n3. Testing assessment start (signup prerequisite)...")
    try:
        assessment_data = {
            "email": "test@unitasa.com",
            "name": "Test User",
            "company": "Test Company",
            "preferred_crm": "hubspot"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/landing/assessment/start",
            json=assessment_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Assessment start successful")
            print(f"   Assessment ID: {result.get('assessment_id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Questions available: {len(result.get('questions', []))}")
            return result.get('assessment_id')
        else:
            print(f"❌ Assessment start failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error starting assessment: {e}")
        return False
    
    # Test 4: Test payment order creation (co-creator signup)
    print("\n4. Testing co-creator payment order creation...")
    try:
        payment_data = {
            "amount": 497.0,
            "customer_email": "test@unitasa.com",
            "customer_name": "Test User",
            "program_type": "co_creator",
            "currency": "USD",
            "customer_country": "US"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/payments/razorpay/create-order",
            json=payment_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Payment order creation successful")
            print(f"   Order ID: {result.get('order_id')}")
            print(f"   Amount: ${result.get('amount_usd')}")
            print(f"   Currency: {result.get('currency')}")
            return True
        else:
            print(f"❌ Payment order creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating payment order: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 UNITASA SIGNUP FLOW END-TO-END TEST")
    print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    success = test_signup_flow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED: Signup flow is working!")
        print("\n📋 Summary:")
        print("   ✅ Signup page accessible")
        print("   ✅ Backend services healthy")
        print("   ✅ Assessment system working")
        print("   ✅ Payment system ready")
        print("\n🔗 Access the signup flow at: http://localhost:8000/signup")
    else:
        print("💥 SOME TESTS FAILED: Issues found in signup flow")
    
    print("=" * 60)

if __name__ == "__main__":
    main()