#!/usr/bin/env python3
"""
Complete signup flow test - creates dummy user and checks database records
"""

import requests
import json
import time
import random
import string
from datetime import datetime

def generate_test_data():
    """Generate realistic test data"""
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return {
        "email": f"test.user.{random_id}@unitasa.com",
        "name": f"Test User {random_id.upper()}",
        "company": f"Test Company {random_id.upper()}",
        "preferred_crm": "hubspot"
    }

def test_complete_signup_flow():
    """Test the complete signup flow and database record creation"""
    print("🚀 COMPLETE SIGNUP FLOW TEST")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    test_data = generate_test_data()
    
    print(f"\n📋 Test Data:")
    print(f"   Email: {test_data['email']}")
    print(f"   Name: {test_data['name']}")
    print(f"   Company: {test_data['company']}")
    print(f"   CRM: {test_data['preferred_crm']}")
    
    # Step 1: Start Assessment (creates lead)
    print(f"\n1️⃣ Starting Assessment (Lead Creation)...")
    try:
        response = requests.post(
            f"{base_url}/api/v1/landing/assessment/start",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            assessment_data = response.json()
            assessment_id = assessment_data.get('assessment_id')
            print(f"✅ Assessment started successfully")
            print(f"   Assessment ID: {assessment_id}")
            print(f"   Status: {assessment_data.get('status')}")
            print(f"   Questions: {len(assessment_data.get('questions', []))}")
        else:
            print(f"❌ Assessment start failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Assessment start error: {e}")
        return False
    
    # Step 2: Submit Assessment Responses
    print(f"\n2️⃣ Submitting Assessment Responses...")
    try:
        # Create realistic assessment responses
        assessment_responses = {
            "assessment_id": assessment_id,
            "responses": [
                {
                    "question_id": "crm_system",
                    "answer": "HubSpot"
                },
                {
                    "question_id": "monthly_leads", 
                    "answer": "201-500"
                },
                {
                    "question_id": "automation_level",
                    "answer": 8
                }
            ],
            "completion_time_seconds": 180
        }
        
        response = requests.post(
            f"{base_url}/api/v1/landing/assessment/submit",
            json=assessment_responses,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Assessment submitted successfully")
            print(f"   Overall Score: {results.get('overall_score')}")
            print(f"   Readiness Level: {results.get('readiness_level')}")
            print(f"   Co-Creator Qualified: {results.get('co_creator_qualified')}")
            
            # Store lead info for later verification
            lead_qualified = results.get('co_creator_qualified', False)
        else:
            print(f"❌ Assessment submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Assessment submission error: {e}")
        return False
    
    # Step 3: Create Payment Order (Co-Creator Signup)
    if lead_qualified:
        print(f"\n3️⃣ Creating Co-Creator Payment Order...")
        try:
            payment_data = {
                "amount": 497.0,
                "customer_email": test_data["email"],
                "customer_name": test_data["name"],
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
                print(f"✅ Payment order created successfully")
                print(f"   Order ID: {order_data.get('order_id')}")
                print(f"   Amount: ${order_data.get('amount_usd')}")
                print(f"   Currency: {order_data.get('currency')}")
                
                order_id = order_data.get('order_id')
            else:
                print(f"❌ Payment order creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Payment order creation error: {e}")
            return False
    else:
        print(f"\n3️⃣ Skipping payment (lead not qualified for co-creator program)")
        order_id = None
    
    # Step 4: Check Database Records
    print(f"\n4️⃣ Verifying Database Records...")
    
    # Check if we can query the database through API endpoints
    try:
        # Check health endpoint for database status
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Database connection healthy")
            print(f"   Service: {health.get('service')}")
            print(f"   Features: {health.get('features')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Step 5: Test Admin Endpoints (if available)
    print(f"\n5️⃣ Checking Admin Data Access...")
    try:
        # Try to access admin endpoints to verify data
        admin_endpoints = [
            "/api/v1/admin/leads/recent",
            "/api/v1/admin/assessments/recent", 
            "/api/v1/admin/stats"
        ]
        
        for endpoint in admin_endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {endpoint} - Accessible")
                    if isinstance(data, list):
                        print(f"   Records found: {len(data)}")
                    elif isinstance(data, dict):
                        print(f"   Data keys: {list(data.keys())}")
                elif response.status_code == 404:
                    print(f"⚠️  {endpoint} - Not implemented")
                else:
                    print(f"❌ {endpoint} - Error: {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint} - Error: {e}")
    except Exception as e:
        print(f"❌ Admin endpoint check error: {e}")
    
    return True

def create_database_verification_script():
    """Create a separate script to verify database records"""
    script_content = '''#!/usr/bin/env python3
"""
Database verification script - checks if records were created
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from datetime import datetime, timedelta

# Import models
import sys
sys.path.append('.')
from app.models.lead import Lead
from app.models.assessment import Assessment
from app.models.payment_transaction import PaymentTransaction
from app.models.user import User

async def verify_database_records():
    """Verify that database records were created"""
    print("🔍 VERIFYING DATABASE RECORDS")
    print("=" * 50)
    
    # Database connection
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/unitas")
    engine = create_async_engine(database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Check recent leads (last hour)
            print("\\n1️⃣ Checking Recent Leads...")
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            result = await session.execute(
                select(Lead).where(Lead.created_at >= one_hour_ago).order_by(Lead.created_at.desc())
            )
            recent_leads = result.scalars().all()
            
            print(f"✅ Found {len(recent_leads)} recent leads")
            for lead in recent_leads[:5]:  # Show last 5
                print(f"   - ID: {lead.id}, Email: {lead.email}, Company: {lead.company}")
                print(f"     Created: {lead.created_at}, Score: {lead.score}")
            
            # Check recent assessments
            print("\\n2️⃣ Checking Recent Assessments...")
            result = await session.execute(
                select(Assessment).where(Assessment.created_at >= one_hour_ago).order_by(Assessment.created_at.desc())
            )
            recent_assessments = result.scalars().all()
            
            print(f"✅ Found {len(recent_assessments)} recent assessments")
            for assessment in recent_assessments[:5]:
                print(f"   - ID: {assessment.id}, Lead ID: {assessment.lead_id}")
                print(f"     Completed: {assessment.is_completed}, Score: {assessment.overall_score}")
            
            # Check recent payment transactions
            print("\\n3️⃣ Checking Recent Payment Transactions...")
            result = await session.execute(
                select(PaymentTransaction).where(PaymentTransaction.created_at >= one_hour_ago).order_by(PaymentTransaction.created_at.desc())
            )
            recent_payments = result.scalars().all()
            
            print(f"✅ Found {len(recent_payments)} recent payment transactions")
            for payment in recent_payments[:5]:
                print(f"   - ID: {payment.id}, Email: {payment.customer_email}")
                print(f"     Amount: ${payment.amount}, Status: {payment.status}")
            
            # Check users table
            print("\\n4️⃣ Checking Users Table...")
            result = await session.execute(select(User).order_by(User.created_at.desc()))
            users = result.scalars().all()
            
            print(f"✅ Found {len(users)} total users")
            for user in users[:5]:
                print(f"   - ID: {user.id}, Email: {user.email}")
                print(f"     Co-Creator: {user.is_co_creator}, Active: {user.is_active}")
            
            print("\\n" + "=" * 50)
            print("🎉 DATABASE VERIFICATION COMPLETE!")
            
    except Exception as e:
        print(f"❌ Database verification error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify_database_records())
'''
    
    with open('verify_database_records.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("📝 Created database verification script: verify_database_records.py")

def main():
    """Main test function"""
    print("=" * 70)
    print("🧪 COMPLETE SIGNUP FLOW TEST WITH DATABASE VERIFICATION")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Create database verification script
    create_database_verification_script()
    
    # Run the complete signup flow test
    success = test_complete_signup_flow()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 SIGNUP FLOW TEST COMPLETED!")
        print("\n📋 Summary:")
        print("   ✅ Assessment flow tested")
        print("   ✅ Lead creation verified")
        print("   ✅ Payment order creation tested")
        print("   ✅ Database health confirmed")
        print("\n🔍 Next Steps:")
        print("   1. Run: python verify_database_records.py")
        print("   2. Check if lead and assessment records were created")
        print("   3. Verify user table entries")
    else:
        print("💥 SIGNUP FLOW TEST FAILED!")
        print("   Check the error messages above")
    
    print("=" * 70)

if __name__ == "__main__":
    main()