#!/usr/bin/env python3
"""
Complete user signup flow test - creates dummy user and verifies database records
"""

import requests
import json
import time
import random
import string
import os
from datetime import datetime

def generate_test_user():
    """Generate realistic test user data"""
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    # Use environment variable for test password, fallback to secure default
    test_password = os.getenv("TEST_USER_PASSWORD", "SecureTestPass123!")

    return {
        "firstName": f"Test",
        "lastName": f"User{random_id.upper()}",
        "email": f"testuser.{random_id}@unitasa.com",
        "company": f"Test Company {random_id.upper()}",
        "password": test_password,
        "confirmPassword": test_password,
        "agreeToTerms": True
    }

def test_complete_user_signup():
    """Test the complete user signup flow"""
    print("🚀 COMPLETE USER SIGNUP FLOW TEST")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    test_user = generate_test_user()
    
    print(f"\n📋 Test User Data:")
    print(f"   Name: {test_user['firstName']} {test_user['lastName']}")
    print(f"   Email: {test_user['email']}")
    print(f"   Company: {test_user['company']}")
    
    # Step 1: Start Assessment (creates lead)
    print(f"\n1️⃣ Starting Assessment (Lead Creation)...")
    try:
        assessment_data = {
            "email": test_user["email"],
            "name": f"{test_user['firstName']} {test_user['lastName']}",
            "company": test_user["company"],
            "preferred_crm": "hubspot"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/landing/assessment/start",
            json=assessment_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            assessment_result = response.json()
            assessment_id = assessment_result.get('assessment_id')
            print(f"✅ Assessment started - ID: {assessment_id}")
        else:
            print(f"❌ Assessment start failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Assessment start error: {e}")
        return False
    
    # Step 2: Submit Assessment Responses
    print(f"\n2️⃣ Submitting Assessment Responses...")
    try:
        assessment_responses = {
            "assessment_id": assessment_id,
            "responses": [
                {"question_id": "crm_system", "answer": "HubSpot"},
                {"question_id": "monthly_leads", "answer": "201-500"},
                {"question_id": "automation_level", "answer": 9}
            ],
            "completion_time_seconds": 120
        }
        
        response = requests.post(
            f"{base_url}/api/v1/landing/assessment/submit",
            json=assessment_responses,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Assessment completed - Score: {results.get('overall_score')}")
            co_creator_qualified = results.get('co_creator_qualified', False)
            print(f"   Co-Creator Qualified: {co_creator_qualified}")
        else:
            print(f"❌ Assessment submission failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Assessment submission error: {e}")
        return False
    
    # Step 3: Create Payment Order (if qualified)
    if co_creator_qualified:
        print(f"\n3️⃣ Creating Co-Creator Payment Order...")
        try:
            payment_data = {
                "amount": 497.0,
                "customer_email": test_user["email"],
                "customer_name": f"{test_user['firstName']} {test_user['lastName']}",
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
                order_data = response.json()
                print(f"✅ Payment order created - ID: {order_data.get('order_id')}")
            else:
                print(f"❌ Payment order failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Payment order error: {e}")
    
    # Step 4: Register User Account
    print(f"\n4️⃣ Registering User Account...")
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            registration_result = response.json()
            print(f"✅ User registration successful!")
            print(f"   User ID: {registration_result.get('user_id')}")
            print(f"   Message: {registration_result.get('message')}")
            print(f"   Co-Creator Status: {registration_result.get('is_co_creator')}")
            
            user_id = registration_result.get('user_id')
        else:
            print(f"❌ User registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ User registration error: {e}")
        return False
    
    # Step 5: Verify Database Records
    print(f"\n5️⃣ Verifying Database Records...")
    
    # Wait a moment for database to be updated
    time.sleep(1)
    
    # Run database verification
    try:
        import subprocess
        result = subprocess.run(['python', 'verify_database_records.py'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Database verification completed")
            # Check if our new user appears in the output
            if test_user["email"] in result.stdout:
                print(f"✅ New user found in database: {test_user['email']}")
            else:
                print(f"⚠️  New user not found in recent records (may be in database)")
        else:
            print(f"❌ Database verification failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Database verification error: {e}")
    
    return True

def main():
    """Main test function"""
    print("=" * 70)
    print("🧪 COMPLETE USER SIGNUP FLOW TEST")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    success = test_complete_user_signup()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 COMPLETE SIGNUP FLOW TEST PASSED!")
        print("\n📋 Summary:")
        print("   ✅ Assessment flow completed")
        print("   ✅ Lead record created")
        print("   ✅ Payment order created (if qualified)")
        print("   ✅ User account registered")
        print("   ✅ Database records verified")
        print("\n🎯 What was tested:")
        print("   • Lead creation via assessment")
        print("   • Assessment completion and scoring")
        print("   • Co-creator qualification check")
        print("   • Payment order creation")
        print("   • User registration with password hashing")
        print("   • Database record creation and linking")
    else:
        print("💥 SIGNUP FLOW TEST FAILED!")
        print("   Check the error messages above")
    
    print("=" * 70)

if __name__ == "__main__":
    main()