# Supabase/Postgres Integration Guide for FastAPI Backend

## Overview

This document details how Supabase Postgres is integrated with the FastAPI backend for HomeQuestAI.

## Connection

- The backend uses SQLAlchemy for ORM/database access.
- By default, backend will read the environment variable `SUPABASE_DB_URL` to connect to the Supabase-managed Postgres instance.
- If `SUPABASE_DB_URL` is not set, it falls back to SQLite for local development.

### Required Environment Variables

Add these to your `.env`, deployment environment, or launch command:

```
SUPABASE_URL=https://dligiseioqdinsgpasqz.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRsaWdpc2Vpb3FkaW5zZ3Bhc3F6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0MzAyNjEsImV4cCI6MjA2NzAwNjI2MX0.8c5FVa5yQeAucH5wJQbe7TbCbs54HOB_FoLmDsrd6bM
SUPABASE_DB_URL=postgresql://postgres:SupabaseUnknown100@db.dligiseioqdinsgpasqz.supabase.co:5432/postgres
```

## How Integration Works

- In `src/api/main.py`, database URL is determined as follows:
    - If `SUPABASE_DB_URL` is present, it is used.
    - If not, defaults to SQLite (`./homequestai.db`)
- SQLite uses a special SQLAlchemy option (`check_same_thread`), but Postgres doesn't need it.

## Requirements

Be sure to install the PostgreSQL driver for Python (SQLAlchemy):

```bash
pip install psycopg2-binary
```
And verify this in `requirements.txt`.

## Migrations

- SQLAlchemy's `Base.metadata.create_all()` will create tables on the fly.
- For migration and versioning in production, use Alembic (not required for initial prototype).

## Auth & Row-Level Security

- **Authentication** (Firebase, JWT, etc.) should be added for production.
- **Supabase row-level security** can be configured from your Supabase dashboard (https://supabase.io), but is not enabled by code changes in this backend.

## Example: Setting up locally with Supabase

1. Create `.env` file at the project root with the environment variables above.
2. Install dependencies.
3. Run FastAPI as usual.

## Audit Trail

- This document is updated upon each integration/configuration with Supabase.

## Additional resources

- [Supabase Documentation](https://supabase.io/docs)
- [SQLAlchemy Postgres Connection Guide](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)

