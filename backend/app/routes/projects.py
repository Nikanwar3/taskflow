import logging
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from ..database import db
from ..models import Project
from ..schemas import project_schema, projects_schema

logger = logging.getLogger(__name__)
projects_bp = Blueprint("projects", __name__)


@projects_bp.get("/")
def list_projects():
    projects = Project.query.order_by(Project.name).all()
    return jsonify(projects_schema.dump(projects))


@projects_bp.post("/")
def create_project():
    try:
        data = project_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    if Project.query.filter_by(name=data["name"]).first():
        return jsonify({"errors": {"name": ["A project with this name already exists."]}}), 409

    project = Project(**data)
    db.session.add(project)
    db.session.commit()
    logger.info("Project created: id=%d name=%s", project.id, project.name)
    return jsonify(project_schema.dump(project)), 201


@projects_bp.get("/<int:project_id>")
def get_project(project_id):
    project = db.get_or_404(Project, project_id)
    return jsonify(project_schema.dump(project))


@projects_bp.put("/<int:project_id>")
def update_project(project_id):
    project = db.get_or_404(Project, project_id)
    try:
        data = project_schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    if "name" in data and data["name"] != project.name:
        if Project.query.filter_by(name=data["name"]).first():
            return jsonify({"errors": {"name": ["A project with this name already exists."]}}), 409

    for key, value in data.items():
        setattr(project, key, value)

    db.session.commit()
    return jsonify(project_schema.dump(project))


@projects_bp.delete("/<int:project_id>")
def delete_project(project_id):
    project = db.get_or_404(Project, project_id)
    db.session.delete(project)
    db.session.commit()
    logger.info("Project deleted: id=%d", project_id)
    return "", 204
