def test_register_and_login(client):
    email = "auth_test_user@test.com"
    r = client.post(
        "/api/v1/auth/register",
        json={"name": "Auth User", "email": email, "password": "Demo@1234", "role": "CITIZEN"},
    )
    assert r.status_code == 201
    assert r.json()["user"]["email"] == email

    r2 = client.post("/api/v1/auth/login", json={"email": email, "password": "Demo@1234"})
    assert r2.status_code == 200
    assert "access_token" in r2.json()


def test_login_wrong_password(client):
    email = "auth_wrong_pw@test.com"
    client.post(
        "/api/v1/auth/register",
        json={"name": "Auth User 2", "email": email, "password": "Demo@1234", "role": "CITIZEN"},
    )
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "wrong-password"})
    assert r.status_code == 401


def test_me_requires_token(client):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


def test_me_with_token(client, citizen_token):
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {citizen_token}"})
    assert r.status_code == 200
    assert r.json()["role"] == "CITIZEN"
