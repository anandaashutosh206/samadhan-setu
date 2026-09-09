import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./test_samadhan.db"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session", autouse=True)
def _cleanup_test_db():
    db_path = Path("./test_samadhan.db")
    if db_path.exists():
        db_path.unlink()
    yield
    if db_path.exists():
        db_path.unlink()


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def citizen_token(client):
    r = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Citizen",
            "email": f"citizen_{os.urandom(4).hex()}@test.com",
            "password": "Demo@1234",
            "role": "CITIZEN",
            "district": "Ranchi",
        },
    )
    assert r.status_code == 201
    return r.json()["access_token"]


@pytest.fixture()
def govt_token(client):
    r = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test Official",
            "email": f"govt_{os.urandom(4).hex()}@test.com",
            "password": "Demo@1234",
            "role": "GOVT_OFFICIAL",
            "district": "Ranchi",
        },
    )
    assert r.status_code == 201
    return r.json()["access_token"]
