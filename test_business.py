import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def db():
    # Recreate tables for a clean state
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


def register_user(payload):
    return client.post("/api/auth/register", json=payload)


def login_user(payload):
    return client.post("/api/auth/login", json=payload)


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_business_flow(db):
    # Register an artisan
    reg_payload = {
        "name": "Artisan Test",
        "email": "artisan@test.com",
        "password": "TestPass123!",
        "role": "artisan",
        "reset_question": "Q?",
        "reset_answer": "A",
    }
    resp = register_user(reg_payload)
    assert resp.status_code == 201

    # Login to obtain token
    login_payload = {"email": reg_payload["email"], "password": reg_payload["password"]}
    resp = login_user(login_payload)
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    headers = auth_header(token)

    # Create a business
    business_payload = {
        "name": "Boulangerie Test",
        "category": "Boulangerie",
        "description": "Pain artisanal",
        "address": "1 rue Test, 75000 Paris",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "phone": "+33 1 23 45 67 89",
        "hours": "08:00-19:00",
        "image_urls": None,
    }
    resp = client.post("/api/businesses", json=business_payload, headers=headers)
    assert resp.status_code == 201
    business = resp.json()
    business_id = business["id"]

    # Get my businesses
    resp = client.get("/api/businesses/my", headers=headers)
    assert resp.status_code == 200
    my_list = resp.json()
    assert any(b["id"] == business_id for b in my_list)

    # Update business name
    update_payload = {"name": "Boulangerie Renommée"}
    resp = client.put(
        f"/api/businesses/{business_id}", json=update_payload, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Boulangerie Renommée"

    # Toggle publish off
    resp = client.put(
        f"/api/businesses/{business_id}/publish?published=false", headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["published"] is False

    # Search should not return unpublished business
    resp = client.get("/api/businesses?query=Boulangerie")
    assert resp.status_code == 200
    results = resp.json()
    assert not any(b["id"] == business_id for b in results)

    # Publish again
    resp = client.put(
        f"/api/businesses/{business_id}/publish?published=true", headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["published"] is True

    # Search should now return it
    resp = client.get("/api/businesses?query=Boulangerie")
    assert resp.status_code == 200
    results = resp.json()
    assert any(b["id"] == business_id for b in results)

    # Get WhatsApp share link
    resp = client.get(f"/api/businesses/{business_id}/whatsapp-share", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "whatsapp_link" in data and "message" in data
