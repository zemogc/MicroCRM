import os
import tempfile

# Configure the app before it is imported: isolated SQLite file, no scheduler, generous limits
_db_dir = tempfile.mkdtemp(prefix="microcrm-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_db_dir, 'test.db')}"
os.environ["ENABLE_SCHEDULER"] = "false"
os.environ["RATE_LIMIT_AUTH_PER_MIN"] = "1000"
os.environ["RATE_LIMIT_API_PER_MIN"] = "1000"
os.environ["SECRET_KEY"] = "test-secret"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from app.core.database import engine, init_db
from app.core.rate_limit import API_BUCKET, AUTH_BUCKET
from app.main import app

PASSWORD = "Secreta123"


@pytest.fixture(autouse=True)
def fresh_database():
    init_db()
    yield
    SQLModel.metadata.drop_all(engine)
    AUTH_BUCKET.clear()
    API_BUCKET.clear()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class ApiUser:
    """Registered user with a client that sends its token"""

    def __init__(self, client: TestClient, name: str):
        email = f"{name.lower()}@example.com"
        response = client.post("/api/auth/register", json={"name": name, "email": email, "password": PASSWORD})
        assert response.status_code == 201, response.text
        data = response.json()
        self.id = data["user"]["id"]
        self.email = email
        self.headers = {"Authorization": f"Bearer {data['access_token']}"}
        self._client = client

    def get(self, url, **kw):
        return self._client.get(url, headers=self.headers, **kw)

    def post(self, url, **kw):
        return self._client.post(url, headers=self.headers, **kw)

    def put(self, url, **kw):
        return self._client.put(url, headers=self.headers, **kw)

    def delete(self, url, **kw):
        return self._client.delete(url, headers=self.headers, **kw)


@pytest.fixture
def make_user(client):
    return lambda name: ApiUser(client, name)


@pytest.fixture
def owner(make_user):
    return make_user("Owner")


@pytest.fixture
def collaborator(make_user):
    return make_user("Colaborador")


@pytest.fixture
def outsider(make_user):
    return make_user("Externo")


@pytest.fixture
def project(owner):
    response = owner.post("/api/projects/", json={"name": "Portal Web", "description": "Rediseño"})
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def membership(owner, collaborator, project):
    roles = owner.get(f"/api/project-roles/project/{project['id']}").json()
    developer = next(r for r in roles if r["name"] == "Desarrollador")
    response = owner.post("/api/project-members/", json={
        "project_id": project["id"],
        "user_id": collaborator.id,
        "project_role_id": developer["id"],
    })
    assert response.status_code == 201, response.text
    return response.json()
