#!/usr/bin/env python3
"""
Comprehensive migration to add all missing columns to users table
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

async def run_user_table_migration():
    """Add all missing columns to users table"""
    # Production database URL
    prod_url = "postgresql://postgres:eNUAZiYjbGNTiHfnNeFbUCPMdAugvujA@switchback.proxy.rlwy.net:24843/railway"

    print("Starting comprehensive users table migration...")
    print(f"Database: {prod_url.split('@')[1] if '@' in prod_url else 'Connected'}")

    try:
        engine = create_async_engine(prod_url, echo=True)

        async with engine.begin() as conn:
            print("Connected to database successfully")

            # Migration SQL statements for all missing columns
            migration_sql = [
                # Add name columns
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);",

                # Add subscription and trial columns
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(50) DEFAULT 'free_trial';",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS monthly_request_limit INTEGER DEFAULT 1000;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS requests_this_month INTEGER DEFAULT 0;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS trial_end_date TIMESTAMP;",

                # Add co-creator columns
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_co_creator BOOLEAN DEFAULT FALSE;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS co_creator_joined_at TIMESTAMP;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS lifetime_access BOOLEAN DEFAULT FALSE;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS co_creator_seat_number INTEGER;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS co_creator_benefits TEXT;",

                # Add email verification columns
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255);",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_sent_at TIMESTAMP;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP;",

                # Add profile columns
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS website VARCHAR(255);",

                # Add API key column
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS api_key VARCHAR(255);",

                # Populate first_name and last_name from existing full_name data
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
                """,

                # Set default trial_end_date for existing users (15 days from now)
                """
                UPDATE users
                SET trial_end_date = CURRENT_TIMESTAMP + INTERVAL '15 days'
                WHERE trial_end_date IS NULL AND subscription_tier = 'free_trial';
                """
            ]

            # Execute migration
            for i, sql in enumerate(migration_sql, 1):
                print(f"Executing migration step {i}/{len(migration_sql)}...")
                await conn.execute(text(sql))
                print(f"Step {i} completed")

            print("Migration completed successfully!")

            # Verify the migration
            print("Verifying migration...")
            result = await conn.execute(text("""
                SELECT
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns
                WHERE table_name = 'users'
                AND table_schema = 'public'
                AND column_name IN (
                    'first_name', 'last_name', 'subscription_tier', 'trial_end_date',
                    'is_co_creator', 'co_creator_joined_at', 'lifetime_access',
                    'co_creator_seat_number', 'co_creator_benefits',
                    'email_verification_token', 'email_verification_sent_at', 'email_verified_at',
                    'avatar_url', 'bio', 'website', 'api_key',
                    'monthly_request_limit', 'requests_this_month'
                )
                ORDER BY column_name;
            """))

            columns = result.fetchall()
            print(f"Verified columns: {len(columns)}")
            for col in columns:
                print(f"  ✓ {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")

        await engine.dispose()
        print("Database connection closed")

    except Exception as e:
        print(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    print("User Table Migration Tool")
    print("=" * 40)
    print("This script will add all missing columns to the users table")
    print()

    # Auto-confirm for production
    print("Starting migration automatically...")
    asyncio.run(run_user_table_migration())
    print("Migration completed! You can now restart your application.")