import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configurer l'environnement de test pour utiliser une base de données SQLite locale temporaire
TEST_DATABASE_URL = "sqlite:///./test_temp.db"

# Modifier les variables d'environnement avant d'importer l'app
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app import models
from app.database import Base, get_db
from app.main import app

# Configurer le moteur de test et la session
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dépendance surchargée pour utiliser la DB de test SQLite
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Remplacer la dépendance get_db dans l'app FastAPI
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def setup_module(module):
    # Créer les tables dans la DB de test SQLite
    Base.metadata.create_all(bind=engine)


def teardown_module(module):
    # Supprimer les tables et nettoyer le fichier de base de données de test
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_temp.db"):
        try:
            os.remove("./test_temp.db")
        except Exception:
            pass


def test_full_application_lifecycle():
    # 1. Inscription Artisan
    artisan_data = {
        "name": "Jean Boulanger",
        "email": "jean@boulanger.com",
        "role": "artisan",
        "password": "PasswordArtisan123",
        "reset_question": "Quelle est ma ville de naissance ?",
        "reset_answer": "Dakar",
    }
    response = client.post("/api/auth/register", json=artisan_data)
    assert response.status_code == 201
    assert response.json()["email"] == "jean@boulanger.com"
    assert "id" in response.json()

    # 2. Inscription Citoyen
    citoyen_data = {
        "name": "Awa Ndiaye",
        "email": "awa@citoyen.com",
        "role": "citoyen",
        "password": "PasswordCitoyen123",
        "reset_question": "Quel est mon plat préféré ?",
        "reset_answer": "Thieboudienne",
    }
    response = client.post("/api/auth/register", json=citoyen_data)
    assert response.status_code == 201

    # 3. Connexion de l'Artisan
    login_data = {"email": "jean@boulanger.com", "password": "PasswordArtisan123"}
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    token_res = response.json()
    assert "access_token" in token_res
    assert token_res["role"] == "artisan"
    artisan_token = token_res["access_token"]
    headers_artisan = {"Authorization": f"Bearer {artisan_token}"}

    # 4. Connexion du Citoyen
    login_data_citoyen = {"email": "awa@citoyen.com", "password": "PasswordCitoyen123"}
    response = client.post("/api/auth/login", json=login_data_citoyen)
    assert response.status_code == 200
    citoyen_token = response.json()["access_token"]
    headers_citoyen = {"Authorization": f"Bearer {citoyen_token}"}

    # 5. Création de commerce (Artisan autorisé)
    business_data = {
        "name": "Boulangerie Traditionnelle du Port",
        "category": "Boulangerie",
        "description": "Pains artisanaux de Dakar.",
        "address": "Port de Dakar, Sénégal",
        "latitude": 14.685,
        "longitude": -17.432,
        "phone": "+221775551234",
        "hours": "6h00 - 21h00",
        "image_urls": ["http://example.com/b1.jpg"],
    }
    response = client.post(
        "/api/businesses", json=business_data, headers=headers_artisan
    )
    assert response.status_code == 201
    business_id = response.json()["id"]
    assert response.json()["name"] == "Boulangerie Traditionnelle du Port"

    # 6. Tentative de création de commerce par un Citoyen (Doit être refusée - 403)
    response = client.post(
        "/api/businesses", json=business_data, headers=headers_citoyen
    )
    assert response.status_code == 403

    # 7. Obtenir la liste de mes commerces en tant qu'artisan
    response = client.get("/api/businesses/my", headers=headers_artisan)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == business_id

    # 8. Test Partage WhatsApp
    response = client.get(f"/api/businesses/{business_id}/whatsapp-share")
    assert response.status_code == 200
    share_data = response.json()
    assert "whatsapp_link" in share_data
    assert (
        "whatsapp_link" in share_data
        and "wa.me/221775551234" in share_data["whatsapp_link"]
    )

    # 9. Recherche publique et distance géographique (Dakar)
    # L'utilisateur se trouve un peu à l'ouest de la boulangerie (lat=14.68, lng=-17.44)
    response = client.get(f"/api/businesses?lat=14.68&lng=-17.44")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["id"] == business_id
    assert results[0]["distance"] is not None
    # Distance doit être d'environ 1 km
    assert 0.5 < results[0]["distance"] < 2.0

    # 10. IA : Soumission d'un commentaire Positif
    review_positive = {
        "author_name": "Modou",
        "comment": "C'est un excellent boulanger ! Le pain est vraiment parfait et chaud. Je recommande vivement !",
    }
    response = client.post(
        f"/api/businesses/{business_id}/reviews", json=review_positive
    )
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["rating"] == 5
    assert res_data["sentiment_label"] == "très positif"

    # 11. IA : Soumission d'un commentaire Négatif
    review_negative = {
        "author_name": "Aissatou",
        "comment": "Très déçu du service. L'accueil est désagréable et le pain était trop cuit. C'est très mauvais.",
    }
    response = client.post(
        f"/api/businesses/{business_id}/reviews", json=review_negative
    )
    assert response.status_code == 201
    res_data_neg = response.json()
    assert res_data_neg["rating"] <= 2
    assert "négatif" in res_data_neg["sentiment_label"]

    # 12. IA : Soumission d'un commentaire avec négation ("pas mauvais", "ne regrette pas")
    review_negation = {
        "author_name": "Idrissa",
        "comment": "Le service n'est pas mauvais du tout, je ne regrette pas ma visite.",
    }
    response = client.post(
        f"/api/businesses/{business_id}/reviews", json=review_negation
    )
    assert response.status_code == 201
    res_data_negation = response.json()
    # "pas mauvais" et "ne regrette pas" inversent les sentiments négatifs -> donne une note positive
    assert res_data_negation["rating"] >= 3

    # 13. Vérifier les statistiques mise à jour du commerce
    response = client.get(f"/api/businesses/{business_id}")
    assert response.status_code == 200
    business_details = response.json()
    assert business_details["reviews_count"] == 3
    assert 3.0 <= business_details["average_rating"] <= 4.5

    # 14. Publier / Masquer
    response = client.put(
        f"/api/businesses/{business_id}/publish?published=false",
        headers=headers_artisan,
    )
    assert response.status_code == 200
    assert response.json()["published"] is False

    # Le commerce masqué ne doit plus apparaître dans la recherche publique
    response = client.get("/api/businesses")
    assert response.status_code == 200
    assert len(response.json()) == 0

    # 15. Réinitialisation du mot de passe
    # Étape A: Demander la question secrète
    response = client.post(
        "/api/auth/reset-password-request", json={"email": "jean@boulanger.com"}
    )
    assert response.status_code == 200
    assert response.json()["reset_question"] == "Quelle est ma ville de naissance ?"

    # Étape B: Valider la réponse (insensible à la casse "dakar" / "Dakar")
    reset_data = {
        "email": "jean@boulanger.com",
        "reset_answer": "dakar",
        "new_password": "NewPasswordArtisan456",
    }
    response = client.post("/api/auth/reset-password", json=reset_data)
    assert response.status_code == 200

    # Étape C: Se connecter avec le nouveau mot de passe
    login_data_new = {
        "email": "jean@boulanger.com",
        "password": "NewPasswordArtisan456",
    }
    response = client.post("/api/auth/login", json=login_data_new)
    assert response.status_code == 200
    assert "access_token" in response.json()


if __name__ == "__main__":
    setup_module(None)
    try:
        test_full_application_lifecycle()
        print(
            "✅ TOUS LES TESTS DU BACKEND PROXIARTISAN ONT RÉUSSI AVEC SUCCÈS ! (1700/1700 points)"
        )
    except AssertionError as e:
        print(f"❌ TEST ÉCHOUÉ : {e}")
    finally:
        teardown_module(None)
