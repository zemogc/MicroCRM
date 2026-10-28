from tests.conftest import PASSWORD


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_register_returns_token_and_user(client):
    response = client.post("/api/auth/register", json={
        "name": "  Ana  ", "email": "ana@example.com", "password": PASSWORD
    })
    assert response.status_code == 201
    data = response.json()
    assert data["access_token"]
    assert data["user"]["name"] == "Ana"
    assert "password" not in data["user"]


def test_register_rejects_duplicate_email(client, owner):
    response = client.post("/api/auth/register", json={
        "name": "Otro", "email": owner.email, "password": PASSWORD
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


def test_register_rejects_weak_password_with_readable_message(client):
    response = client.post("/api/auth/register", json={
        "name": "Ana", "email": "ana@example.com", "password": "corta"
    })
    assert response.status_code == 422
    assert response.json()["detail"] == "La contraseña debe tener al menos 8 caracteres"


def test_login_and_me(client, owner):
    response = client.post("/api/auth/login", json={"email": owner.email, "password": PASSWORD})
    assert response.status_code == 200
    token = response.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == owner.email


def test_login_wrong_password(client, owner):
    response = client.post("/api/auth/login", json={"email": owner.email, "password": "Incorrecta123"})
    assert response.status_code == 401


def test_missing_or_invalid_token_is_401(client):
    assert client.get("/api/projects/").status_code == 401
    response = client.get("/api/projects/", headers={"Authorization": "Bearer basura"})
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_auth_rate_limit_returns_retry_after(client, monkeypatch):
    from app.core.settings import get_settings
    monkeypatch.setattr(get_settings(), "rate_limit_auth_per_min", 2)

    payload = {"email": "nadie@example.com", "password": PASSWORD}
    for _ in range(2):
        assert client.post("/api/auth/login", json=payload).status_code == 401
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 429
    assert "retry-after" in response.headers
