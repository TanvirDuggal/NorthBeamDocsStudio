"""Swagger UI routes."""

from pathlib import Path

from flask import Blueprint, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint


SWAGGER_URL = "/swagger"
OPENAPI_FILENAME = "openapi.yaml"
OPENAPI_DIRECTORY = Path(__file__).resolve().parents[3] / "docs"

swagger_bp = get_swaggerui_blueprint(
    SWAGGER_URL,
    f"{SWAGGER_URL}/{OPENAPI_FILENAME}",
    config={"app_name": "NorthBeam Docs Studio API"},
)

openapi_bp = Blueprint("openapi", __name__)


@openapi_bp.get(f"{SWAGGER_URL}/{OPENAPI_FILENAME}")
def openapi_spec():
    return send_from_directory(OPENAPI_DIRECTORY, OPENAPI_FILENAME)


