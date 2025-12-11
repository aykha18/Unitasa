#!/usr/bin/env python3
"""
Test the complete email verification signup flow
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.v1.user_registration import register_user, verify_email, UserRegistrationRequest
from app.core.database import get_db
from app.models.user import User
from sqlalchemy import select

async def test_email_verification_signup():
    """Test the complete email verification signup flow"""
    
    print("🧪 Testing Email Verification Signup Flow")
    print("=" * 50)
    
    # Test data
    test_email = f"test.user.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
    
    registration_data = UserRegistrationRequest(
        firstName="Test",
        lastName="User",
        email=test_email,
        company="Test Company",
        password="testpassword123",
        confirmPassword="testpassword123",
        agreeToTerms=True
    )
    
    try:
        # Get database session
        async for db in get_db():
            print(f"📝 Step 1: Registering user with email: {test_email}")
            
            # Register user
            result = await register_user(registration_data, db)
            
            if result.success:
                print(f"✅ Registration successful: {result.message}")
                print(f"   User ID: {result.user_id}")
                
                # Check user in database
                user_result = await db.execute(select(User).where(User.id == result.user_id))
                user = user_result.scalar_one_or_none()
                
                if user:
                    print(f"📧 Step 2: Checking email verification token")
                    print(f"   Email verified: {user.is_verified}")
                    print(f"   Verification token: {user.email_verification_token[:20]}..." if user.email_verification_token else "None")
                    print(f"   Trial end date: {user.trial_end_date}")
                    print(f"   Subscription tier: {user.subscription_tier}")
                    
                    if user.email_verification_token:
                        print(f"🔐 Step 3: Testing email verification")
                        
                        # Test email verification
                        verify_result = await verify_email(user.email_verification_token, db)
                        
                        if verify_result.get("success"):
                            print(f"✅ Email verification successful: {verify_result['message']}")
                            
                            # Check user status after verification
                            await db.refresh(user)
                            print(f"   Email verified after verification: {user.is_verified}")
                            print(f"   Verification token cleared: {user.email_verification_token is None}")
                            
                        else:
                            print(f"❌ Email verification failed: {verify_result}")
                    else:
                        print("❌ No verification token generated")
                        
                else:
                    print("❌ User not found in database after registration")
                    
            else:
                print(f"❌ Registration failed: {result.message}")
                
            break  # Exit the async generator
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_email_verification_signup())