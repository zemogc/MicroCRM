def test_directory_lists_users_without_passwords(owner, collaborator):
    page = owner.get("/api/users/", params={"search": "colab"}).json()
    assert [u["email"] for u in page["items"]] == [collaborator.email]
    assert "password" not in page["items"][0]


def test_order_by_password_is_ignored(owner, collaborator):
    assert owner.get("/api/users/", params={"order_by": "password"}).status_code == 200


def test_user_updates_own_profile(owner):
    response = owner.put(f"/api/users/{owner.id}", json={"name": "Nuevo Nombre"})
    assert response.status_code == 200
    assert response.json()["name"] == "Nuevo Nombre"


def test_user_cannot_update_or_delete_others(owner, collaborator):
    assert owner.put(f"/api/users/{collaborator.id}", json={"name": "Hack"}).status_code == 403
    assert owner.delete(f"/api/users/{collaborator.id}").status_code == 403


def test_email_must_stay_unique(owner, collaborator):
    response = owner.put(f"/api/users/{owner.id}", json={"email": collaborator.email})
    assert response.status_code == 400


def test_deleting_account_removes_owned_projects_and_unassigns_tasks(owner, collaborator, project, membership):
    other = collaborator.post("/api/projects/", json={"name": "Del colaborador"}).json()
    roles = collaborator.get(f"/api/project-roles/project/{other['id']}").json()
    collaborator.post("/api/project-members/", json={
        "project_id": other["id"], "user_id": owner.id, "project_role_id": roles[0]["id"]
    })
    task = owner.post("/api/tasks/", json={
        "project_id": project["id"], "title": "Asignada", "assigned_to": collaborator.id
    }).json()

    assert collaborator.delete(f"/api/users/{collaborator.id}").status_code == 204

    assert owner.get(f"/api/projects/{other['id']}").status_code == 404
    assert owner.get(f"/api/tasks/{task['id']}").json()["assigned_to"] is None
    assert owner.get(f"/api/project-members/project/{project['id']}").json() == []
