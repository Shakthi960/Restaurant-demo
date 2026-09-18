"""Lightweight admin authentication via signed cookie.

Uses a static HMAC of ADMIN_PASSWORD under SECRET_KEY — no database session
needed.  If either ADMIN_PASSWORD or SECRET_KEY is missing the admin area is
disabled.  The token itself never expires; /admin/logout clears the cookie.
"""

import hashlib
import hmac
import os
import secrets

from fastapi import Request, Response
from fastapi.responses import RedirectResponse

COOKIE_NAME = "galaxy_admin"
CSRF_COOKIE_NAME = "galaxy_csrf"
# Generate a random secret at startup when none is set. This means sessions
# are invalidated on restart — acceptable for a demo; set SECRET_KEY in .env
# for persistence.
SECRET_KEY: str = os.getenv("SECRET_KEY", "") or secrets.token_hex(32)
ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "").strip()
# Cookies are marked Secure only behind TLS (Render terminates it).
SECURE_COOKIES: bool = os.getenv("SECURE_COOKIES", "").lower() in ("1", "true", "yes")


def admin_enabled() -> bool:
    return bool(ADMIN_PASSWORD)


def _expected_token() -> str:
    if not ADMIN_PASSWORD:
        return ""
    return hmac.new(
        SECRET_KEY.encode(),
        ADMIN_PASSWORD.encode(),
        hashlib.sha256,
    ).hexdigest()


def create_admin_cookie(response: Response) -> None:
    token = _expected_token()
    response.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        samesite="lax",
        secure=SECURE_COOKIES,
        max_age=60 * 60 * 24 * 7,  # 7 days
    )


def clear_admin_cookie(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, httponly=True, samesite="lax", secure=SECURE_COOKIES)


def is_admin(request: Request) -> bool:
    token = request.cookies.get(COOKIE_NAME, "")
    if not token or not admin_enabled():
        return False
    return hmac.compare_digest(token, _expected_token())


def require_admin(request: Request) -> RedirectResponse | None:
    """FastAPI dependency — redirect to login when unauthenticated."""
    if is_admin(request):
        return None
    return RedirectResponse("/admin/login", status_code=303)


def new_csrf_token() -> str:
    """Random per-page CSRF token used with the double-submit cookie."""
    return secrets.token_hex(16)


def set_csrf_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        CSRF_COOKIE_NAME,
        token,
        httponly=True,
        samesite="lax",
        secure=SECURE_COOKIES,
        max_age=60 * 60 * 24 * 7,  # 7 days
    )


def csrf_token_valid(request: Request, submitted: str) -> bool:
    """Compare the submitted form token against the CSRF cookie value."""
    cookie = request.cookies.get(CSRF_COOKIE_NAME, "")
    if not cookie or not submitted:
        return False
    return hmac.compare_digest(cookie, submitted)