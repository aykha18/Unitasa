#!/usr/bin/env python3
"""
Create a test user for login testing
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_database
from app.models.user import User
from app.core.jwt_handler import get_password_hash

async def create_test_user():
    """Create a test user"""
    try:
        # Use environment variables for test user credentials
        test_email = os.getenv("TEST_USER_EMAIL", "test@example.com")
        test_password = os.getenv("TEST_USER_PASSWORD", "testpassword123")
        test_name = os.getenv("TEST_USER_NAME", "Test User")

        print(f"Creating test user: {test_email}")
        engine, SessionLocal = init_database()

        async with SessionLocal() as session:
            # Check if user already exists
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.email == test_email))
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print('✅ User already exists!')
                print(f'Email: {existing_user.email}')
                print(f'Active: {existing_user.is_active}')
                return

            # Create new user
            hashed_password = get_password_hash(test_password)
            user = User(
                email=test_email,
                hashed_password=hashed_password,
                full_name=test_name,
                first_name=test_name.split()[0] if test_name else 'Test',
                last_name=' '.join(test_name.split()[1:]) if test_name and len(test_name.split()) > 1 else 'User',
                company='Test Company',
                is_active=True,
                is_verified=True,
                subscription_tier='free_trial',
                is_trial_active=True
            )

            session.add(user)
            await session.commit()

            print('✅ Test user created successfully!')
            print(f'Email: {user.email}')
            print(f'Password: {test_password}')
            print(f'User ID: {user.id}')

    except Exception as e:
        print(f'❌ Error creating user: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_test_user())