from app import db


def test_healthz_ok(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert resp.json()["db_reachable"] is True


def test_healthz_degraded_when_db_down(client, monkeypatch):
    monkeypatch.setattr(db, "ping", lambda: False)
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "degraded"
    assert resp.json()["db_reachable"] is False