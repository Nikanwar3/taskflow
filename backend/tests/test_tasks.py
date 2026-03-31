import json
from datetime import date, timedelta


def post_task(client, **kwargs):
    payload = {"title": "Test task", "priority": "medium", **kwargs}
    return client.post("/tasks/", json=payload)


def post_project(client, name="Work"):
    return client.post("/projects/", json={"name": name})


# --- creation ---

def test_create_task_returns_201(client):
    resp = post_task(client)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == "Test task"
    assert data["status"] == "todo"
    assert data["priority"] == "medium"


def test_create_task_missing_title_returns_422(client):
    resp = client.post("/tasks/", json={"priority": "low"})
    assert resp.status_code == 422
    assert "title" in resp.get_json()["errors"]


def test_create_task_invalid_priority_returns_422(client):
    resp = post_task(client, priority="urgent")
    assert resp.status_code == 422


def test_create_task_due_date_in_past_returns_422(client):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    resp = post_task(client, due_date=yesterday)
    assert resp.status_code == 422
    assert "due_date" in resp.get_json()["errors"]


def test_create_task_with_future_due_date(client):
    future = (date.today() + timedelta(days=3)).isoformat()
    resp = post_task(client, due_date=future)
    assert resp.status_code == 201
    assert resp.get_json()["due_date"] == future


def test_create_task_with_nonexistent_project_returns_422(client):
    resp = post_task(client, project_id=999)
    assert resp.status_code == 422


def test_create_task_with_valid_project(client):
    project_id = post_project(client).get_json()["id"]
    resp = post_task(client, project_id=project_id)
    assert resp.status_code == 201
    assert resp.get_json()["project_id"] == project_id


# --- retrieval ---

def test_list_tasks(client):
    post_task(client, title="A")
    post_task(client, title="B")
    resp = client.get("/tasks/")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_get_task(client):
    task_id = post_task(client).get_json()["id"]
    resp = client.get(f"/tasks/{task_id}")
    assert resp.status_code == 200
    assert resp.get_json()["id"] == task_id


def test_get_nonexistent_task_returns_404(client):
    resp = client.get("/tasks/9999")
    assert resp.status_code == 404


def test_filter_tasks_by_status(client):
    post_task(client, title="todo task")
    task_id = post_task(client, title="progress task").get_json()["id"]
    client.patch(f"/tasks/{task_id}/status", json={"status": "in_progress"})
    resp = client.get("/tasks/?status=in_progress")
    tasks = resp.get_json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "in_progress"


def test_filter_tasks_by_priority(client):
    post_task(client, priority="low")
    post_task(client, priority="high")
    resp = client.get("/tasks/?priority=low")
    tasks = resp.get_json()
    assert all(t["priority"] == "low" for t in tasks)


# --- status transitions ---

def test_valid_status_transition_todo_to_in_progress(client):
    task_id = post_task(client).get_json()["id"]
    resp = client.patch(f"/tasks/{task_id}/status", json={"status": "in_progress"})
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "in_progress"


def test_invalid_status_transition_todo_to_done_returns_422(client):
    task_id = post_task(client).get_json()["id"]
    resp = client.patch(f"/tasks/{task_id}/status", json={"status": "done"})
    assert resp.status_code == 422
    assert "status" in resp.get_json()["errors"]


def test_valid_transition_in_progress_to_done(client):
    task_id = post_task(client).get_json()["id"]
    client.patch(f"/tasks/{task_id}/status", json={"status": "in_progress"})
    resp = client.patch(f"/tasks/{task_id}/status", json={"status": "done"})
    assert resp.status_code == 200


def test_valid_transition_done_to_in_progress(client):
    task_id = post_task(client).get_json()["id"]
    client.patch(f"/tasks/{task_id}/status", json={"status": "in_progress"})
    client.patch(f"/tasks/{task_id}/status", json={"status": "done"})
    resp = client.patch(f"/tasks/{task_id}/status", json={"status": "in_progress"})
    assert resp.status_code == 200


def test_invalid_status_value_returns_422(client):
    task_id = post_task(client).get_json()["id"]
    resp = client.patch(f"/tasks/{task_id}/status", json={"status": "flying"})
    assert resp.status_code == 422


# --- update and delete ---

def test_update_task_title(client):
    task_id = post_task(client).get_json()["id"]
    resp = client.put(f"/tasks/{task_id}", json={"title": "Updated", "priority": "high"})
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "Updated"


def test_delete_task(client):
    task_id = post_task(client).get_json()["id"]
    resp = client.delete(f"/tasks/{task_id}")
    assert resp.status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404
