import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def fix_schema():
    # Connect to database using environment variables
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:aykha123@localhost:5432/unitas")

    # Parse database URL for asyncpg connection
    if database_url.startswith("postgresql+asyncpg://"):
        # Extract connection details from URL
        url_parts = database_url.replace("postgresql+asyncpg://", "").split("@")
        user_pass = url_parts[0].split(":")
        host_db = url_parts[1].split("/")

        user = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else ""
        host_port = host_db[0].split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 5432
        database = host_db[1]

        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
    else:
        # Fallback to direct connection (for backward compatibility)
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='aykha123',
            database='unitas'
        )
    
    try:
        # Add missing columns
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_requested BOOLEAN DEFAULT FALSE;
        ''')
        print("✓ Added consultation_requested")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_booked BOOLEAN DEFAULT FALSE;
        ''')
        print("✓ Added consultation_booked")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_completed BOOLEAN DEFAULT FALSE;
        ''')
        print("✓ Added consultation_completed")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_type VARCHAR(100);
        ''')
        print("✓ Added consultation_type")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_challenges TEXT;
        ''')
        print("✓ Added consultation_challenges")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_scheduled_at TIMESTAMP;
        ''')
        print("✓ Added consultation_scheduled_at")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS consultation_completed_at TIMESTAMP;
        ''')
        print("✓ Added consultation_completed_at")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS ai_report_requested BOOLEAN DEFAULT FALSE;
        ''')
        print("✓ Added ai_report_requested")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS ai_report_generated BOOLEAN DEFAULT FALSE;
        ''')
        print("✓ Added ai_report_generated")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS ai_report_sent BOOLEAN DEFAULT FALSE;
        ''')
        print("✓ Added ai_report_sent")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS ai_report_id VARCHAR(100);
        ''')
        print("✓ Added ai_report_id")
        
        await conn.execute('''
            ALTER TABLE leads ADD COLUMN IF NOT EXISTS ai_report_generated_at TIMESTAMP;
        ''')
        print("✓ Added ai_report_generated_at")
        
        # Check if lead_id column exists and remove it (it's not in the model)
        result = await conn.fetchval('''
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'leads' AND column_name = 'lead_id'
        ''')
        
        if result > 0:
            await conn.execute('ALTER TABLE leads DROP COLUMN lead_id;')
            print("✓ Removed lead_id column")
        
        print("\n✅ Database schema updated successfully!")
        
        # Show current columns
        columns = await conn.fetch('''
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'leads' 
            ORDER BY ordinal_position
        ''')
        
        print("\nCurrent leads table columns:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']}")
            
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(fix_schema())
