"""
Pytest Configuration and Fixtures
Owner: Engineering Team

Provides shared test configuration, fixtures, and utilities.
Runs BEFORE any test session to set up environment and provide shared fixtures.
"""

import os
from typing import Generator

import pytest

# ── SET ENVIRONMENT VARIABLES BEFORE IMPORTING APP (CRITICAL!)
# This must happen first, before app initialization
os.environ.setdefault("PYTHONPATH", ".")
os.environ.setdefault("USE_MOCK_SERVICES", "true")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

# ── NOW import app after environment is configured
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def test_app():
    """
    Provide FastAPI application instance for the entire test session.

    Usage:
        def test_something(test_app):
            assert test_app is not None
    """
    return app


@pytest.fixture
def client() -> Generator:
    """
    Provide FastAPI TestClient for making HTTP requests to endpoints.

    This fixture is function-scoped, meaning a new client is created for each test.
    Automatically handles context manager (startup/shutdown).

    Usage:
        def test_health(client):
            response = client.get("/api/v1/health")
            assert response.status_code == 200
    """
    with TestClient(app) as test_client:
        yield test_client
