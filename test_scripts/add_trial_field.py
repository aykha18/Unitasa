#!/usr/bin/env python3
"""
Add trial_end_date field to users table
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def add_trial_field():
    """Add trial_end_date column to users table"""
    print("🔧 Adding trial_end_date column to users table...")
    
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:aykha123@localhost:5432/unitas")
    engine = create_async_engine(database_url)
    
    try:
        async with engine.begin() as conn:
            # Check if column exists first
            check_column_sql = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'trial_end_date';
            """
            
            result = await conn.execute(text(check_column_sql))
            existing_columns = [row[0] for row in result.fetchall()]
            
            # Add trial_end_date if it doesn't exist
            if 'trial_end_date' not in existing_columns:
                print("Adding trial_end_date column...")
                await conn.execute(text("ALTER TABLE users ADD COLUMN trial_end_date TIMESTAMP;"))
                print("✅ Added trial_end_date column")
            else:
                print("✅ trial_end_date column already exists")
            
            print("🎉 Database schema updated successfully!")
            
    except Exception as e:
        print(f"❌ Error updating database schema: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_trial_field())