-- Check current users table schema
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'users'
AND table_schema = 'public'
ORDER BY ordinal_position;

-- Check for specific columns that should exist
SELECT
    'first_name' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'first_name'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'last_name' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'last_name'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'subscription_tier' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'subscription_tier'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'trial_end_date' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'trial_end_date'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'is_co_creator' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'is_co_creator'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'co_creator_joined_at' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'co_creator_joined_at'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'lifetime_access' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'lifetime_access'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'co_creator_seat_number' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'co_creator_seat_number'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'email_verification_token' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'email_verification_token'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'email_verification_sent_at' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'email_verification_sent_at'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'email_verified_at' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'email_verified_at'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'avatar_url' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'avatar_url'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'bio' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'bio'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'website' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'website'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'api_key' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'api_key'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'monthly_request_limit' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'monthly_request_limit'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'requests_this_month' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'requests_this_month'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'co_creator_benefits' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'co_creator_benefits'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT
    'last_login' as column_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'last_login'
    ) THEN 'EXISTS' ELSE 'MISSING' END as status;