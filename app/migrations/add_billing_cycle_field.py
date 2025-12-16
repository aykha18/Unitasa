"""
Migration to add billing_cycle column to users table
"""

from sqlalchemy import Column, String, MetaData, Table
from sqlalchemy.sql import text

# Migration metadata
revision = "add_billing_cycle_field"
down_revision = None  # This would be set if we had a previous migration

def upgrade():
    """Add billing_cycle column to users table"""

    # Add billing_cycle column
    add_billing_cycle_sql = """
    ALTER TABLE users ADD COLUMN IF NOT EXISTS billing_cycle VARCHAR(20) DEFAULT 'monthly';
    """

    return [text(add_billing_cycle_sql)]

def downgrade():
    """Remove billing_cycle column from users table"""

    # Remove the column (be careful with this in production!)
    drop_column_sql = """
    ALTER TABLE users DROP COLUMN IF EXISTS billing_cycle;
    """

    return [text(drop_column_sql)]

# For manual execution if needed
if __name__ == "__main__":
    print("Migration: Add billing_cycle column to users table")
    print("Run this migration on your production database:")
    print()
    print("SQL to execute:")
    print(upgrade()[0].text)