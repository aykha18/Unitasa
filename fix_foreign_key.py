#!/usr/bin/env python3
"""
Fix foreign key constraint for co_creators.lead_id
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

async def fix_foreign_key():
    prod_url = "postgresql+asyncpg://postgres:eNUAZiYjbGNTiHfnNeFbUCPMdAugvujA@switchback.proxy.rlwy.net:24843/railway"

    print("Fixing foreign key constraint for co_creators.lead_id...")

    try:
        engine = create_async_engine(prod_url, echo=True)

        async with engine.begin() as conn:
            print("Connected to database")

            # First, check current foreign key constraints
            result = await conn.execute(text("""
                SELECT conname, conrelid::regclass, confrelid::regclass, conkey, confkey
                FROM pg_constraint
                WHERE conrelid = 'co_creators'::regclass
                AND contype = 'f';
            """))

            print("Current foreign key constraints on co_creators:")
            constraints = result.fetchall()
            for constraint in constraints:
                print(f"  {constraint[0]}: {constraint[1]}.{constraint[3]} -> {constraint[2]}.{constraint[4]}")

            # Drop the existing foreign key constraint if it exists
            await conn.execute(text("""
                ALTER TABLE co_creators DROP CONSTRAINT IF EXISTS co_creators_lead_id_fkey;
            """))
            print("Dropped existing lead_id foreign key constraint")

            # Add the correct foreign key constraint
            await conn.execute(text("""
                ALTER TABLE co_creators ADD CONSTRAINT co_creators_lead_id_fkey
                FOREIGN KEY (lead_id) REFERENCES leads(id);
            """))
            print("Added correct foreign key constraint: co_creators.lead_id -> leads.id")

            # Verify the constraint was added
            result = await conn.execute(text("""
                SELECT conname, conrelid::regclass, confrelid::regclass, conkey, confkey
                FROM pg_constraint
                WHERE conrelid = 'co_creators'::regclass
                AND contype = 'f'
                AND conname = 'co_creators_lead_id_fkey';
            """))

            constraint = result.fetchone()
            if constraint:
                print(f"✓ Verified constraint: {constraint[0]}")
            else:
                print("✗ Constraint not found after creation")

        await engine.dispose()
        print("Foreign key fix completed!")

    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(fix_foreign_key())