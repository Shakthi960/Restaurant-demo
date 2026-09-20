"""JSON API endpoints backed by Supabase.

Auth note: supabase-py attaches the configured key to every request. When the
service role key is set (recommended) RLS is bypassed on the server side.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request

from app import db, schemas
from app.limiter import limiter

router = APIRouter(prefix="/api")


def _ist_now() -> datetime:
    """Current time in India (Asia/Kolkata)."""
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo("Asia/Kolkata"))
    except Exception:  # pragma: no cover - defensive
        from datetime import timedelta, timezone

        return datetime.now(timezone.utc) + timedelta(minutes=330)


def _require_db():
    if db.get_client() is None:
        raise HTTPException(
            status_code=503,
            detail="Backend database not configured. Add SUPABASE_URL and a key to backend/.env.",
        )


@router.get("/menu")
def api_menu(category: Optional[str] = Query(None)):
    return {"data": db.get_dishes(category=category)}


@router.get("/locations")
def api_locations():
    return {"data": db.get_locations()}


@router.get("/gallery")
def api_gallery():
    return {"data": db.get_gallery_images()}


@router.get("/reviews")
def api_reviews():
    return {"data": db.get_reviews()}


@router.post("/reservations", response_model=schemas.ReservationOut, status_code=201)
@limiter.limit("10/minute")
def create_reservation(request: Request, payload: schemas.ReservationIn):
    _require_db()
    location_id = db.get_location_id(payload.location)
    if location_id is None:
        raise HTTPException(status_code=400, detail="Unknown location. Choose a city from our list.")

    # Reject dates/times already in the past (per India time)
    slot = datetime(
        payload.date.year, payload.date.month, payload.date.day,
        payload.time.hour, payload.time.minute,
        tzinfo=_ist_now().tzinfo,
    )
    if slot < _ist_now():
        raise HTTPException(status_code=400, detail="That time slot has already passed. Please pick a later time.")

    row = {
        "name": payload.name,
        "phone": payload.phone,
        "location_id": location_id,
        "reservation_date": payload.date.isoformat(),
        "reservation_time": payload.time.strftime("%H:%M"),
        "guests": payload.guests,
        "status": "pending",
    }
    email = (payload.email or "").strip()
    if email:
        row["email"] = email  # only when set — older DBs may not have the column
    created = db.create_reservation(row)
    if created is None:
        reason = db.last_error or "unknown database error"
        hint = " Email will not be stored until the matching DB migration runs (see database/supabase/schema.sql)." if "email" in reason.lower() else ""
        raise HTTPException(
            status_code=500,
            detail=f"Reservation could not be saved. Reason: {reason[:200]}.{hint}",
        )

    reservation_id = str(created.get("id", ""))

    return schemas.ReservationOut(id=reservation_id, status="pending")


@router.post("/reviews", response_model=schemas.ReviewOut, status_code=201)
@limiter.limit("10/minute")
def create_review(request: Request, payload: schemas.ReviewIn):
    _require_db()
    row = {
        "author": payload.author,
        "city": payload.city or "",
        "rating": payload.rating,
        "review": payload.review,
        "is_approved": False,
    }
    created = db.create_review(row)
    if created is None:
        raise HTTPException(status_code=500, detail="Review could not be saved. Please try again.")

    return schemas.ReviewOut(id=str(created.get("id", "")), status="pending_moderation")


@router.post("/contact", response_model=schemas.ContactOut, status_code=201)
@limiter.limit("10/minute")
def create_contact_message(request: Request, payload: schemas.ContactIn):
    _require_db()
    row = {
        "name": payload.name,
        "email": payload.email,
        "phone": payload.phone or "",
        "message": payload.message,
    }
    created = db.create_contact_message(row)
    if created is None:
        raise HTTPException(status_code=500, detail="Message could not be saved. Please try again.")

    return schemas.ContactOut(id=str(created.get("id", "")), status="received")