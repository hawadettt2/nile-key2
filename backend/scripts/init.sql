-- PostgreSQL initialization script.
-- Runs automatically on first container start via /docker-entrypoint-initdb.d/.
-- Uses POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB from the container environment.
-- No secrets are hardcoded here.

-- Set timezone to UTC for consistent timestamp handling.
SET timezone = 'UTC';

-- Optional: create a dedicated schema for the application.
-- Uncomment if you want schema isolation instead of using public.
-- CREATE SCHEMA IF NOT EXISTS nilekey AUTHORIZATION CURRENT_USER;
-- SET search_path TO nilekey, public;

-- Optional: useful extensions (uncomment if needed by future migrations).
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- CREATE EXTENSION IF NOT EXISTS "pgcrypto";
