import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app

client = TestClient(app)

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------
@pytest.fixture(scope="module")
def db():
    # Re‑crée les tables pour un état propre
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()

# ----------------------------------------------------------------------
# Helpers – Auth
# ----------------------------------------------------------------------
def register_user(payload):
    return client.post("/api/auth/register", json=payload)

def login_user(payload):
    return client.post("/api/auth/login", json=payload)

def auth_header(token):
    return {"Authorization": f"Bearer {token}"}

# ----------------------------------------------------------------------
# Test complet du flux Review
# ----------------------------------------------------------------------
def test_review_flow(db):
    # 1️⃣ Crée un artisan et récupère le token
    reg_payload = {
        "name": "Artisan Review",
        "email": "reviewer@test.com",
        "password": "StrongPass!23",
        "role": "artisan",
        "reset_question": "Q?",
        "reset_answer": "A",
    }
    assert register_user(reg_payload).status_code == 201

    login_payload = {"email": reg_payload["email"], "password": reg_payload["password"]}
    token = login_user(login_payload).json()["access_token"]
    headers = auth_header(token)

    # 2️⃣ Crée un commerce (déjà testé dans `test_business.py`)
    business_payload = {
        "name": "Boulangerie Review",
        "category": "Boulangerie",
        "description": "Pain artisanal",
        "address": "1 rue Review, 75000 Paris",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "phone": "+33 1 23 45 67 89",
        "hours": "08:00-19:00",
        "image_urls": None,
    }
    resp = client.post("/api/businesses", json=business_payload, headers=headers)
    assert resp.status_code == 201
    business_id = resp.json()["id"]

    # 3️⃣ Crée un avis – le texte est analysé par l'IA
    review_payload = {
        "author_name": "Alice",
        "comment": "Service excellent, très sympathique !"
    }
    resp = client.post(f"/api/businesses/{business_id}/reviews", json=review_payload, headers=headers)
    assert resp.status_code == 201
    review = resp.json()
    # Le rating doit être entre 1 et 5 (IA donne la note)
    assert 1 <= review["rating"] <= 5
    assert isinstance(review["sentiment_score"], float)

    # 4️⃣ Récupère la liste des avis du commerce
    resp = client.get(f"/api/businesses/{business_id}/reviews", headers=headers)
    assert resp.status_code == 200
    reviews = resp.json()
    assert isinstance(reviews, list)
    # Notre avis doit être présent
    assert any(r["id"] == review["id"] for r in reviews)
