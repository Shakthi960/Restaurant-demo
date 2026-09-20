"""Thin Supabase client wrapper.

The client is created lazily on the first data access. If credentials are not
configured (no .env), every accessor returns [] / None so the site still boots
and renders templates gracefully during development.
"""

import functools
import json
import logging
import threading
import time
from typing import Optional

from app import config

logger = logging.getLogger(__name__)

# Seconds to cache catalogue reads served to visitors (menu, locations, ...).
CACHE_TTL = 300

_client = None

# Last write error as a string ("" when none). Lets routes show the real
# reason behind an otherwise generic 500, which helps debug on a demo.
last_error: str = ""


def _ttl_cache(ttl: float = CACHE_TTL):
    """Memoize a zero-arg-or-keyword-callable for `ttl` seconds, thread-safe."""

    def decorator(func):
        cache: dict = {}
        lock = threading.Lock()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, json.dumps(kwargs, sort_keys=True))
            now = time.monotonic()
            with lock:
                hit = cache.get(key)
                if hit and now - hit[0] < ttl:
                    return hit[1]
            value = func(*args, **kwargs)
            with lock:
                cache[key] = (now, value)
            return value

        return wrapper

    return decorator


def get_client():
    """Return the shared Supabase client or None when unconfigured."""
    global _client
    if _client is not None:
        return _client
    if not (config.SUPABASE_URL and config.SUPABASE_KEY):
        return None
    try:
        from supabase import create_client

        _client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Supabase client init failed: %s", exc)
        return None
    return _client


def _table(name: str):
    client = get_client()
    if client is None:
        return None
    return client.table(name)


# ---------------------------------------------------------------------------
# Accessors (each returns [] on any failure)
# ---------------------------------------------------------------------------

def fetch_all(table: str, order: str = "sort_order") -> list:
    try:
        result = _table(table).select("*").order(order).execute()
        return result.data or []
    except Exception as exc:
        logger.warning("fetch_all(%s) failed: %s", table, exc)
        return []


@_ttl_cache()
def get_dishes(category: Optional[str] = None, signature_only: bool = False) -> list:
    query = _table("dishes")
    if query is None:
        return []
    try:
        builder = query.select("*")
        if signature_only:
            builder = builder.eq("is_signature", True)
        if category:
            builder = builder.eq("category", category)
        length = 100
        return (builder.order("sort_order").limit(length).execute()).data or []
    except Exception as exc:
        logger.warning("get_dishes failed: %s", exc)
        return []


@_ttl_cache()
def get_locations() -> list:
    return fetch_all("locations")


@_ttl_cache()
def get_gallery_images() -> list:
    return fetch_all("gallery_images")


@_ttl_cache()
def get_reviews() -> list:
    try:
        result = _table("reviews").select("*").eq("is_approved", True).order("created_at").limit(6).execute()
        return result.data or []
    except Exception as exc:
        logger.warning("get_reviews failed: %s", exc)
        return []


def get_location_id(slug: str) -> Optional[str]:
    try:
        result = _table("locations").select("id").eq("slug", slug).limit(1).execute()
        rows = result.data or []
        return rows[0]["id"] if rows else None
    except Exception as exc:
        logger.warning("get_location_id(%s) failed: %s", slug, exc)
        return None


# ---------------------------------------------------------------------------
# Writers (each returns the created row or None on failure)
# ---------------------------------------------------------------------------

def create_reservation(row: dict) -> Optional[dict]:
    global last_error
    try:
        result = _table("reservations").insert(row).execute()
        data = result.data or []
        last_error = ""
        return data[0] if data else None
    except Exception as exc:
        last_error = str(exc)
        logger.warning("create_reservation failed: %s", exc)
        # Older databases may not have the email column yet. Retry without it
        # so the booking still goes through and can be linked by phone.
        if row.get("email") and "email" in last_error.lower():
            logger.warning("Retrying reservation insert without email (column may be missing).")
            return create_reservation({k: v for k, v in row.items() if k != "email"})
        return None


def create_review(row: dict) -> Optional[dict]:
    try:
        result = _table("reviews").insert(row).execute()
        data = result.data or []
    except Exception as exc:
        logger.warning("create_review failed: %s", exc)
        return None
    return data[0] if data else None


def create_contact_message(row: dict) -> Optional[dict]:
    try:
        result = _table("contact_messages").insert(row).execute()
        data = result.data or []
    except Exception as exc:
        logger.warning("create_contact_message failed: %s", exc)
        return None
    return data[0] if data else None


def ping() -> bool:
    """Lightweight DB connectivity check — a single read against a catalogue table."""
    client = get_client()
    if client is None:
        return False
    try:
        client.table("locations").select("id").limit(1).execute()
        return True
    except Exception as exc:
        logger.warning("db ping failed: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Admin helpers
# ---------------------------------------------------------------------------

def _location_map() -> dict:
    """Map location id -> city for decorating reservation rows."""
    return {loc["id"]: loc["city"] for loc in get_locations()}


def get_all_reservations() -> list:
    """All reservations with an extra ``city`` field from the locations table."""
    reservations = fetch_all("reservations", order="created_at")
    if not reservations:
        return reservations
    loc_map = _location_map()
    for r in reservations:
        r["city"] = loc_map.get(r.get("location_id"), "—")
    return reservations


def get_reservation(reservation_id: str) -> Optional[dict]:
    """Single reservation with an extra ``city`` field, or None."""
    try:
        result = _table("reservations").select("*").eq("id", reservation_id).limit(1).execute()
        rows = result.data or []
    except Exception as exc:
        logger.warning("get_reservation(%s) failed: %s", reservation_id, exc)
        return None
    if not rows:
        return None
    row = rows[0]
    row["city"] = _location_map().get(row.get("location_id"), "—")
    return row


def update_reservation_status(reservation_id: str, status: str) -> bool:
    if status not in ("confirmed", "cancelled", "pending"):
        return False
    try:
        result = _table("reservations").update({"status": status}).eq("id", reservation_id).execute()
        return bool(result.data)
    except Exception as exc:
        logger.warning("update_reservation_status failed: %s", exc)
        return False


def get_all_reviews() -> list:
    return fetch_all("reviews", order="created_at")


def approve_review(review_id: str) -> bool:
    try:
        result = _table("reviews").update({"is_approved": True}).eq("id", review_id).execute()
        return bool(result.data)
    except Exception as exc:
        logger.warning("approve_review failed: %s", exc)
        return False


def delete_review(review_id: str) -> bool:
    try:
        result = _table("reviews").delete().eq("id", review_id).execute()
        return bool(result.data)
    except Exception as exc:
        logger.warning("delete_review failed: %s", exc)
        return False


def get_all_contacts() -> list:
    return fetch_all("contact_messages", order="created_at")


def archive_expired_reservations() -> int:
    """Move reservations whose date has passed into reservation_history."""
    client = get_client()
    if client is None:
        return 0
    try:
        result = client.rpc("archive_expired_reservations").execute()
        data = result.data if hasattr(result, "data") else None
        if isinstance(data, (int, float)):
            count = int(data)
            if count:
                logger.info("Archived %s expired reservation(s)", count)
            return count
        logger.info("archive_expired_reservations returned: %r", data)
        return 0
    except Exception as exc:
        logger.warning("archive_expired_reservations failed: %s", exc)
        return 0


def get_reservation_history() -> list:
    """Past bookings from reservation_history (newest archive first), with city."""
    try:
        result = (
            _table("reservation_history")
            .select("*")
            .order("archived_on", desc=True)
            .order("reservation_date", desc=True)
            .limit(100)
            .execute()
        )
        rows = result.data or []
    except Exception as exc:
        logger.warning("get_reservation_history failed: %s", exc)
        return []
    if not rows:
        return rows
    loc_map = _location_map()
    for r in rows:
        r["city"] = loc_map.get(r.get("location_id"), "—")
    return rows