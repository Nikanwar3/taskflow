from flask import Flask
from flask_cors import CORS
from .database import db
from .errors import register_error_handlers
from .routes import tasks_bp, projects_bp
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


def create_app(config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///taskflow.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config:
        app.config.update(config)

    CORS(app)
    db.init_app(app)

    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(projects_bp, url_prefix="/projects")

    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    return app
