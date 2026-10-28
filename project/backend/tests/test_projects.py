def test_create_project_uses_token_user_and_default_roles(owner, outsider):
    response = owner.post("/api/projects/", json={"name": "CRM", "id_user": outsider.id})
    assert response.status_code == 201
    project = response.json()
    assert project["id_user"] == owner.id
    assert project["creator_email"] == owner.email

    roles = owner.get(f"/api/project-roles/project/{project['id']}").json()
    assert sorted(r["name"] for r in roles) == ["Administrador", "Desarrollador", "Revisor"]


def test_blank_project_name_is_rejected(owner):
    assert owner.post("/api/projects/", json={"name": "   "}).status_code == 422


def test_list_only_returns_accessible_projects(owner, collaborator, outsider, project, membership):
    outsider.post("/api/projects/", json={"name": "Privado"})

    owner_names = [p["name"] for p in owner.get("/api/projects/").json()["items"]]
    collaborator_names = [p["name"] for p in collaborator.get("/api/projects/").json()["items"]]
    outsider_names = [p["name"] for p in outsider.get("/api/projects/").json()["items"]]

    assert owner_names == ["Portal Web"]
    assert collaborator_names == ["Portal Web"]
    assert outsider_names == ["Privado"]


def test_outsider_cannot_see_project(outsider, project):
    assert outsider.get(f"/api/projects/{project['id']}").status_code == 404


def test_collaborator_can_read_but_not_modify(collaborator, project, membership):
    assert collaborator.get(f"/api/projects/{project['id']}").status_code == 200
    assert collaborator.put(f"/api/projects/{project['id']}", json={"name": "X"}).status_code == 403
    assert collaborator.delete(f"/api/projects/{project['id']}").status_code == 403


def test_update_refreshes_updated_at(owner, project):
    response = owner.put(f"/api/projects/{project['id']}", json={"name": "Portal Web v2"})
    assert response.status_code == 200
    assert response.json()["name"] == "Portal Web v2"
    assert response.json()["updated_at"] > project["updated_at"]


def test_delete_project_removes_tasks_roles_and_members(owner, collaborator, project, membership):
    owner.post("/api/tasks/", json={"project_id": project["id"], "title": "Maquetar"})

    assert owner.delete(f"/api/projects/{project['id']}").status_code == 204
    assert owner.get(f"/api/projects/{project['id']}").status_code == 404
    assert collaborator.get(f"/api/project-members/user/{collaborator.id}").json() == []
    assert owner.get("/api/tasks/").json()["total"] == 0


def test_unknown_order_by_falls_back_to_default(owner, project):
    response = owner.get("/api/projects/", params={"order_by": "metadata"})
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_pagination(owner):
    for i in range(3):
        owner.post("/api/projects/", json={"name": f"P{i}"})
    page = owner.get("/api/projects/", params={"limit": 2, "order_by": "name", "order_dir": "asc"}).json()
    assert [p["name"] for p in page["items"]] == ["P0", "P1"]
    assert page["total"] == 3
    assert page["has_more"] is True
