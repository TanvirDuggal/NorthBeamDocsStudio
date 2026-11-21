"""Shared pytest fixtures for the backend."""

import sys
from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app import create_app  # noqa: E402


@pytest.fixture()
def app(tmp_path):
    database_path = tmp_path / "test.sqlite3"
    return create_app(
        {
            "TESTING": True,
            "DATABASE": str(database_path),
        }
    )


@pytest.fixture()
def client(app):
    return app.test_client()
