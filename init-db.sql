-- Initialize astrology database
-- This script runs automatically when the PostgreSQL container starts

-- The database is already created via POSTGRES_DB env var
-- This script can be used for additional initialization if needed

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Astrology database initialized successfully';
END $$;