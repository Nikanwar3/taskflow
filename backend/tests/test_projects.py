def post_project(client, name="Work", description=None):
    payload = {"name": name}
    if description:
        payload["description"] = description
    return client.post("/projects/", json=payload)


def test_create_project_returns_201(client):
    resp = post_project(client)
    assert resp.status_code == 201
    assert resp.get_json()["name"] == "Work"


def test_create_project_missing_name_returns_422(client):
    resp = client.post("/projects/", json={})
    assert resp.status_code == 422
    assert "name" in resp.get_json()["errors"]


def test_create_duplicate_project_name_returns_409(client):
    post_project(client, name="Unique")
    resp = post_project(client, name="Unique")
    assert resp.status_code == 409


def test_list_projects(client):
    post_project(client, name="Alpha")
    post_project(client, name="Beta")
    resp = client.get("/projects/")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_get_project(client):
    project_id = post_project(client).get_json()["id"]
    resp = client.get(f"/projects/{project_id}")
    assert resp.status_code == 200
    assert resp.get_json()["id"] == project_id


def test_get_nonexistent_project_returns_404(client):
    resp = client.get("/projects/9999")
    assert resp.status_code == 404


def test_update_project(client):
    project_id = post_project(client).get_json()["id"]
    resp = client.put(f"/projects/{project_id}", json={"name": "Personal"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Personal"


def test_delete_project(client):
    project_id = post_project(client).get_json()["id"]
    resp = client.delete(f"/projects/{project_id}")
    assert resp.status_code == 204
    assert client.get(f"/projects/{project_id}").status_code == 404


def test_project_name_too_long_returns_422(client):
    resp = post_project(client, name="x" * 101)
    assert resp.status_code == 422
