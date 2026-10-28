from datetime import timedelta

from app.core.clock import utcnow


def test_empty_summary(owner):
    summary = owner.get("/api/dashboard/summary").json()
    assert summary["projects"] == {"owned": 0, "collaborating": 0, "total": 0}
    assert summary["tasks"]["assigned"] == 0
    assert summary["tasks"]["completion_rate"] == 0
    assert summary["clients"]["by_status"] == {"lead": 0, "active": 0, "inactive": 0}
    assert summary["due_soon"] == []


def test_summary_counts(owner, collaborator, project, membership):
    soon = (utcnow() + timedelta(days=2)).isoformat()
    later = (utcnow() + timedelta(days=30)).isoformat()
    for title, status, due in [
        ("Entregar mockups", "pending", soon),
        ("Revisar copy", "completed", soon),
        ("Planear sprint", "in_progress", later),
    ]:
        owner.post("/api/tasks/", json={
            "project_id": project["id"], "title": title, "status": status,
            "due_date": due, "assigned_to": collaborator.id,
        })
    collaborator.post("/api/clients/", json={"name": "Globex", "status": "active"})

    summary = collaborator.get("/api/dashboard/summary").json()
    assert summary["projects"] == {"owned": 0, "collaborating": 1, "total": 1}
    assert summary["tasks"]["assigned"] == 3
    assert summary["tasks"]["open"] == 2
    assert summary["tasks"]["completion_rate"] == 33
    assert summary["clients"]["by_status"]["active"] == 1
    assert [t["title"] for t in summary["due_soon"]] == ["Entregar mockups"]
    assert [p["name"] for p in summary["recent_projects"]] == ["Portal Web"]


def test_seed_creates_demo_data_once(client):
    from sqlmodel import Session
    from app.core.database import engine
    from app.seed import DEMO_EMAIL, DEMO_PASSWORD, seed

    with Session(engine) as session:
        assert seed(session) is True
        assert seed(session) is False

    token = client.post("/api/auth/login", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD}).json()["access_token"]
    summary = client.get("/api/dashboard/summary", headers={"Authorization": f"Bearer {token}"}).json()
    assert summary["projects"] == {"owned": 3, "collaborating": 1, "total": 4}
    assert summary["clients"]["total"] == 7
    assert summary["tasks"]["by_status"]["overdue"] == 1
