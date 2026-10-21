from app.models import Project, Task, db


def test_project_crud(client, app):
    response = client.post(
        "/projects/new",
        data={"name": "Alpha", "description": "First project"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Project created successfully." in response.data
    assert b"Alpha" in response.data

    with app.app_context():
        project = Project.query.filter_by(name="Alpha").first()
        assert project is not None
        project_id = project.id

    response = client.post(
        f"/projects/{project_id}/edit",
        data={"name": "Alpha Updated", "description": "Updated"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Project updated successfully." in response.data
    assert b"Alpha Updated" in response.data

    response = client.post(f"/projects/{project_id}/delete", follow_redirects=True)
    assert response.status_code == 200
    assert b"Project deleted successfully." in response.data

    with app.app_context():
        assert db.session.get(Project, project_id) is None


def test_project_validation_requires_name(client):
    response = client.post("/projects/new", data={"name": "", "description": "No name"})
    assert response.status_code == 400
    assert b"Project name is required." in response.data


def test_task_crud_and_validation(client, app):
    with app.app_context():
        project = Project(name="Beta", description="Task project")
        db.session.add(project)
        db.session.commit()
        project_id = project.id

    response = client.post(
        "/tasks/new",
        data={
            "title": "Build API",
            "description": "Create task",
            "status": "todo",
            "priority": "high",
            "due_date": "2030-01-01",
            "project_id": str(project_id),
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Task created successfully." in response.data
    assert b"Build API" in response.data

    with app.app_context():
        task = Task.query.filter_by(title="Build API").first()
        assert task is not None
        task_id = task.id

    response = client.post(
        f"/tasks/{task_id}/edit",
        data={
            "title": "Build API v2",
            "description": "Updated task",
            "status": "in_progress",
            "priority": "medium",
            "due_date": "2030-02-01",
            "project_id": str(project_id),
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Task updated successfully." in response.data
    assert b"Build API v2" in response.data

    invalid_response = client.post(
        "/tasks/new",
        data={
            "title": "Bad task",
            "description": "Invalid",
            "status": "bad_status",
            "priority": "medium",
            "due_date": "not-a-date",
            "project_id": "9999",
        },
    )
    assert invalid_response.status_code == 400
    assert b"Task status is invalid." in invalid_response.data
    assert b"Due date must be in YYYY-MM-DD format." in invalid_response.data
    assert b"A valid project is required." in invalid_response.data

    response = client.post(f"/tasks/{task_id}/delete", follow_redirects=True)
    assert response.status_code == 200
    assert b"Task deleted successfully." in response.data

    with app.app_context():
        assert db.session.get(Task, task_id) is None


def test_project_detail_filter_by_status(client, app):
    with app.app_context():
        project = Project(name="Gamma", description="Filter project")
        db.session.add(project)
        db.session.flush()

        db.session.add_all(
            [
                Task(title="Todo task", status="todo", priority="low", project_id=project.id),
                Task(
                    title="Done task",
                    status="done",
                    priority="high",
                    project_id=project.id,
                ),
            ]
        )
        db.session.commit()
        project_id = project.id

    response = client.get(f"/projects/{project_id}?status=todo&sort=priority")
    assert response.status_code == 200
    assert b"Todo task" in response.data
    assert b"Done task" not in response.data
