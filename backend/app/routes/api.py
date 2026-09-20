"""JSON API endpoints backed by Supabase.

Auth note: supabase-py attaches the configured key to every request. When the
service role key is set (recommended) RLS is bypassed on the server side.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request

from app import db, schemas
from app.limiter import limiter

router = APIRouter(prefix="/api")


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

    row = {
        "name": payload.name,
        "phone": payload.phone,
        "email": (payload.email or "").strip(),
        "location_id": location_id,
        "reservation_date": payload.date.isoformat(),
        "reservation_time": payload.time.strftime("%H:%M"),
        "guests": payload.guests,
        "status": "pending",
    }
    created = db.create_reservation(row)
    if created is None:
        raise HTTPException(status_code=500, detail="Reservation could not be saved. Please try again.")

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