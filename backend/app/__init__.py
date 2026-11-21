"""Flask application factory."""

import os

from flask import Flask

from .db import init_app as init_db_app
from .db import init_db
from .routes.health import health_bp
from .routes.swagger import openapi_bp
from .routes.swagger import swagger_bp
from .routes.articles import articles_bp


def create_app(test_config: dict | None = None) -> Flask:
    """Create the Flask application and register its blueprints."""
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "northbeam.sqlite3"),
    )
    if test_config is not None:
        app.config.update(test_config)

    init_db_app(app)
    app.register_blueprint(health_bp)
    app.register_blueprint(swagger_bp)
    app.register_blueprint(openapi_bp)
    app.register_blueprint(articles_bp)

    with app.app_context():
        init_db()

    return app
