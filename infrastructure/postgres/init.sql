-- =============================================================================
-- SentinelEdge — PostgreSQL Initialization Script
-- Runs once when the postgres container is first created.
-- Installs required extensions into the sentineledge database.
-- =============================================================================

-- Vector similarity search (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

-- Trigram-based fuzzy text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- RFC 4122-compliant UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Case-insensitive text type
CREATE EXTENSION IF NOT EXISTS citext;

-- Cryptographic functions (used for token hashing, etc.)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ---------------------------------------------------------------------------
-- Verify extensions
-- ---------------------------------------------------------------------------
DO $$
BEGIN
  ASSERT (SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector')   = 1, 'pgvector not installed';
  ASSERT (SELECT COUNT(*) FROM pg_extension WHERE extname = 'pg_trgm')  = 1, 'pg_trgm not installed';
  ASSERT (SELECT COUNT(*) FROM pg_extension WHERE extname = 'uuid-ossp')= 1, 'uuid-ossp not installed';
  RAISE NOTICE 'SentinelEdge PostgreSQL extensions installed successfully.';
END;
$$;
