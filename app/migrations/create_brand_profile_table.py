"""
Migration to create brand_profiles table
"""

from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.sql import text

# Migration metadata
revision = "create_brand_profile_table"
down_revision = "add_user_name_fields"

def upgrade():
    """Create brand_profiles table"""

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS brand_profiles (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL UNIQUE,
        client_id VARCHAR(255) NOT NULL UNIQUE,
        profile_data JSON NOT NULL DEFAULT '{}',
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc') NOT NULL,
        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc') NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    
    CREATE INDEX IF NOT EXISTS ix_brand_profiles_user_id ON brand_profiles (user_id);
    CREATE INDEX IF NOT EXISTS ix_brand_profiles_client_id ON brand_profiles (client_id);
    """

    return [text(create_table_sql)]

def downgrade():
    """Drop brand_profiles table"""

    drop_table_sql = """
    DROP TABLE IF EXISTS brand_profiles;
    """

    return [text(drop_table_sql)]

if __name__ == "__main__":
    print("Migration: Create brand_profiles table")
    print("SQL to execute:")
    print(upgrade()[0].text)
