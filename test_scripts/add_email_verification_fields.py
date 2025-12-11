#!/usr/bin/env python3
"""
Add email verification fields to users table
"""

import asyncio
import sys
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import get_settings

async def add_email_verification_fields():
    """Add email verification fields to users table"""
    settings = get_settings()
    
    # Use the correct database URL from .env
    database_url = "postgresql+asyncpg://postgres:aykha123@localhost:5432/unitas"
    print(f"Using database URL: {database_url}")
    
    # Create async engine
    engine = create_async_engine(
        database_url,
        echo=True
    )
    
    try:
        async with engine.begin() as conn:
            print("Adding email verification fields to users table...")
            
            # Add email verification fields
            await conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255) UNIQUE,
                ADD COLUMN IF NOT EXISTS email_verification_sent_at TIMESTAMP,
                ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP;
            """))
            
            # Create index on email_verification_token
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_users_email_verification_token 
                ON users(email_verification_token);
            """))
            
            print("✅ Email verification fields added successfully!")
            
            # Verify the changes
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('email_verification_token', 'email_verification_sent_at', 'email_verified_at')
                ORDER BY column_name;
            """))
            
            columns = result.fetchall()
            print("\n📋 Added columns:")
            for column in columns:
                print(f"  - {column[0]}: {column[1]} (nullable: {column[2]})")
                
    except Exception as e:
        print(f"❌ Error adding email verification fields: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_email_verification_fields())