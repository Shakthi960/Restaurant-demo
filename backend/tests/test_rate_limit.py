PAYLOAD = {
    "name": "Guest One",
    "email": "guest@example.com",
    "message": "hello there",
}


def test_rate_limit_contact(client):
    codes = [client.post("/api/contact", json=PAYLOAD).status_code for _ in range(12)]
    assert codes[:10] == [201] * 10
    assert codes[10:] == [429, 429]


def test_rate_limit_isolation(client):
    assert client.post("/api/contact", json=PAYLOAD).status_code == 201