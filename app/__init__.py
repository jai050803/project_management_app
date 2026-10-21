import os

import click
from flask import Flask

from .models import Project, Task, db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    database_path = os.path.join(app.instance_path, "project_management.db")

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", f"sqlite:///{database_path}"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    from . import routes

    app.register_blueprint(routes.bp)

    @app.cli.command("init-db")
    @click.option("--seed", is_flag=True, help="Seed demo data after creating tables.")
    def init_db_command(seed):
        """Initialize database tables."""
        db.create_all()
        if seed:
            seed_demo_data()
        click.echo("Initialized the database.")

    with app.app_context():
        db.create_all()

    return app


def seed_demo_data():
    if Project.query.count() > 0:
        return

    website_project = Project(name="Website Redesign", description="Refresh landing pages.")
    api_project = Project(name="API Improvements", description="Improve API reliability.")

    db.session.add_all([website_project, api_project])
    db.session.flush()

    db.session.add_all(
        [
            Task(
                title="Audit existing UI",
                description="Review current page consistency.",
                status="todo",
                priority="medium",
                project_id=website_project.id,
            ),
            Task(
                title="Add retry logic",
                description="Handle transient API errors.",
                status="in_progress",
                priority="high",
                project_id=api_project.id,
            ),
        ]
    )

    db.session.commit()
