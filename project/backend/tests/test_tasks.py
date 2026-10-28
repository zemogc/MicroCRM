from datetime import timedelta

from app.core.clock import utcnow


def create_task(user, project, **fields):
    payload = {"project_id": project["id"], "title": "Diseñar landing", **fields}
    response = user.post("/api/tasks/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_owner_creates_task_assigned_to_collaborator(owner, collaborator, project, membership):
    task = create_task(owner, project, assigned_to=collaborator.id)
    assert task["status"] == "pending"
    assert task["assigned_to_email"] == collaborator.email
    assert task["project_name"] == "Portal Web"


def test_task_cannot_be_assigned_outside_the_project(owner, outsider, project):
    response = owner.post("/api/tasks/", json={
        "project_id": project["id"], "title": "X", "assigned_to": outsider.id
    })
    assert response.status_code == 400


def test_invalid_status_is_rejected(owner, project):
    response = owner.post("/api/tasks/", json={"project_id": project["id"], "title": "X", "status": "done"})
    assert response.status_code == 422


def test_collaborator_cannot_create_tasks(collaborator, project, membership):
    response = collaborator.post("/api/tasks/", json={"project_id": project["id"], "title": "X"})
    assert response.status_code == 403


def test_assignee_can_only_change_status(owner, collaborator, project, membership):
    task = create_task(owner, project, assigned_to=collaborator.id)

    moved = collaborator.put(f"/api/tasks/{task['id']}", json={"status": "in_progress"})
    assert moved.status_code == 200
    assert moved.json()["status"] == "in_progress"

    renamed = collaborator.put(f"/api/tasks/{task['id']}", json={"title": "Otro"})
    assert renamed.status_code == 403
    assert collaborator.delete(f"/api/tasks/{task['id']}").status_code == 403


def test_collaborator_cannot_update_unassigned_task(owner, collaborator, project, membership):
    task = create_task(owner, project)
    assert collaborator.put(f"/api/tasks/{task['id']}", json={"status": "completed"}).status_code == 403


def test_outsider_cannot_see_tasks(owner, outsider, project):
    task = create_task(owner, project)
    assert outsider.get(f"/api/tasks/{task['id']}").status_code == 404
    assert outsider.get(f"/api/tasks/project/{project['id']}").status_code == 404
    assert outsider.get("/api/tasks/").json()["total"] == 0


def test_my_tasks_only_for_myself(owner, collaborator, project, membership):
    create_task(owner, project, assigned_to=collaborator.id)
    assert len(collaborator.get(f"/api/tasks/user/{collaborator.id}").json()) == 1
    assert owner.get(f"/api/tasks/user/{collaborator.id}").status_code == 403


def test_static_task_routes_are_not_captured_by_task_id(owner):
    response = owner.get("/api/tasks/overdue-count")
    assert response.status_code == 200
    assert response.json()["overdue_count"] == 0


def test_past_due_tasks_become_overdue(owner, project):
    yesterday = (utcnow() - timedelta(days=1)).isoformat()
    tomorrow = (utcnow() + timedelta(days=1)).isoformat()
    late = create_task(owner, project, title="Atrasada", due_date=yesterday)
    review = create_task(owner, project, title="En revisión", due_date=yesterday, status="in_review")
    on_time = create_task(owner, project, title="A tiempo", due_date=tomorrow)

    assert owner.get("/api/tasks/overdue-count").json()["overdue_count"] == 1

    statuses = {t["id"]: t["status"] for t in owner.get(f"/api/tasks/project/{project['id']}").json()}
    assert statuses[late["id"]] == "overdue"
    assert statuses[review["id"]] == "in_review"
    assert statuses[on_time["id"]] == "pending"


def test_filter_and_search(owner, project):
    create_task(owner, project, title="Configurar CI", status="completed")
    create_task(owner, project, title="Escribir README")

    completed = owner.get("/api/tasks/", params={"status": "completed"}).json()
    assert [t["title"] for t in completed["items"]] == ["Configurar CI"]

    found = owner.get("/api/tasks/", params={"search": "readme"}).json()
    assert [t["title"] for t in found["items"]] == ["Escribir README"]
