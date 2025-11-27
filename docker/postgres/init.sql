-- =============================================================================
-- PostgreSQL Initialization Script
-- =============================================================================
-- This script is executed only on first container startup
-- Alembic migrations will handle the actual schema creation

-- Ensure database encoding is UTF-8
SELECT 'Database initialized. Alembic will manage schema.' AS status;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'PostgreSQL initialized for Transactional Agent';
    RAISE NOTICE 'Schema will be created by Alembic migrations';
END $$;
