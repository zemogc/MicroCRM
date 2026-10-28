def test_owner_adds_collaborator(collaborator, project, membership):
    assert membership["user_id"] == collaborator.id
    assert membership["role_name"] == "Desarrollador"

    mine = collaborator.get(f"/api/project-members/user/{collaborator.id}").json()
    assert [m["project_name"] for m in mine] == ["Portal Web"]


def test_cannot_list_memberships_of_another_user(owner, collaborator):
    assert owner.get(f"/api/project-members/user/{collaborator.id}").status_code == 403


def test_owner_cannot_be_added_as_member(owner, project):
    roles = owner.get(f"/api/project-roles/project/{project['id']}").json()
    response = owner.post("/api/project-members/", json={
        "project_id": project["id"], "user_id": owner.id, "project_role_id": roles[0]["id"]
    })
    assert response.status_code == 400


def test_duplicate_membership_is_rejected(owner, collaborator, project, membership):
    response = owner.post("/api/project-members/", json={
        "project_id": project["id"], "user_id": collaborator.id, "project_role_id": membership["project_role_id"]
    })
    assert response.status_code == 400


def test_role_from_another_project_is_rejected(owner, outsider, collaborator, project):
    other = outsider.post("/api/projects/", json={"name": "Ajeno"}).json()
    foreign_role = outsider.get(f"/api/project-roles/project/{other['id']}").json()[0]

    response = owner.post("/api/project-members/", json={
        "project_id": project["id"], "user_id": collaborator.id, "project_role_id": foreign_role["id"]
    })
    assert response.status_code == 400


def test_collaborator_cannot_manage_members(collaborator, outsider, project, membership):
    response = collaborator.post("/api/project-members/", json={
        "project_id": project["id"], "user_id": outsider.id, "project_role_id": membership["project_role_id"]
    })
    assert response.status_code == 403
    assert collaborator.delete(f"/api/project-members/{membership['id']}").status_code == 403


def test_owner_changes_role_and_removes_member(owner, project, membership):
    roles = owner.get(f"/api/project-roles/project/{project['id']}").json()
    reviewer = next(r for r in roles if r["name"] == "Revisor")

    response = owner.put(f"/api/project-members/{membership['id']}", json={"project_role_id": reviewer["id"]})
    assert response.status_code == 200
    assert response.json()["role_name"] == "Revisor"

    assert owner.delete(f"/api/project-members/{membership['id']}").status_code == 204


def test_custom_roles(owner, collaborator, project, membership):
    created = owner.post("/api/project-roles/", json={"project_id": project["id"], "name": "QA"})
    assert created.status_code == 201
    assert owner.post("/api/project-roles/", json={"project_id": project["id"], "name": "QA"}).status_code == 400
    assert collaborator.post("/api/project-roles/", json={"project_id": project["id"], "name": "Hack"}).status_code == 403

    renamed = owner.put(f"/api/project-roles/{created.json()['id']}", json={"name": "Calidad"})
    assert renamed.json()["name"] == "Calidad"
    assert owner.delete(f"/api/project-roles/{created.json()['id']}").status_code == 204


def test_role_in_use_cannot_be_deleted(owner, membership):
    response = owner.delete(f"/api/project-roles/{membership['project_role_id']}")
    assert response.status_code == 400
