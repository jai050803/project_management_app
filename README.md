# Project Management App

A Flask-based project/task management application for local development.

## Features

- Project CRUD (create, view, update, delete)
- Task CRUD with project association
- Task fields: title, description, status, priority, due date
- Project detail view with task filtering/sorting
- Flash messages and validation handling
- SQLite persistence via Flask-SQLAlchemy
- CLI database initialization and optional seed data
- Pytest test suite for core CRUD + validation paths

## Tech Stack

- Python 3.10+
- Flask
- Flask-SQLAlchemy
- SQLite
- Pytest

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment:

```bash
cp .env.example .env
```

## Database Initialization

Initialize tables:

```bash
flask --app run.py init-db
```

Initialize with demo data:

```bash
flask --app run.py init-db --seed
```

## Run Locally

```bash
flask --app run.py run --debug
```

Then open http://127.0.0.1:5000.

## Run Tests

```bash
pytest
```

## Notes

- The default SQLite database is stored at `instance/project_management.db`.
- Keep secrets in `.env` (already gitignored).
