#!/usr/bin/env python3
"""
Simple database fix for nullability issues
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

async def fix_db():
    prod_url = "postgresql+asyncpg://postgres:eNUAZiYjbGNTiHfnNeFbUCPMdAugvujA@switchback.proxy.rlwy.net:24843/railway"

    print("Fixing database nullability issues...")

    try:
        engine = create_async_engine(prod_url, echo=True)

        async with engine.begin() as conn:
            print("Connected to database")

            # Check current constraints
            result = await conn.execute(text("""
                SELECT column_name, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'users' AND column_name IN ('is_co_creator', 'lifetime_access');
            """))

            print("Current state:")
            for row in result:
                print(f"  {row[0]}: nullable={row[1]}, default={row[2]}")

            # Fix is_co_creator
            print("Making is_co_creator nullable...")
            await conn.execute(text("ALTER TABLE users ALTER COLUMN is_co_creator DROP NOT NULL;"))

            # Fix lifetime_access
            print("Making lifetime_access nullable...")
            await conn.execute(text("ALTER TABLE users ALTER COLUMN lifetime_access DROP NOT NULL;"))

            # Set defaults for existing rows
            await conn.execute(text("UPDATE users SET is_co_creator = false WHERE is_co_creator IS NULL;"))
            await conn.execute(text("UPDATE users SET lifetime_access = false WHERE lifetime_access IS NULL;"))

            # Verify
            result = await conn.execute(text("""
                SELECT column_name, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'users' AND column_name IN ('is_co_creator', 'lifetime_access');
            """))

            print("After fix:")
            for row in result:
                print(f"  {row[0]}: nullable={row[1]}")

            print("Database fixes applied successfully!")

        await engine.dispose()

    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(fix_db())