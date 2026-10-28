def create_client(user, **fields):
    payload = {"name": "Acme S.A.S.", **fields}
    response = user.post("/api/clients/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_client_with_defaults(owner):
    client = create_client(owner, email="", phone="  ", company="Acme")
    assert client["status"] == "lead"
    assert client["owner_id"] == owner.id
    assert client["email"] is None
    assert client["phone"] is None


def test_invalid_email_or_status_is_rejected(owner):
    assert owner.post("/api/clients/", json={"name": "X", "email": "no-es-correo"}).status_code == 422
    assert owner.post("/api/clients/", json={"name": "X", "status": "vip"}).status_code == 422
    assert owner.post("/api/clients/", json={"name": "  "}).status_code == 422


def test_clients_are_private_to_their_owner(owner, outsider):
    client = create_client(owner)
    assert outsider.get(f"/api/clients/{client['id']}").status_code == 404
    assert outsider.put(f"/api/clients/{client['id']}", json={"name": "X"}).status_code == 404
    assert outsider.delete(f"/api/clients/{client['id']}").status_code == 404
    assert outsider.get("/api/clients/").json()["total"] == 0


def test_update_and_delete(owner):
    client = create_client(owner)
    updated = owner.put(f"/api/clients/{client['id']}", json={"status": "active", "notes": "Firmó contrato"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "active"
    assert updated.json()["name"] == "Acme S.A.S."

    assert owner.delete(f"/api/clients/{client['id']}").status_code == 204
    assert owner.get(f"/api/clients/{client['id']}").status_code == 404


def test_search_and_filter(owner):
    create_client(owner, name="Globex", company="Globex Corp", status="active")
    create_client(owner, name="Initech", email="compras@initech.com")

    assert [c["name"] for c in owner.get("/api/clients/", params={"status": "active"}).json()["items"]] == ["Globex"]
    assert [c["name"] for c in owner.get("/api/clients/", params={"search": "initech.com"}).json()["items"]] == ["Initech"]
