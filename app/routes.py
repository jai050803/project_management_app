from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import case

from .models import (
    Project,
    Task,
    VALID_PRIORITIES,
    VALID_STATUSES,
    db,
    parse_due_date,
)

bp = Blueprint("projects", __name__)


@bp.route("/")
def index():
    return redirect(url_for("projects.project_list"))


@bp.route("/projects")
def project_list():
    projects = Project.query.order_by(Project.name.asc()).all()
    return render_template("projects/list.html", projects=projects)


@bp.route("/projects/new", methods=["GET", "POST"])
def project_create():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Project name is required.", "error")
            return render_template("projects/form.html", project=None), 400

        project = Project(name=name, description=description)
        db.session.add(project)
        db.session.commit()
        flash("Project created successfully.", "success")
        return redirect(url_for("projects.project_detail", project_id=project.id))

    return render_template("projects/form.html", project=None)


@bp.route("/projects/<int:project_id>")
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    status_filter = request.args.get("status", "all")
    sort = request.args.get("sort", "created_at")

    tasks_query = Task.query.filter_by(project_id=project.id)

    if status_filter in VALID_STATUSES:
        tasks_query = tasks_query.filter_by(status=status_filter)
    else:
        status_filter = "all"

    if sort == "priority":
        tasks_query = tasks_query.order_by(
            case(
                (Task.priority == "high", 1),
                (Task.priority == "medium", 2),
                else_=3,
            ),
            Task.due_date.asc(),
        )
    elif sort == "due_date":
        tasks_query = tasks_query.order_by(Task.due_date.asc().nullslast(), Task.created_at.asc())
    elif sort == "status":
        tasks_query = tasks_query.order_by(
            case(
                (Task.status == "todo", 1),
                (Task.status == "in_progress", 2),
                else_=3,
            ),
            Task.created_at.asc(),
        )
    else:
        sort = "created_at"
        tasks_query = tasks_query.order_by(Task.created_at.desc())

    tasks = tasks_query.all()
    return render_template(
        "projects/detail.html",
        project=project,
        tasks=tasks,
        status_filter=status_filter,
        sort=sort,
        statuses=VALID_STATUSES,
    )


@bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
def project_edit(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            flash("Project name is required.", "error")
            return render_template("projects/form.html", project=project), 400

        project.name = name
        project.description = description
        db.session.commit()
        flash("Project updated successfully.", "success")
        return redirect(url_for("projects.project_detail", project_id=project.id))

    return render_template("projects/form.html", project=project)


@bp.route("/projects/<int:project_id>/delete", methods=["POST"])
def project_delete(project_id):
    project = Project.query.get_or_404(project_id)

    db.session.delete(project)
    db.session.commit()
    flash("Project deleted successfully.", "success")
    return redirect(url_for("projects.project_list"))


@bp.route("/tasks")
def task_list():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template("tasks/list.html", tasks=tasks)


@bp.route("/tasks/new", methods=["GET", "POST"])
def task_create():
    projects = Project.query.order_by(Project.name.asc()).all()
    project_id = request.args.get("project_id", type=int)

    if request.method == "POST":
        form_data = request.form.to_dict()
        project_id = request.form.get("project_id", type=int)
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "todo").strip()
        priority = request.form.get("priority", "medium").strip()
        due_date_raw = request.form.get("due_date", "").strip()

        errors = validate_task_form(title, status, priority, project_id, due_date_raw)
        if errors:
            for error in errors:
                flash(error, "error")
            return (
                render_template(
                    "tasks/form.html",
                    task=None,
                    projects=projects,
                    form_data=form_data,
                    statuses=VALID_STATUSES,
                    priorities=VALID_PRIORITIES,
                ),
                400,
            )

        task = Task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=parse_due_date(due_date_raw),
            project_id=project_id,
        )
        db.session.add(task)
        db.session.commit()
        flash("Task created successfully.", "success")
        return redirect(url_for("projects.task_detail", task_id=task.id))

    form_data = {"project_id": project_id} if project_id else {}
    return render_template(
        "tasks/form.html",
        task=None,
        projects=projects,
        form_data=form_data,
        statuses=VALID_STATUSES,
        priorities=VALID_PRIORITIES,
    )


@bp.route("/tasks/<int:task_id>")
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template("tasks/detail.html", task=task)


@bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def task_edit(task_id):
    task = Task.query.get_or_404(task_id)
    projects = Project.query.order_by(Project.name.asc()).all()

    if request.method == "POST":
        form_data = request.form.to_dict()
        project_id = request.form.get("project_id", type=int)
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "todo").strip()
        priority = request.form.get("priority", "medium").strip()
        due_date_raw = request.form.get("due_date", "").strip()

        errors = validate_task_form(title, status, priority, project_id, due_date_raw)
        if errors:
            for error in errors:
                flash(error, "error")
            return (
                render_template(
                    "tasks/form.html",
                    task=task,
                    projects=projects,
                    form_data=form_data,
                    statuses=VALID_STATUSES,
                    priorities=VALID_PRIORITIES,
                ),
                400,
            )

        task.title = title
        task.description = description
        task.status = status
        task.priority = priority
        task.project_id = project_id
        task.due_date = parse_due_date(due_date_raw)

        db.session.commit()
        flash("Task updated successfully.", "success")
        return redirect(url_for("projects.task_detail", task_id=task.id))

    return render_template(
        "tasks/form.html",
        task=task,
        projects=projects,
        form_data={},
        statuses=VALID_STATUSES,
        priorities=VALID_PRIORITIES,
    )


@bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
def task_delete(task_id):
    task = Task.query.get_or_404(task_id)
    project_id = task.project_id

    db.session.delete(task)
    db.session.commit()
    flash("Task deleted successfully.", "success")
    return redirect(url_for("projects.project_detail", project_id=project_id))


@bp.app_errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@bp.app_errorhandler(400)
def bad_request(error):
    return render_template("400.html"), 400


def validate_task_form(title, status, priority, project_id, due_date_raw):
    errors = []

    if not title:
        errors.append("Task title is required.")

    if status not in VALID_STATUSES:
        errors.append("Task status is invalid.")

    if priority not in VALID_PRIORITIES:
        errors.append("Task priority is invalid.")

    project = db.session.get(Project, project_id) if project_id else None
    if not project:
        errors.append("A valid project is required.")

    if due_date_raw:
        try:
            due_date = parse_due_date(due_date_raw)
            if due_date < date(1900, 1, 1):
                errors.append("Due date must be after 1900-01-01.")
        except ValueError:
            errors.append("Due date must be in YYYY-MM-DD format.")

    return errors
