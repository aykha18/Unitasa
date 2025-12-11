#!/usr/bin/env python3
"""
Add missing columns to users table
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def add_user_columns():
    """Add first_name and last_name columns to users table"""
    print("🔧 Adding missing columns to users table...")
    
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:aykha123@localhost:5432/unitas")
    engine = create_async_engine(database_url)
    
    try:
        async with engine.begin() as conn:
            # Check if columns exist first
            check_columns_sql = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('first_name', 'last_name');
            """
            
            result = await conn.execute(text(check_columns_sql))
            existing_columns = [row[0] for row in result.fetchall()]
            
            print(f"Existing columns: {existing_columns}")
            
            # Add first_name if it doesn't exist
            if 'first_name' not in existing_columns:
                print("Adding first_name column...")
                await conn.execute(text("ALTER TABLE users ADD COLUMN first_name VARCHAR(100);"))
                print("✅ Added first_name column")
            else:
                print("✅ first_name column already exists")
            
            # Add last_name if it doesn't exist
            if 'last_name' not in existing_columns:
                print("Adding last_name column...")
                await conn.execute(text("ALTER TABLE users ADD COLUMN last_name VARCHAR(100);"))
                print("✅ Added last_name column")
            else:
                print("✅ last_name column already exists")
            
            print("🎉 Database schema updated successfully!")
            
    except Exception as e:
        print(f"❌ Error updating database schema: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_user_columns())