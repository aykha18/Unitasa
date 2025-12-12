#!/usr/bin/env python3
"""
Comprehensive database schema comparison script
Checks all tables and identifies missing columns between local and production
"""

import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
import json

def get_production_db_url():
    """Get production database URL"""
    return "postgresql://postgres:eNUAZiYjbGNTiHfnNeFbUCPMdAugvujA@switchback.proxy.rlwy.net:24843/railway"

def get_local_db_url():
    """Get local database URL"""
    return os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Expected schema for each table
EXPECTED_SCHEMA = {
    "users": [
        'id', 'email', 'hashed_password', 'full_name', 'first_name', 'last_name',
        'company', 'role', 'is_active', 'is_verified', 'api_key', 'avatar_url',
        'bio', 'website', 'subscription_tier', 'monthly_request_limit',
        'requests_this_month', 'trial_end_date', 'is_co_creator',
        'co_creator_joined_at', 'lifetime_access', 'co_creator_seat_number',
        'co_creator_benefits', 'email_verification_token',
        'email_verification_sent_at', 'email_verified_at', 'last_login',
        'created_at', 'updated_at'
    ],
    "leads": [
        'id', 'email', 'first_name', 'last_name', 'company', 'phone',
        'crm_score', 'lead_source', 'lead_status', 'assessment_completed',
        'assessment_score', 'interested_in_co_creator', 'user_id',
        'created_at', 'updated_at'
    ],
    "co_creators": [
        'id', 'lead_id', 'user_id', 'seat_number', 'payment_intent_id',
        'activation_token', 'is_activated', 'activated_at', 'benefits',
        'created_at', 'updated_at'
    ],
    "campaigns": [
        'id', 'campaign_id', 'user_id', 'name', 'description', 'status',
        'campaign_type', 'target_audience', 'platforms', 'total_posts',
        'total_engagements', 'total_impressions', 'total_clicks',
        'budget_allocated', 'budget_spent', 'start_date', 'end_date',
        'created_at', 'updated_at'
    ],
    "events": [
        'id', 'user_id', 'event_type', 'event_data', 'ip_address',
        'user_agent', 'session_id', 'created_at'
    ],
    "social_accounts": [
        'id', 'user_id', 'platform', 'account_id', 'username', 'name',
        'profile_url', 'avatar_url', 'access_token', 'refresh_token',
        'token_expires_at', 'follower_count', 'following_count',
        'is_active', 'last_synced_at', 'created_at', 'updated_at'
    ],
    "social_posts": [
        'id', 'user_id', 'social_account_id', 'platform', 'post_id',
        'content', 'media_urls', 'post_url', 'posted_at', 'engagement_count',
        'like_count', 'comment_count', 'share_count', 'click_count',
        'status', 'scheduled_for', 'created_at', 'updated_at'
    ],
    "engagements": [
        'id', 'user_id', 'social_account_id', 'platform', 'engagement_type',
        'target_post_id', 'target_user_id', 'content', 'status',
        'scheduled_for', 'executed_at', 'created_at', 'updated_at'
    ],
    "content_templates": [
        'id', 'user_id', 'name', 'description', 'platform', 'content_type',
        'template_content', 'variables', 'is_active', 'usage_count',
        'created_at', 'updated_at'
    ],
    "analytics_snapshots": [
        'id', 'user_id', 'snapshot_date', 'platform', 'metric_type',
        'metric_value', 'comparison_period', 'change_percentage',
        'created_at'
    ]
}

async def inspect_table_schema(engine, table_name):
    """Inspect table schema and return column information"""
    try:
        async with engine.begin() as conn:
            # Check if table exists
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = :table_name
                );
            """), {"table_name": table_name})

            table_exists = result.scalar()
            if not table_exists:
                return {"table_exists": False}

            # Get column information
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = :table_name
                AND table_schema = 'public'
                ORDER BY ordinal_position;
            """), {"table_name": table_name})

            columns = result.fetchall()

            return {
                "table_exists": True,
                "columns": [
                    {
                        "name": col[0],
                        "type": col[1],
                        "nullable": col[2] == 'YES',
                        "default": col[3]
                    } for col in columns
                ]
            }
    except Exception as e:
        return {"error": str(e)}

async def compare_databases():
    """Compare local and production database schemas"""
    print("Comprehensive Database Schema Comparison")
    print("=" * 60)

    # Get database URLs
    prod_url = get_production_db_url()
    local_url = get_local_db_url()

    print(f"Production DB: {prod_url.split('@')[1] if '@' in prod_url else 'Connected'}")
    print(f"Local DB: {local_url}")
    print()

    results = {}

    # Check production database
    print("[TEST] Inspecting PRODUCTION database...")
    try:
        prod_engine = create_async_engine(prod_url, echo=False)
        prod_schemas = {}

        for table_name in EXPECTED_SCHEMA.keys():
            print(f"  Checking table: {table_name}")
            schema = await inspect_table_schema(prod_engine, table_name)
            prod_schemas[table_name] = schema

        await prod_engine.dispose()
        print("[PASS] Production inspection complete")
    except Exception as e:
        print(f"[ERROR] Production database connection failed: {e}")
        prod_schemas = {"connection_error": str(e)}

    # Check local database
    print("\n[TEST] Inspecting LOCAL database...")
    try:
        local_engine = create_async_engine(local_url, echo=False)
        local_schemas = {}

        for table_name in EXPECTED_SCHEMA.keys():
            print(f"  Checking table: {table_name}")
            schema = await inspect_table_schema(local_engine, table_name)
            local_schemas[table_name] = schema

        await local_engine.dispose()
        print("[PASS] Local inspection complete")
    except Exception as e:
        print(f"[ERROR] Local database connection failed: {e}")
        local_schemas = {"connection_error": str(e)}

    # Analyze results
    print("\n" + "=" * 60)
    print("SCHEMA ANALYSIS RESULTS")
    print("=" * 60)

    all_issues = []

    for table_name, expected_columns in EXPECTED_SCHEMA.items():
        print(f"\n[TABLE] {table_name}")
        print("-" * 40)

        prod_schema = prod_schemas.get(table_name, {})
        local_schema = local_schemas.get(table_name, {})

        # Check if table exists
        if "connection_error" in prod_schemas:
            print("[ERROR] Production database connection failed")
            continue

        if "error" in prod_schema:
            print(f"[ERROR] Production table check failed: {prod_schema['error']}")
            all_issues.append(f"Production {table_name}: {prod_schema['error']}")
            continue

        if not prod_schema.get("table_exists", False):
            print(f"[MISSING] Table does not exist in production")
            all_issues.append(f"Table {table_name} missing in production")
            continue

        # Get actual columns
        prod_columns = [col['name'] for col in prod_schema.get('columns', [])]

        # Find missing columns
        missing_columns = [col for col in expected_columns if col not in prod_columns]

        if missing_columns:
            print(f"[MISSING COLUMNS] {len(missing_columns)} columns missing:")
            for col in missing_columns:
                print(f"  - {col}")
            all_issues.extend([f"{table_name}.{col}" for col in missing_columns])
        else:
            prod_col_count = len(prod_columns)
            expected_count = len(expected_columns)
            print(f"[OK] All {prod_col_count} expected columns present")

            if prod_col_count != expected_count:
                print(f"[WARNING] Column count mismatch: expected {expected_count}, found {prod_col_count}")

    # Generate migration SQL
    print("\n" + "=" * 60)
    print("GENERATED MIGRATION SQL")
    print("=" * 60)

    migration_sql = []

    for table_name, expected_columns in EXPECTED_SCHEMA.items():
        prod_schema = prod_schemas.get(table_name, {})

        if not prod_schema.get("table_exists", False):
            print(f"\n-- Create table {table_name} (not implemented)")
            continue

        prod_columns = [col['name'] for col in prod_schema.get('columns', [])]
        missing_columns = [col for col in expected_columns if col not in prod_columns]

        if missing_columns:
            print(f"\n-- Add missing columns to {table_name}")
            for col in missing_columns:
                # Determine column type based on common patterns
                if 'date' in col.lower() or 'at' in col.lower():
                    col_type = 'TIMESTAMP'
                elif 'count' in col.lower() or 'number' in col.lower() or 'id' in col:
                    col_type = 'INTEGER'
                elif 'is_' in col.lower() or col.startswith('has_'):
                    col_type = 'BOOLEAN DEFAULT FALSE'
                elif 'url' in col.lower() or 'token' in col.lower():
                    col_type = 'TEXT'
                else:
                    col_type = 'VARCHAR(255)'

                sql = f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {col} {col_type};"
                print(sql)
                migration_sql.append(sql)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if all_issues:
        print(f"[ISSUES FOUND] {len(all_issues)} schema mismatches:")
        for issue in all_issues:
            print(f"  - {issue}")

        print(f"\n[RECOMMENDATION] Run the generated SQL above in your production database")
        print("Then restart your application")
    else:
        print("[SUCCESS] All schemas match between production and local!")

    return migration_sql

if __name__ == "__main__":
    asyncio.run(compare_databases())