import re


def _login(client):
    resp = client.post("/admin/login", data={"password": "test-password"}, follow_redirects=False)
    assert resp.status_code == 303
    assert "galaxy_admin" in resp.cookies


def test_admin_redirects_anonymous(client):
    resp = client.get("/admin", follow_redirects=False)
    assert resp.status_code == 303
    assert "/admin/login" in resp.headers["location"]


def test_confirm_redirects_anonymous(client):
    resp = client.post("/admin/reservations/res-1/confirm", data={}, follow_redirects=False)
    assert resp.status_code == 303
    assert "/admin/login" in resp.headers["location"]


def test_login_wrong_password(client):
    resp = client.post("/admin/login", data={"password": "wrong"}, follow_redirects=False)
    assert resp.status_code == 200
    assert "Invalid password" in resp.text


def test_login_ok_and_dashboard(client):
    _login(client)
    resp = client.get("/admin")
    assert resp.status_code == 200
    assert "Reservations" in resp.text
    assert "csrf_token" in resp.text


def test_csrf_rejects_wrong_token(client):
    _login(client)
    resp = client.post(
        "/admin/reservations/res-1/confirm",
        data={"csrf_token": "deadbeef"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "Session%20expired" in resp.headers["location"]


def test_csrf_accepts_valid_token(client):
    _login(client)
    page = client.get("/admin").text
    match = re.search(r'name="csrf_token" value="([0-9a-f]+)"', page)
    assert match, "csrf field not rendered"
    token = match.group(1)
    resp = client.post(
        "/admin/reservations/res-1/confirm",
        data={"csrf_token": token},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "Reservation%20confirmed" in resp.headers["location"]


def test_logout_clears_cookie(client):
    _login(client)
    resp = client.get("/admin/logout", follow_redirects=False)
    assert resp.status_code == 303
    set_cookie = resp.headers.get("set-cookie", "")
    assert "galaxy_admin=" in set_cookie
    assert "Max-Age=0" in set_cookie or "expires" in set_cookie.lower()