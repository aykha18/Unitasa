-- Add missing lead_id column to leads table
ALTER TABLE leads ADD COLUMN IF NOT EXISTS lead_id VARCHAR(255);

-- Make it unique and add index
ALTER TABLE leads ADD CONSTRAINT leads_lead_id_key UNIQUE (lead_id);
CREATE INDEX IF NOT EXISTS ix_leads_lead_id ON leads (lead_id);

-- Generate lead_id values for existing records
UPDATE leads SET lead_id = 'lead_' || id::text WHERE lead_id IS NULL;