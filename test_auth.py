import pytest
from fastapi.testclient import TestClient

from app import crud, schemas
from app.database import SessionLocal
from app.main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def db():
    """Provides a fresh DB session for the test module."""
    db = SessionLocal()
    # Ensure a clean state: drop and recreate tables
    from app.database import Base, engine

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield db
    db.close()


def test_register_and_login(db):
    # Register a new user
    register_payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "Password123!",
        "role": "citoyen",
        "reset_question": "What is your favorite color?",
        "reset_answer": "Blue",
    }
    response = client.post("/api/auth/register", json=register_payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == register_payload["email"]
    assert data["name"] == register_payload["name"]

    # Login with the same credentials
    login_payload = {
        "email": register_payload["email"],
        "password": register_payload["password"],
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200, response.text
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    access_token = token_data["access_token"]

    # Use the token to get current user info
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200, response.text
    me_data = response.json()
    assert me_data["email"] == register_payload["email"]
    assert me_data["name"] == register_payload["name"]
