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


def test_validation_role_invalid(db):
    """Test qu'un rôle invalide est rejeté"""
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "Password123",
        "role": "admin",  # Rôle invalide
        "reset_question": "Q?",
        "reset_answer": "A",
    }
    response = register_user(payload)
    assert response.status_code == 422
    assert "role" in str(response.json())


def test_validation_role_valid(db):
    """Test que les rôles valides sont acceptés"""
    for role in ["artisan", "citoyen"]:
        payload = {
            "name": f"Test {role}",
            "email": f"test{role}@example.com",
            "password": "Password123",
            "role": role,
            "reset_question": "Q?",
            "reset_answer": "A",
        }
        response = register_user(payload)
        assert response.status_code == 201


def test_validation_password_complexity(db):
    """Test la validation de la complexité du mot de passe"""
    # Mot de passe trop court
    payload = {
        "name": "Test User",
        "email": "test1@example.com",
        "password": "Pass1",  # Trop court
        "role": "citoyen",
        "reset_question": "Q?",
        "reset_answer": "A",
    }
    response = register_user(payload)
    assert response.status_code == 422

    # Pas de majuscule
    payload["email"] = "test2@example.com"
    payload["password"] = "password123"
    response = register_user(payload)
    assert response.status_code == 422

    # Pas de minuscule
    payload["email"] = "test3@example.com"
    payload["password"] = "PASSWORD123"
    response = register_user(payload)
    assert response.status_code == 422

    # Pas de chiffre
    payload["email"] = "test4@example.com"
    payload["password"] = "PasswordABC"
    response = register_user(payload)
    assert response.status_code == 422

    # Mot de passe valide
    payload["email"] = "test5@example.com"
    payload["password"] = "Password123"
    response = register_user(payload)
    assert response.status_code == 201


def test_validation_gps_coordinates(db):
    """Test la validation des coordonnées GPS"""
    # S'inscrire comme artisan
    reg_payload = {
        "name": "Artisan Test",
        "email": "artisan@example.com",
        "password": "Password123",
        "role": "artisan",
        "reset_question": "Q?",
        "reset_answer": "A",
    }
    resp = register_user(reg_payload)
    assert resp.status_code == 201

    # Se connecter
    login_payload = {"email": reg_payload["email"], "password": reg_payload["password"]}
    resp = login_user(login_payload)
    token = resp.json()["access_token"]
    headers = auth_header(token)

    # Latitude invalide (> 90)
    business_payload = {
        "name": "Boulangerie Test",
        "category": "Boulangerie",
        "description": "Pain artisanal",
        "address": "1 rue Test",
        "latitude": 95.0,  # Invalide
        "longitude": 2.3522,
        "phone": "+33 1 23 45 67 89",
    }
    resp = client.post("/api/businesses", json=business_payload, headers=headers)
    assert resp.status_code == 422

    # Latitude invalide (< -90)
    business_payload["latitude"] = -95.0
    resp = client.post("/api/businesses", json=business_payload, headers=headers)
    assert resp.status_code == 422

    # Longitude invalide (> 180)
    business_payload["latitude"] = 48.8566
    business_payload["longitude"] = 185.0  # Invalide
    resp = client.post("/api/businesses", json=business_payload, headers=headers)
    assert resp.status_code == 422

    # Longitude invalide (< -180)
    business_payload["longitude"] = -185.0
    resp = client.post("/api/businesses", json=business_payload, headers=headers)
    assert resp.status_code == 422

    # Coordonnées valides
    business_payload["latitude"] = 48.8566
    business_payload["longitude"] = 2.3522
    resp = client.post("/api/businesses", json=business_payload, headers=headers)
    assert resp.status_code == 201


def test_validation_phone_format(db):
    """Test la validation du format de téléphone"""
    # S'inscrire comme artisan
    reg_payload = {
        "name": "Artisan Test",
        "email": "artisan2@example.com",
        "password": "Password123",
        "role": "artisan",
        "reset_question": "Q?",
        "reset_answer": "A",
    }
    resp = register_user(reg_payload)
    assert resp.status_code == 201

    # Se connecter
    login_payload = {"email": reg_payload["email"], "password": reg_payload["password"]}
    resp = login_user(login_payload)
    token = resp.json()["access_token"]
    headers = auth_header(token)

    # Téléphone invalide (trop court)
    business_payload = {
        "name": "Boulangerie Test",
        "category": "Boulangerie",
        "description": "Pain artisanal",
        "address": "1 rue Test",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "phone": "123",  # Invalide
    }
    resp = client.post("/api/businesses", json=business_payload, headers=headers)
    assert resp.status_code == 422

    # Téléphone valide (format international)
    business_payload["phone"] = "+221771234567"
    resp = client.post("/api/businesses", json=business_payload, headers=headers)
    assert resp.status_code == 201


def test_validation_image_urls(db):
    """Test la validation des URLs d'images"""
    # S'inscrire comme artisan
    reg_payload = {
        "name": "Artisan Test",
        "email": "artisan3@example.com",
        "password": "Password123",
        "role": "artisan",
        "reset_question": "Q?",
        "reset_answer": "A",
    }
    resp = register_user(reg_payload)
    assert resp.status_code == 201

    # Se connecter
    login_payload = {"email": reg_payload["email"], "password": reg_payload["password"]}
    resp = login_user(login_payload)
    token = resp.json()["access_token"]
    headers = auth_header(token)

    # Plus de 3 images
    business_payload = {
        "name": "Boulangerie Test",
        "category": "Boulangerie",
        "description": "Pain artisanal",
        "address": "1 rue Test",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "phone": "+33 1 23 45 67 89",
        "image_urls": ["http://a.com/1.jpg", "http://a.com/2.jpg", "http://a.com/3.jpg", "http://a.com/4.jpg"],
    }
    resp = client.post("/api/businesses", json=business_payload, headers=headers)
    assert resp.status_code == 422

    # URL invalide
    business_payload["image_urls"] = ["not-a-url"]
    resp = client.post("/api/businesses", json=business_payload, headers=headers)
    assert resp.status_code == 422

    # URLs valides (3 max)
    business_payload["image_urls"] = ["http://example.com/1.jpg", "https://example.com/2.jpg", "http://example.com/3.jpg"]
    resp = client.post("/api/businesses", json=business_payload, headers=headers)
    assert resp.status_code == 201


def test_validation_category(db):
    """Test la validation des catégories"""
    # S'inscrire comme artisan
    reg_payload = {
        "name": "Artisan Test",
        "email": "artisan4@example.com",
        "password": "Password123",
        "role": "artisan",
        "reset_question": "Q?",
        "reset_answer": "A",
    }
    resp = register_user(reg_payload)
    assert resp.status_code == 201

    # Se connecter
    login_payload = {"email": reg_payload["email"], "password": reg_payload["password"]}
    resp = login_user(login_payload)
    token = resp.json()["access_token"]
    headers = auth_header(token)

    # Catégorie invalide
    business_payload = {
        "name": "Boulangerie Test",
        "category": "CatégorieInvalide",  # Invalide
        "description": "Pain artisanal",
        "address": "1 rue Test",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "phone": "+33 1 23 45 67 89",
    }
    resp = client.post("/api/businesses", json=business_payload, headers=headers)
    assert resp.status_code == 422

    # Catégorie valide
    business_payload["category"] = "Boulangerie"
    resp = client.post("/api/businesses", json=business_payload, headers=headers)
    assert resp.status_code == 201


def test_delete_business(db):
    """Test la suppression d'un commerce"""
    # S'inscrire comme artisan
    reg_payload = {
        "name": "Artisan Test",
        "email": "artisan5@example.com",
        "password": "Password123",
        "role": "artisan",
        "reset_question": "Q?",
        "reset_answer": "A",
    }
    resp = register_user(reg_payload)
    assert resp.status_code == 201

    # Se connecter
    login_payload = {"email": reg_payload["email"], "password": reg_payload["password"]}
    resp = login_user(login_payload)
    token = resp.json()["access_token"]
    headers = auth_header(token)

    # Créer un commerce
    business_payload = {
        "name": "Boulangerie Test",
        "category": "Boulangerie",
        "description": "Pain artisanal",
        "address": "1 rue Test",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "phone": "+33 1 23 45 67 89",
    }
    resp = client.post("/api/businesses", json=business_payload, headers=headers)
    assert resp.status_code == 201
    business_id = resp.json()["id"]

    # Supprimer le commerce
    resp = client.delete(f"/api/businesses/{business_id}", headers=headers)
    assert resp.status_code == 204

    # Vérifier que le commerce n'existe plus
    resp = client.get(f"/api/businesses/{business_id}")
    assert resp.status_code == 404


def test_pagination(db):
    """Test la pagination de la recherche"""
    # S'inscrire comme artisan
    reg_payload = {
        "name": "Artisan Test",
        "email": "artisan6@example.com",
        "password": "Password123",
        "role": "artisan",
        "reset_question": "Q?",
        "reset_answer": "A",
    }
    resp = register_user(reg_payload)
    assert resp.status_code == 201

    # Se connecter
    login_payload = {"email": reg_payload["email"], "password": reg_payload["password"]}
    resp = login_user(login_payload)
    token = resp.json()["access_token"]
    headers = auth_header(token)

    # Créer plusieurs commerces
    for i in range(5):
        business_payload = {
            "name": f"Boulangerie Test {i}",
            "category": "Boulangerie",
            "description": "Pain artisanal",
            "address": f"{i} rue Test",
            "latitude": 48.8566 + i * 0.01,
            "longitude": 2.3522 + i * 0.01,
            "phone": "+33 1 23 45 67 89",
        }
        resp = client.post("/api/businesses", json=business_payload, headers=headers)
        assert resp.status_code == 201

    # Tester pagination avec limit=2
    resp = client.get("/api/businesses?limit=2")
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 2

    # Tester pagination avec skip=2, limit=2
    resp = client.get("/api/businesses?skip=2&limit=2")
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 2


def test_rate_limiting(db):
    """Test le rate limiting des tentatives de connexion"""
    # Créer un utilisateur
    reg_payload = {
        "name": "Test User",
        "email": "ratelimit@example.com",
        "password": "Password123",
        "role": "citoyen",
        "reset_question": "Q?",
        "reset_answer": "A",
    }
    resp = register_user(reg_payload)
    assert resp.status_code == 201

    # Tenter 5 connexions avec mauvais mot de passe
    login_payload = {"email": "ratelimit@example.com", "password": "WrongPassword"}
    for i in range(5):
        resp = login_user(login_payload)
        assert resp.status_code == 401

    # La 6ème tentative doit être bloquée par rate limiting (HTTP 429)
    resp = login_user(login_payload)
    assert resp.status_code == 429
    assert "Trop de tentatives" in resp.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
