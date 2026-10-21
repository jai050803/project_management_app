from datetime import date, datetime, timezone

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    tasks = db.relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="todo")
    priority = db.Column(db.String(20), nullable=False, default="medium")
    due_date = db.Column(db.Date, nullable=True)

    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    project = db.relationship("Project", back_populates="tasks")


VALID_STATUSES = ("todo", "in_progress", "done")
VALID_PRIORITIES = ("low", "medium", "high")


def parse_due_date(raw_due_date):
    if not raw_due_date:
        return None
    return date.fromisoformat(raw_due_date)
