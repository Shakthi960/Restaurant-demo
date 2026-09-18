"""Apply database/supabase/schema.sql + seed.sql to the Supabase Postgres.

Connection chain (first success wins):
  1. DATABASE_URL from backend/.env (direct :5432)
  2. Transaction pooler fallback on :6543 (same host region)
  3. Session poolers across common regions on :5432

Usage:  python scripts/init_db.py
"""

import os
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import psycopg2
from dotenv import load_dotenv

BACKEND = Path(__file__).resolve().parents[1]
SQL_DIR = BACKEND.parent / "database" / "supabase"
load_dotenv(BACKEND / ".env")

DB_URL = os.getenv("DATABASE_URL", "").strip()

POOLER_REGIONS = [
    "ap-northeast-2", "ap-south-1", "ap-south-2", "ap-southeast-1",
    "ap-southeast-2", "us-east-1", "us-east-2", "us-west-1", "us-west-2",
    "eu-west-1", "eu-west-2", "eu-central-1",
]


def _dsn_variants(dsn: str):
    """Yield candidate DSNs: original, transaction pooler, then session poolers."""
    parts = urlsplit(dsn)
    if not parts.hostname:
        return
    passwd = parts.password

    # Project ref: host "db.<ref>.supabase.co" -> "<ref>"
    ref = parts.hostname.split(".")[1] if "db." in parts.hostname else parts.hostname.split(".")[0]

    yield dsn

    # Session poolers across regions: aws-0-<region>.pooler.supabase.com:5432
    for region in POOLER_REGIONS:
        netloc = f"postgres.{ref}:{passwd}@aws-0-{region}.pooler.supabase.com:5432"
        query = f"sslmode=require&options=project%3D{ref}"
        yield urlunsplit(parts._replace(netloc=netloc, path="/postgres", query=query))


def main():
    if not DB_URL:
        sys.exit("Error: DATABASE_URL is not set in backend/.env")

    conn = None
    for dsn in _dsn_variants(DB_URL):
        try:
            conn = psycopg2.connect(dsn, connect_timeout=10)
            break
        except Exception:
            continue

    if conn is None:
        sys.exit("Error: could not connect to the database with any candidate DSN.")

    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            for name in ("schema.sql", "seed.sql"):
                sql_path = SQL_DIR / name
                if not sql_path.exists():
                    sys.exit(f"Error: {sql_path} not found")
                print(f"Executing {name} ...")
                cur.execute(sql_path.read_text(encoding="utf-8"))
                print(f"  done ({sql_path.stat().st_size} bytes)")
        print("\nDatabase ready: schema + seed applied.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()