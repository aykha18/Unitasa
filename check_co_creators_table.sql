-- Check if co_creators table exists and its foreign key constraints
SELECT
    schemaname,
    tablename
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename = 'co_creators';

-- Check foreign key constraints for co_creators table
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

-- Check co_creators table structure
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'co_creators'
    AND table_schema = 'public'
ORDER BY ordinal_position;