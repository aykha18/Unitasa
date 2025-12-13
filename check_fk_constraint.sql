-- Check the actual foreign key constraint for co_creators.lead_id
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    ccu.ordinal_position AS foreign_ordinal
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
    AND tc.table_schema = 'public'
    AND kcu.column_name = 'lead_id';

-- Check what columns exist in leads table
SELECT column_name, data_type, ordinal_position
FROM information_schema.columns
WHERE table_name = 'leads' AND table_schema = 'public'
ORDER BY ordinal_position;