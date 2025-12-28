-- PostgreSQL initialization script
-- Runs automatically when database first starts
-- Creates schema, indexes, and initial settings

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search optimization

-- Create references table with proper constraints
CREATE TABLE IF NOT EXISTS references_tbl (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    authors TEXT,
    year TEXT,
    doi TEXT UNIQUE,
    bibtex TEXT,
    user_id INTEGER,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create notes table
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    user_id INTEGER,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_references_user_id ON references_tbl(user_id);
CREATE INDEX IF NOT EXISTS idx_references_doi ON references_tbl(doi);
CREATE INDEX IF NOT EXISTS idx_references_created_at ON references_tbl(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);
CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at DESC);

-- Create full-text search index for title and authors
CREATE INDEX IF NOT EXISTS idx_references_fulltext ON references_tbl 
    USING gin(to_tsvector('english', title || ' ' || COALESCE(authors, '')));

-- Set up automatic update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_references_updated_at ON references_tbl;
CREATE TRIGGER update_references_updated_at
    BEFORE UPDATE ON references_tbl
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_notes_updated_at ON notes;
CREATE TRIGGER update_notes_updated_at
    BEFORE UPDATE ON notes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Set database parameters for optimal performance
ALTER DATABASE capstone_db SET shared_preload_libraries = 'pg_stat_statements';
ALTER DATABASE capstone_db SET log_connections = on;
ALTER DATABASE capstone_db SET log_disconnections = on;
ALTER DATABASE capstone_db SET log_duration = off;
ALTER DATABASE capstone_db SET log_lock_waits = on;

GRANT CONNECT ON DATABASE capstone_db TO capstone;
GRANT USAGE ON SCHEMA public TO capstone;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO capstone;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO capstone;

-- Log initialization completion
SELECT 'PostgreSQL database initialized successfully' as status;
