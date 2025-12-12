#!/usr/bin/env python3
"""
Check foreign key constraints in production database
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

async def check_foreign_keys():
    prod_url = "postgresql+asyncpg://postgres:eNUAZiYjbGNTiHfnNeFbUCPMdAugvujA@switchback.proxy.rlwy.net:24843/railway"

    print("Checking foreign key constraints...")

    try:
        engine = create_async_engine(prod_url, echo=False)

        async with engine.begin() as conn:
            print("Connected to database")

            # Check foreign key constraints for co_creators table
            result = await conn.execute(text("""
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM
                    information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE
                    tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = 'co_creators'
                    AND tc.table_schema = 'public';
            """))

            print("Foreign key constraints for co_creators table:")
            rows = result.fetchall()
            if rows:
                for row in rows:
                    print(f"  {row[0]}.{row[1]} -> {row[2]}.{row[3]}")
            else:
                print("  No foreign key constraints found")

            # Check if co_creators table exists and its structure
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'co_creators' AND table_schema = 'public'
                ORDER BY ordinal_position;
            """))

            print("\nco_creators table structure:")
            rows = result.fetchall()
            if rows:
                for row in rows:
                    nullable = "NULL" if row[2] == 'YES' else "NOT NULL"
                    print(f"  {row[0]}: {row[1]} ({nullable})")
            else:
                print("  co_creators table does not exist")

            # Check if leads table has lead_id column
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'leads' AND table_schema = 'public'
                AND column_name IN ('id', 'lead_id')
                ORDER BY column_name;
            """))

            print("\nleads table id/lead_id columns:")
            rows = result.fetchall()
            for row in rows:
                nullable = "NULL" if row[2] == 'YES' else "NOT NULL"
                print(f"  {row[0]}: {row[1]} ({nullable})")

        await engine.dispose()

    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(check_foreign_keys())