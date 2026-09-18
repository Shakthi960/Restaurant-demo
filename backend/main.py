"""Galaxy Restaurants — FastAPI application.

Run:  uvicorn main:app --reload
"""

import logging

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app import config, db
from app.limiter import limiter
from app.routes import api, pages, admin


def _setup_logging() -> None:
    """Console (stdout) logging for the ``app.*`` loggers, captured by the host."""
    logger = logging.getLogger("app")
    if logger.handlers:
        return
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    logger.addHandler(handler)


_setup_logging()

app = FastAPI(
    title="Galaxy Restaurants",
    description="Taste Tradition Together — website pages and public API.",
    version="0.2.0",
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def _rate_limit_exceeded(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again in a moment."},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the existing design sources (css, js, assets) from frontend/ at /static.
app.mount("/static", StaticFiles(directory=str(config.FRONTEND_DIR)), name="static")

app.include_router(pages.router)
app.include_router(api.router)
app.include_router(admin.router)


@app.get("/healthz")
def healthz():
    db_ok = db.ping()
    return {
        "status": "ok" if db_ok else "degraded",
        "db_configured": bool(config.SUPABASE_KEY),
        "db_reachable": db_ok,
    }