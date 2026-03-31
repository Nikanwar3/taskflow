from datetime import datetime, timezone
from ..database import db

VALID_STATUSES = ("todo", "in_progress", "done")
VALID_PRIORITIES = ("low", "medium", "high")

# Allowed status transitions: key -> set of valid next states
STATUS_TRANSITIONS = {
    "todo": {"in_progress"},
    "in_progress": {"todo", "done"},
    "done": {"in_progress"},
}


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="todo")
    priority = db.Column(db.String(10), nullable=False, default="medium")
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=True)

    project = db.relationship("Project", back_populates="tasks")

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in STATUS_TRANSITIONS.get(self.status, set())
