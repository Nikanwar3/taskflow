# TaskFlow

A minimal task management system built with Python/Flask, React, and SQLite.

## Stack

- **Backend**: Python 3.11, Flask 3.0, SQLAlchemy, Marshmallow, pytest
- **Frontend**: React 18, Vite, Axios
- **Database**: SQLite (file-based, zero setup)

## Running locally

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python run.py
```

API available at `http://localhost:5000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App available at `http://localhost:3000`.

### Tests

```bash
cd backend
pytest tests/ -v
```

---

## Key technical decisions

### Status transitions enforced at the model layer

Tasks follow a defined lifecycle: `todo → in_progress → done`. Skipping directly from `todo` to `done` is disallowed. Transitions can go backwards (`done → in_progress`, `in_progress → todo`) to support reopening tasks.

This rule lives in `STATUS_TRANSITIONS` in `models/task.py` and is enforced by `Task.can_transition_to()`. The dedicated `PATCH /tasks/:id/status` endpoint applies this check before any write.

**Why this approach**: centralising the rule in the model means any future route or service layer automatically benefits from the constraint — it cannot be accidentally bypassed.

### Marshmallow schemas as the validation boundary

All incoming data is validated through marshmallow schemas before reaching the database. Invalid requests return HTTP 422 with field-level error messages in a consistent `{"errors": {field: [messages]}}` shape.

**Why**: schemas give a single place to tighten or relax validation rules. Adding a new field requires updating the schema first — the model and route follow naturally.

### SQLite for simplicity

SQLite eliminates the need for a running database server during development. Swapping to PostgreSQL requires only changing `SQLALCHEMY_DATABASE_URI` — SQLAlchemy abstracts the rest.

### Vite proxy

The Vite dev server proxies `/tasks` and `/projects` to the Flask backend so the frontend never hard-codes the backend URL.

---

## Tradeoffs and known weaknesses

- **No authentication** — All data is public. In production, requests would need a user identity layer (JWT or session).
- **SQLite concurrency** — SQLite does not handle concurrent writes well. A production deployment would swap to PostgreSQL.
- **No pagination** — `GET /tasks/` returns all tasks. This breaks at scale. Adding cursor-based pagination is a one-route change isolated to `routes/tasks.py`.
- **Frontend has no edit form** — Tasks can be created and status-transitioned but not fully edited through the UI. The `PUT /tasks/:id` API supports full edits.
- **Deleting a project does not delete its tasks** — Tasks become project-less. This is a deliberate choice to avoid accidental data loss; a cascade-delete option could be added with a query parameters.

## Extension approach

To add a new feature (e.g. task tags):
1. Add `Tag` model and `task_tags` association table in `models/`
2. Add `TagSchema` in `schemas/`
3. Add `/tags` blueprint in `routes/`
4. Write tests covering invalid inputs and the happy path
5. Update the React API client and add a tag selector to `TaskForm`

The layered structure (models → schemas → routes) means each step is independent and testable in isolation..
