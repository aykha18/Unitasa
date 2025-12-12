#!/usr/bin/env python3
"""
Database Schema Comparison Tool
Compares production database schema with expected User model schema
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from typing import Dict, List, Tuple

# Expected User model schema based on app/models/user.py
EXPECTED_SCHEMA = {
    'id': ('integer', False),
    'email': ('character varying(255)', False),
    'hashed_password': ('character varying(255)', False),
    'full_name': ('character varying(255)', True),
    'first_name': ('character varying(100)', True),
    'last_name': ('character varying(100)', True),
    'company': ('character varying(255)', True),
    'role': ('character varying(50)', True),
    'is_active': ('boolean', True),
    'is_verified': ('boolean', True),
    'api_key': ('character varying(255)', True),
    'avatar_url': ('text', True),
    'bio': ('text', True),
    'website': ('character varying(255)', True),
    'subscription_tier': ('character varying(50)', True),
    'monthly_request_limit': ('integer', True),
    'requests_this_month': ('integer', True),
    'trial_end_date': ('timestamp without time zone', True),
    'is_co_creator': ('boolean', True),
    'co_creator_joined_at': ('timestamp without time zone', True),
    'lifetime_access': ('boolean', True),
    'co_creator_seat_number': ('integer', True),
    'co_creator_benefits': ('text', True),
    'email_verification_token': ('character varying(255)', True),
    'email_verification_sent_at': ('timestamp without time zone', True),
    'email_verified_at': ('timestamp without time zone', True),
    'last_login': ('timestamp without time zone', True),
    'created_at': ('timestamp without time zone', True),
    'updated_at': ('timestamp without time zone', True)
}

async def compare_database_schema():
    """Compare production database schema with expected schema"""
    # Production database URL with asyncpg driver
    prod_url = "postgresql+asyncpg://postgres:eNUAZiYjbGNTiHfnNeFbUCPMdAugvujA@switchback.proxy.rlwy.net:24843/railway"

    print("Database Schema Comparison Tool")
    print("=" * 50)
    print(f"Database: {prod_url.split('@')[1] if '@' in prod_url else 'Connected'}")
    print()

    try:
        engine = create_async_engine(prod_url, echo=False)

        async with engine.begin() as conn:
            print("Connected to database successfully")
            print()

            # Get current schema
            result = await conn.execute(text("""
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_name = 'users'
                AND table_schema = 'public'
                ORDER BY ordinal_position;
            """))

            current_schema = {}
            rows = result.fetchall()

            print("Current Database Schema:")
            print("-" * 30)
            for row in rows:
                col_name, data_type, is_nullable, default = row
                current_schema[col_name] = (data_type, is_nullable == 'YES', default)
                nullable_str = "NULL" if is_nullable == 'YES' else "NOT NULL"
                default_str = f" DEFAULT {default}" if default else ""
                print(f"  {col_name}: {data_type} ({nullable_str}){default_str}")

            print()
            print("Comparison Results:")
            print("-" * 30)

            missing_columns = []
            type_mismatches = []
            nullable_mismatches = []

            # Check for missing columns
            for expected_col, (expected_type, expected_nullable) in EXPECTED_SCHEMA.items():
                if expected_col not in current_schema:
                    missing_columns.append((expected_col, expected_type, expected_nullable))
                else:
                    current_type, current_nullable, _ = current_schema[expected_col]

                    # Check type mismatch
                    if current_type != expected_type:
                        type_mismatches.append((expected_col, expected_type, current_type))

                    # Check nullable mismatch
                    if current_nullable != expected_nullable:
                        nullable_mismatches.append((expected_col, expected_nullable, current_nullable))

            # Report missing columns
            if missing_columns:
                print("MISSING COLUMNS:")
                for col, exp_type, exp_nullable in missing_columns:
                    nullable_str = "NULL" if exp_nullable else "NOT NULL"
                    print(f"  - {col}: {exp_type} ({nullable_str})")
                print()

                # Generate ADD COLUMN statements
                print("FIX COMMANDS:")
                for col, exp_type, exp_nullable in missing_columns:
                    nullable_clause = "" if exp_nullable else " NOT NULL"
                    default_clause = get_default_clause(col)
                    print(f"  ALTER TABLE users ADD COLUMN {col} {exp_type}{nullable_clause}{default_clause};")
                print()

            # Report type mismatches
            if type_mismatches:
                print("TYPE MISMATCHES:")
                for col, expected, current in type_mismatches:
                    print(f"  - {col}: Expected {expected}, Got {current}")
                print()

            # Report nullable mismatches
            if nullable_mismatches:
                print("NULLABILITY MISMATCHES:")
                for col, expected, current in nullable_mismatches:
                    exp_str = "NULL" if expected else "NOT NULL"
                    cur_str = "NULL" if current else "NOT NULL"
                    print(f"  - {col}: Expected {exp_str}, Got {cur_str}")
                print()

            # Check for extra columns
            extra_columns = []
            for current_col in current_schema:
                if current_col not in EXPECTED_SCHEMA:
                    extra_columns.append(current_col)

            if extra_columns:
                print("EXTRA COLUMNS (not in model):")
                for col in extra_columns:
                    col_type, nullable, _ = current_schema[col]
                    nullable_str = "NULL" if nullable else "NOT NULL"
                    print(f"  - {col}: {col_type} ({nullable_str})")
                print()

            # Summary
            print("SUMMARY:")
            print(f"  - Expected columns: {len(EXPECTED_SCHEMA)}")
            print(f"  - Current columns: {len(current_schema)}")
            print(f"  - Missing columns: {len(missing_columns)}")
            print(f"  - Type mismatches: {len(type_mismatches)}")
            print(f"  - Nullability mismatches: {len(nullable_mismatches)}")
            print(f"  - Extra columns: {len(extra_columns)}")

            if not missing_columns and not type_mismatches and not nullable_mismatches:
                print("\nSchema matches expected model!")
            else:
                print("\nSchema has issues that need to be fixed.")

        await engine.dispose()
        print("\nDatabase connection closed")

    except Exception as e:
        print(f"Error: {e}")
        raise

def get_default_clause(column_name: str) -> str:
    """Get appropriate default clause for a column"""
    defaults = {
        'role': " DEFAULT 'user'",
        'is_active': " DEFAULT true",
        'is_verified': " DEFAULT false",
        'subscription_tier': " DEFAULT 'free'",
        'monthly_request_limit': " DEFAULT 1000",
        'requests_this_month': " DEFAULT 0",
        'is_co_creator': " DEFAULT false",
        'lifetime_access': " DEFAULT false"
    }
    return defaults.get(column_name, "")

if __name__ == "__main__":
    asyncio.run(compare_database_schema())