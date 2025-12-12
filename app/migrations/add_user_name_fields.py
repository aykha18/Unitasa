"""
Migration to add first_name and last_name columns to users table
"""

from sqlalchemy import Column, String, MetaData, Table
from sqlalchemy.sql import text

# Migration metadata
revision = "add_user_name_fields"
down_revision = None  # This would be set if we had a previous migration

def upgrade():
    """Add first_name and last_name columns to users table"""

    # Using raw SQL for the migration since we're dealing with production database
    # This approach works with any SQLAlchemy-supported database

    # Add first_name column
    add_first_name_sql = """
    ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);
    """

    # Add last_name column
    add_last_name_sql = """
    ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);
    """

    # Update existing records to populate first_name and last_name from full_name
    # This assumes full_name format is "First Last"
    populate_names_sql = """
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

    return [
        text(add_first_name_sql),
        text(add_last_name_sql),
        text(populate_names_sql)
    ]

def downgrade():
    """Remove first_name and last_name columns from users table"""

    # Remove the columns (be careful with this in production!)
    drop_columns_sql = """
    ALTER TABLE users DROP COLUMN IF EXISTS first_name;
    ALTER TABLE users DROP COLUMN IF EXISTS last_name;
    """

    return [text(drop_columns_sql)]

# For manual execution if needed
if __name__ == "__main__":
    print("Migration: Add first_name and last_name columns to users table")
    print("Run this migration on your production database:")
    print()
    print("SQL to execute:")
    print(upgrade()[0].text)
    print(upgrade()[1].text)
    print(upgrade()[2].text)