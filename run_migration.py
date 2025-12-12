#!/usr/bin/env python3
"""
Script to run database migrations on production
"""

import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

# Load environment variables
load_dotenv()

def get_database_url():
    """Get database URL from environment"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")

    # Ensure it's async
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

    return DATABASE_URL

async def run_migration():
    """Run the user name fields migration"""
    print("Starting database migration: Add first_name and last_name columns")

    try:
        # Get database URL
        database_url = get_database_url()
        print(f"Connecting to database...")

        # Create engine
        engine = create_async_engine(database_url, echo=True)

        async with engine.begin() as conn:
            print("Connected to database successfully")

            # Migration SQL statements
            migration_sql = [
                # Add first_name column
                """
                ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);
                """,

                # Add last_name column
                """
                ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);
                """,

                # Populate existing records
                """
                UPDATE users
                SET
                    first_name = CASE
                        WHEN full_name IS NOT NULL AND POSITION(' ' IN full_name) > 0
                        THEN TRIM(SPLIT_PART(full_name, ' ', 1))
                        ELSE ''
                    END,
                    last_name = CASE
                        WHEN full_name IS NOT NULL AND POSITION(' ' IN full_name) > 0
                        THEN TRIM(SUBSTRING(full_name FROM POSITION(' ' IN full_name) + 1))
                        ELSE ''
                    END
                WHERE first_name IS NULL OR last_name IS NULL;
                """
            ]

            # Execute migration
            for i, sql in enumerate(migration_sql, 1):
                print(f"Executing migration step {i}...")
                await conn.execute(text(sql))
                print(f"Step {i} completed")

            print("Migration completed successfully!")

            # Verify the migration
            print("Verifying migration...")
            result = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name IN ('first_name', 'last_name');"))
            columns = result.fetchall()

            if len(columns) >= 2:
                print("✅ Migration verified: first_name and last_name columns exist")
            else:
                print("⚠️  Migration may not have completed properly")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

    finally:
        if 'engine' in locals():
            await engine.dispose()

if __name__ == "__main__":
    print("Database Migration Tool")
    print("=" * 50)
    print("This script will add first_name and last_name columns to the users table")
    print()

    # Confirm before running
    confirm = input("Are you sure you want to run this migration? (yes/no): ").lower().strip()
    if confirm not in ['yes', 'y']:
        print("Migration cancelled")
        exit(0)

    # Run the migration
    asyncio.run(run_migration())