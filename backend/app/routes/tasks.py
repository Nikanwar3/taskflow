import logging
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from ..database import db
from ..models import Task, Project
from ..schemas import task_schema, tasks_schema
from ..models.task import VALID_STATUSES, VALID_PRIORITIES

logger = logging.getLogger(__name__)
tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.get("/")
def list_tasks():
    query = Task.query

    status = request.args.get("status")
    if status:
        if status not in VALID_STATUSES:
            return jsonify({"errors": {"status": [f"Must be one of: {', '.join(VALID_STATUSES)}"]}}), 422
        query = query.filter_by(status=status)

    priority = request.args.get("priority")
    if priority:
        if priority not in VALID_PRIORITIES:
            return jsonify({"errors": {"priority": [f"Must be one of: {', '.join(VALID_PRIORITIES)}"]}}), 422
        query = query.filter_by(priority=priority)

    project_id = request.args.get("project_id", type=int)
    if project_id:
        query = query.filter_by(project_id=project_id)

    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify(tasks_schema.dump(tasks))


@tasks_bp.post("/")
def create_task():
    try:
        data = task_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    if data.get("project_id") and not db.session.get(Project, data["project_id"]):
        return jsonify({"errors": {"project_id": ["Project not found."]}}), 422

    task = Task(**data)
    db.session.add(task)
    db.session.commit()
    logger.info("Task created: id=%d title=%s", task.id, task.title)
    return jsonify(task_schema.dump(task)), 201


@tasks_bp.get("/<int:task_id>")
def get_task(task_id):
    task = db.get_or_404(Task, task_id)
    return jsonify(task_schema.dump(task))


@tasks_bp.put("/<int:task_id>")
def update_task(task_id):
    task = db.get_or_404(Task, task_id)
    try:
        data = task_schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    if "status" in data and data["status"] != task.status:
        if not task.can_transition_to(data["status"]):
            return jsonify({
                "errors": {
                    "status": [
                        f"Cannot transition from '{task.status}' to '{data['status']}'."
                    ]
                }
            }), 422

    if "project_id" in data and data["project_id"] is not None:
        if not db.session.get(Project, data["project_id"]):
            return jsonify({"errors": {"project_id": ["Project not found."]}}), 422

    for key, value in data.items():
        setattr(task, key, value)

    db.session.commit()
    logger.info("Task updated: id=%d", task_id)
    return jsonify(task_schema.dump(task))


@tasks_bp.patch("/<int:task_id>/status")
def update_status(task_id):
    task = db.get_or_404(Task, task_id)
    body = request.get_json() or {}
    new_status = body.get("status")

    if new_status not in VALID_STATUSES:
        return jsonify({"errors": {"status": [f"Must be one of: {', '.join(VALID_STATUSES)}"]}}), 422

    if not task.can_transition_to(new_status):
        return jsonify({
            "errors": {
                "status": [f"Cannot transition from '{task.status}' to '{new_status}'."]
            }
        }), 422

    task.status = new_status
    db.session.commit()
    logger.info("Task %d status -> %s", task_id, new_status)
    return jsonify(task_schema.dump(task))


@tasks_bp.delete("/<int:task_id>")
def delete_task(task_id):
    task = db.get_or_404(Task, task_id)
    db.session.delete(task)
    db.session.commit()
    logger.info("Task deleted: id=%d", task_id)
    return "", 204
