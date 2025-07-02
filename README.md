# chennaihomenavigator-17395-25d07905

## Supabase/Postgres Backend Integration

### 1. Environment Variables

To connect your FastAPI backend to Supabase Postgres, set the following environment variables (use your `.env` file, or an environment manager):

```
SUPABASE_URL=https://dligiseioqdinsgpasqz.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRsaWdpc2Vpb3FkaW5zZ3Bhc3F6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE0MzAyNjEsImV4cCI6MjA2NzAwNjI2MX0.8c5FVa5yQeAucH5wJQbe7TbCbs54HOB_FoLmDsrd6bM
SUPABASE_DB_URL=postgresql://postgres:SupabaseUnknown100@db.dligiseioqdinsgpasqz.supabase.co:5432/postgres
```

### 2. FastAPI Backend Setup for Supabase

- The backend (`src/api/main.py`) now detects `SUPABASE_DB_URL` and uses it for SQLAlchemy if set; otherwise it falls back to SQLite. No code changes needed for switching environments!
- For local development with SQLite, keep `SUPABASE_DB_URL` unset.
- To deploy with Supabase, set the environment variables above.

### 3. Dependencies

**If using Postgres (Supabase), ensure you have:**
- Install the async/pg driver:

```bash
pip install psycopg2-binary
```

Add `psycopg2-binary` to your `requirements.txt`:

```
psycopg2-binary
```

### 4. Database Migrations

- Table/model auto-creation still works via SQLAlchemy, but for production you may wish to use Alembic or equivalent for migrations.
