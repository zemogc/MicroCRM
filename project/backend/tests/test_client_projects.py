from sqlalchemy import create_engine, inspect, text


def create_client(user, name="Acme"):
    response = user.post("/api/clients/", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()


def test_project_linked_to_client(owner):
    client = create_client(owner)
    project = owner.post("/api/projects/", json={"name": "Web Acme", "client_id": client["id"]}).json()
    assert project["client_id"] == client["id"]
    assert project["client_name"] == "Acme"

    assert owner.get(f"/api/clients/{client['id']}").json()["projects_count"] == 1
    filtered = owner.get("/api/projects/", params={"client_id": client["id"]}).json()
    assert [p["name"] for p in filtered["items"]] == ["Web Acme"]


def test_cannot_link_client_of_another_user(owner, outsider):
    foreign = create_client(outsider, "Ajeno")
    response = owner.post("/api/projects/", json={"name": "X", "client_id": foreign["id"]})
    assert response.status_code == 400

    project = owner.post("/api/projects/", json={"name": "Y"}).json()
    response = owner.put(f"/api/projects/{project['id']}", json={"client_id": foreign["id"]})
    assert response.status_code == 400


def test_change_and_unlink_client(owner):
    first, second = create_client(owner, "Uno"), create_client(owner, "Dos")
    project = owner.post("/api/projects/", json={"name": "P", "client_id": first["id"]}).json()

    moved = owner.put(f"/api/projects/{project['id']}", json={"client_id": second["id"]}).json()
    assert moved["client_name"] == "Dos"

    unlinked = owner.put(f"/api/projects/{project['id']}", json={"client_id": None}).json()
    assert unlinked["client_id"] is None
    assert unlinked["name"] == "P"


def test_deleting_client_keeps_the_project(owner):
    client = create_client(owner)
    project = owner.post("/api/projects/", json={"name": "P", "client_id": client["id"]}).json()

    assert owner.delete(f"/api/clients/{client['id']}").status_code == 204
    kept = owner.get(f"/api/projects/{project['id']}").json()
    assert kept["client_id"] is None
    assert kept["client_name"] is None


def test_collaborator_sees_client_name(owner, collaborator, project, membership):
    client = create_client(owner)
    owner.put(f"/api/projects/{project['id']}", json={"client_id": client["id"]})
    assert collaborator.get(f"/api/projects/{project['id']}").json()["client_name"] == "Acme"


def test_upgrade_adds_client_id_to_old_projects_table(tmp_path, monkeypatch):
    """Databases created before this version get the new column on startup"""
    import app.core.database as database

    old_engine = create_engine(f"sqlite:///{tmp_path / 'old.db'}")
    with old_engine.begin() as connection:
        connection.execute(text("CREATE TABLE projects (id INTEGER PRIMARY KEY, name VARCHAR(100))"))
        connection.execute(text("INSERT INTO projects (id, name) VALUES (1, 'Antiguo')"))

    monkeypatch.setattr(database, "engine", old_engine)
    database.upgrade_schema()
    database.upgrade_schema()  # idempotent

    columns = {c["name"] for c in inspect(old_engine).get_columns("projects")}
    assert "client_id" in columns
    with old_engine.connect() as connection:
        assert connection.execute(text("SELECT name, client_id FROM projects")).one() == ("Antiguo", None)
