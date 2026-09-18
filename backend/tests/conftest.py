import os
import sys
from pathlib import Path

os.environ.setdefault("ADMIN_PASSWORD", "test-password")
os.environ.setdefault("SECRET_KEY", "test-secret")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

import main as main_mod
from app import db, whatsapp
from app.limiter import limiter

FAKE_RESERVATION = {
    "id": "res-1",
    "name": "Test User",
    "phone": "9000000000",
    "city": "Chennai",
    "location_id": "loc-1",
    "reservation_date": "2026-09-20",
    "reservation_time": "19:00",
    "guests": 2,
    "status": "pending",
    "created_at": "2026-09-10",
}


@pytest.fixture(autouse=True)
def isolated(monkeypatch):
    limiter.reset()
    monkeypatch.setattr(db, "get_client", lambda: object())
    monkeypatch.setattr(db, "get_dishes", lambda *a, **k: [])
    monkeypatch.setattr(db, "get_locations", lambda: [])
    monkeypatch.setattr(db, "get_gallery_images", lambda: [])
    monkeypatch.setattr(db, "get_reviews", lambda: [])
    monkeypatch.setattr(db, "get_location_id", lambda slug: "loc-1" if slug else None)
    monkeypatch.setattr(db, "create_reservation", lambda row: {**row, "id": "res-1"})
    monkeypatch.setattr(db, "create_review", lambda row: {**row, "id": "rev-1"})
    monkeypatch.setattr(db, "create_contact_message", lambda row: {**row, "id": "msg-1"})
    monkeypatch.setattr(db, "get_all_reservations", lambda: [FAKE_RESERVATION])
    monkeypatch.setattr(db, "get_all_reviews", lambda: [])
    monkeypatch.setattr(db, "get_all_contacts", lambda: [])
    monkeypatch.setattr(db, "get_reservation", lambda rid: dict(FAKE_RESERVATION))
    monkeypatch.setattr(db, "update_reservation_status", lambda rid, status: True)
    monkeypatch.setattr(db, "approve_review", lambda rid: True)
    monkeypatch.setattr(db, "delete_review", lambda rid: True)
    monkeypatch.setattr(db, "archive_expired_reservations", lambda: 0)
    monkeypatch.setattr(db, "get_reservation_history", lambda: [])
    monkeypatch.setattr(db, "ping", lambda: True)
    monkeypatch.setattr(whatsapp, "send_received", lambda **k: True)
    monkeypatch.setattr(whatsapp, "send_confirmed", lambda **k: True)
    yield


@pytest.fixture()
def client():
    with TestClient(main_mod.app) as c:
        yield c