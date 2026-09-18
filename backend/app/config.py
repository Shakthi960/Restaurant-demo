"""Application configuration loaded from backend/.env"""

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent

load_dotenv(BACKEND_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
# New-style API keys. Service/secret key bypasses RLS; falls back to the
# publishable/anon key when the secret is not set.
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY", "").strip() or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY", "").strip() or os.getenv("SUPABASE_ANON_KEY", "").strip()
SUPABASE_KEY = SUPABASE_SECRET_KEY or SUPABASE_PUBLISHABLE_KEY

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Comma-separated list of origins allowed to call the API (CORS).
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()] or [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# Directory that holds the existing design sources (css, js, assets).
FRONTEND_DIR = PROJECT_ROOT / "frontend"
TEMPLATES_DIR = BACKEND_DIR / "templates"