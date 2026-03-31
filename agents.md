# AI Agent Guidance

## Purpose
This file defines constraints and standards for AI agents contributing to this codebase.

## Non-negotiable rules

1. **Never bypass validation** — All user input must pass through marshmallow schemas before touching the database.
2. **Respect status transitions** — The `STATUS_TRANSITIONS` map in `task.py` is the single source of truth. Do not add shortcut transitions without updating this map and the corresponding tests.
3. **No raw SQL** — Use SQLAlchemy ORM only. Raw queries bypass the model layer and break type safety.
4. **Keep domain logic in models, not routes** — Business rules (e.g. `can_transition_to`) belong on the model. Routes handle HTTP concerns only.
5. **Tests must pass before merging** — Every new endpoint or rule must have a corresponding pytest test covering the happy path and at least one invalid input case.

## Adding new features

- Add the model change → schema change → route change in that order.
- Validation errors must return HTTP 422 with `{"errors": {field: [messages]}}` format — do not invent new error shapes.
- Prefer simple, explicit code over clever abstractions.
- Do not add a field to the database without adding it to the schema.

## What to avoid

- Do not add retry logic or fallbacks that silently swallow errors.
- Do not log sensitive user data.
- Do not introduce new dependencies without a clear reason.
