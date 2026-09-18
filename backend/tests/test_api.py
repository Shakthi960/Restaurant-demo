from datetime import date, timedelta

import pytest

from app import db

VALID_RESERVATION = {
    "name": "Test User",
    "phone": "+91 90000 00000",
    "location": "chennai",
    "date": (date.today() + timedelta(days=2)).isoformat(),
    "time": "19:00",
    "guests": 2,
}


def test_menu_empty(client):
    resp = client.get("/api/menu")
    assert resp.status_code == 200
    assert resp.json() == {"data": []}


def test_create_reservation_ok(client):
    resp = client.post("/api/reservations", json=VALID_RESERVATION)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == "res-1"
    assert body["status"] == "pending"


def test_create_reservation_rejects_past_date(client):
    payload = {**VALID_RESERVATION, "date": (date.today() - timedelta(days=1)).isoformat()}
    resp = client.post("/api/reservations", json=payload)
    assert resp.status_code == 422


def test_create_reservation_rejects_bad_phone(client):
    payload = {**VALID_RESERVATION, "phone": "12345"}
    resp = client.post("/api/reservations", json=payload)
    assert resp.status_code == 422


def test_create_reservation_unknown_location(client, monkeypatch):
    monkeypatch.setattr(db, "get_location_id", lambda slug: None)
    resp = client.post("/api/reservations", json=VALID_RESERVATION)
    assert resp.status_code == 400
    assert "location" in resp.json()["detail"].lower()


def test_create_review_ok(client):
    payload = {"author": "Guest One", "city": "Chennai", "rating": 5, "review": "Wonderful food."}
    resp = client.post("/api/reviews", json=payload)
    assert resp.status_code == 201
    assert resp.json()["status"] == "pending_moderation"


def test_create_review_rating_range(client):
    payload = {"author": "Guest One", "rating": 9, "review": "Wonderful food."}
    resp = client.post("/api/reviews", json=payload)
    assert resp.status_code == 422


def test_contact_rejects_bad_email(client):
    payload = {"name": "Guest One", "email": "not-an-email", "message": "hello there"}
    resp = client.post("/api/contact", json=payload)
    assert resp.status_code == 422


def test_contact_ok(client):
    payload = {"name": "Guest One", "email": "guest@example.com", "message": "hello there"}
    resp = client.post("/api/contact", json=payload)
    assert resp.status_code == 201
    assert resp.json()["status"] == "received"