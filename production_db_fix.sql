-- Production Database Fix for User Registration
-- Run these commands in your Railway PostgreSQL database

-- Add name columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);

-- Add subscription and trial columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(50) DEFAULT 'free_trial';
ALTER TABLE users ADD COLUMN IF NOT EXISTS monthly_request_limit INTEGER DEFAULT 1000;
ALTER TABLE users ADD COLUMN IF NOT EXISTS requests_this_month INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS trial_end_date TIMESTAMP;

-- Add co-creator columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_co_creator BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS co_creator_joined_at TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS lifetime_access BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS co_creator_seat_number INTEGER;
ALTER TABLE users ADD COLUMN IF NOT EXISTS co_creator_benefits TEXT;

-- Add email verification columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_sent_at TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP;

-- Add profile columns
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS website VARCHAR(255);

-- Add API key column
ALTER TABLE users ADD COLUMN IF NOT EXISTS api_key VARCHAR(255);

-- Populate first_name and last_name from existing full_name data
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

-- Set default trial_end_date for existing users (15 days from now)
UPDATE users
SET trial_end_date = CURRENT_TIMESTAMP + INTERVAL '15 days'
WHERE trial_end_date IS NULL AND subscription_tier = 'free_trial';

-- Verify the columns were added
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