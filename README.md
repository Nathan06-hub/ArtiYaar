# ProxiArtisan - Backend API REST

ProxiArtisan est une API REST puissante, moderne et performante développée en **Python** avec **FastAPI**, **PostgreSQL** et **SQLAlchemy**. Elle sert de moteur principal pour l'annuaire géolocalisé des commerces et services de proximité.

Ce projet s'inscrit dans le cadre du défi hackathon *"Le numérique au service du développement local"* et implémente l'intégralité des fonctionnalités exigées, totalisant les **1700 points** du barème.

---

## 👥 Informations du Groupe
* **Nom du Groupe** : LogiCode
* **Membres & Coordonnées** :
  - Stéphane Nathanaël MARE - Développeur Backend  ([maresteph06@gmail.com](mailto:maresteph06@gmail.com))
  - Omaïmata OUEDRAOGO - Développeur Frontend ([omaiodg@gmail.com](mailto:omaiodg@gmail.com))
  - Serge Landry WAONGO - Developpeur Frontend/ Lead ([sergewaongolandry@gmail.com](mailto:sergewaongolandry@gmail.com))
  - Papus Aymerick KONATE -  ([papuskonate74@gmail.com](mailto:papuskonate74@gmail.com))
  - Cedric NINkIEMA - Desingner UI/UX ([alalande@gmail.com](mailto:alalande@gmail.com)) 
    
---

## 🏗️ Architecture Technique et Choix Technologiques

Le backend est structuré selon un patron de conception modulaire séparant les routes, la logique d'accès aux données (CRUD), la sécurité, et les services spécialisés (géolocalisation et intelligence artificielle).

* **Framework API** : **FastAPI**
  - Validation automatique des requêtes et réponses via **Pydantic**.
  - Génération automatique et interactive de la documentation Swagger (`/docs`) et ReDoc (`/redoc`).
  - Performances optimales grâce au support de l'asynchronisme.
* **Base de données** : **PostgreSQL** (système de gestion de bases de données relationnelles robuste et éprouvé).
* **ORM (Object-Relational Mapping)** : **SQLAlchemy**
  - Abstraction complète des requêtes SQL complexes.
  - Initialisation automatique de la structure des tables au démarrage de l'application.
* **Sécurité & Authentification** :
  - Hachage cryptographique fort des mots de passe (bcrypt via **passlib**).
  - Authentification sans état (stateless) à l'aide de jetons **JWT (JSON Web Tokens)**.

---

## 📂 Structure du Projet

```text
proxiartisan-backend/
│
├── requirements.txt      # Dépendances du projet Python
├── .env                  # Variables d'environnement (Base de données, clés secrètes)
├── README.md             # Ce document de documentation technique (200 pts)
│
└── app/
    ├── __init__.py
    ├── main.py           # Point d'entrée FastAPI, configuration CORS et de la base de données
    ├── config.py         # Module de configuration chargeant les données depuis le .env
    ├── database.py       # Configuration SQLAlchemy (Engine, SessionLocal, Dépendance get_db)
    ├── models.py         # Modèles de base de données relationnelle SQLAlchemy
    ├── schemas.py        # Schémas de validation Pydantic (Request/Response models)
    ├── crud.py           # Opérations CRUD d'accès et d'écriture en base de données
    ├── auth.py           # Utilitaires de cryptographie et dépendances de sécurité JWT
    │
    ├── routers/
    │   ├── __init__.py
    │   ├── auth.py       # API d'inscription, de connexion et de réinitialisation de mot de passe
    │   ├── business.py   # API d'enregistrement, de publication et de recherche de commerces
    │   └── review.py     # API d'avis et d'analyse sentimentale (IA)
    │
    └── services/
        ├── __init__.py
        ├── ai.py         # Moteur IA autonome d'analyse de sentiment lexical en français
        └── distance.py   # Calculateur de distance géographique (Haversine)
```

---

## 🗄️ Schéma de la Base de Données Relative

L'API s'appuie sur trois entités relationnelles configurées dans `app/models.py` :

```mermaid
erDiagram
    USERS {
        int id PK
        string name
        string email
        string hashed_password
        string role
        string reset_question
        string reset_answer
    }
    BUSINESSES {
        int id PK
        int owner_id FK
        string name
        string category
        string description
        string address
        float latitude
        float longitude
        string phone
        string hours
        boolean published
        string image_urls
    }
    REVIEWS {
        int id PK
        int business_id FK
        string author_name
        string comment
        int rating
        float sentiment_score
        datetime created_at
    }

    USERS ||--o{ BUSINESSES : possede
    BUSINESSES ||--o{ REVIEWS : recoit
```

---

## 🚀 Guide de Démarrage Rapide

### 1. Prérequis
- Python 3.9+ installé
- PostgreSQL installé et configuré (avec une base de données créée, par exemple `proxiartisan`)

### 2. Installation des Dépendances
Dans le répertoire racine du projet, lancez :
```bash
pip install -r requirements.txt
```

### 3. Configuration de l'environnement (`.env`)
Modifiez le fichier `.env` à la racine pour renseigner vos identifiants PostgreSQL :
```env
DATABASE_URL=postgresql://mon_utilisateur:mon_mot_de_passe@localhost:5432/proxiartisan
JWT_SECRET_KEY=une_cle_secrete_tres_longue_et_aleatoire
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

### 4. Lancement de l'Application
Démarrez le serveur ASGI Uvicorn en mode rechargement automatique :
```bash
uvicorn app.main:app --reload
```
Le serveur démarre sur [http://127.0.0.1:8000](http://127.0.0.1:8000).
- La documentation Swagger interactive est disponible sur : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- La documentation ReDoc est disponible sur : [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🛠️ Description des Endpoints et Exemples d'Utilisation

### 1. Gestion de Comptes (200 pts)

#### 📝 Inscription (`POST /api/auth/register`)
Crée un compte utilisateur. Deux rôles sont acceptés : `artisan` (peut créer des fiches) et `citoyen` (peut écrire des avis).
* **Requête** :
```json
{
  "name": "Jean Dupont",
  "email": "jean.dupont@example.com",
  "role": "artisan",
  "password": "MonMotDePasse123",
  "reset_question": "Quel est le nom de mon premier animal de compagnie ?",
  "reset_answer": "Rex"
}
```
* **Réponse (201 Created)** :
```json
{
  "name": "Jean Dupont",
  "email": "jean.dupont@example.com",
  "role": "artisan",
  "id": 1
}
```

#### 🔑 Connexion (`POST /api/auth/login`)
Retourne un jeton JWT d'authentification valide.
* **Requête** :
```json
{
  "email": "jean.dupont@example.com",
  "password": "MonMotDePasse123"
}
```
* **Réponse (200 OK)** :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "role": "artisan",
  "name": "Jean Dupont"
}
```

#### 🔄 Réinitialisation de Mot de Passe (`POST /api/auth/reset-password-request` & `POST /api/auth/reset-password`)
Permet de sécuriser la perte de compte en vérifiant d'abord la question de sécurité, puis en soumettant le nouveau mot de passe.
1. **Étape 1 : Demande de question** (`POST /api/auth/reset-password-request`)
   - Requête : `{"email": "jean.dupont@example.com"}`
   - Réponse : `{"email": "jean.dupont@example.com", "reset_question": "Quel est le nom de mon premier animal de compagnie ?"}`
2. **Étape 2 : Validation de la réponse et réinitialisation** (`POST /api/auth/reset-password`)
   - Requête :
     ```json
     {
       "email": "jean.dupont@example.com",
       "reset_answer": "rex",
       "new_password": "NouveauMotDePasse456"
     }
     ```
   - Réponse : `{"message": "Le mot de passe a été réinitialisé avec succès."}`

---

### 2. Gestion de Commerces (400 pts)

#### 🔨 Enregistrement d'un Commerce (`POST /api/businesses`)
Permet à un artisan connecté d'ajouter un commerce (un artisan peut posséder plusieurs commerces).
* **En-tête requis** : `Authorization: Bearer <JWT_TOKEN>`
* **Requête** :
```json
{
  "name": "Boulangerie Le Bon Pain",
  "category": "Boulangerie",
  "description": "Pain artisanal cuit au feu de bois et viennoiseries chaudes.",
  "address": "12 Rue de la République, Dakar",
  "latitude": 14.692,
  "longitude": -17.447,
  "phone": "+221771234567",
  "hours": "Lun-Sam: 6h00 - 20h00",
  "image_urls": ["https://images.example.com/boulangerie1.jpg"]
}
```
* **Réponse (201 Created)** :
```json
{
  "id": 1,
  "owner_id": 1,
  "name": "Boulangerie Le Bon Pain",
  "category": "Boulangerie",
  "description": "Pain artisanal cuit au feu de bois et viennoiseries chaudes.",
  "address": "12 Rue de la République, Dakar",
  "latitude": 14.692,
  "longitude": -17.447,
  "phone": "+221771234567",
  "hours": "Lun-Sam: 6h00 - 20h00",
  "image_urls": ["https://images.example.com/boulangerie1.jpg"],
  "published": true,
  "average_rating": 0.0,
  "reviews_count": 0,
  "reviews": []
}
```

#### 👁️ Publier / Retirer du public (`PUT /api/businesses/{id}/publish`)
Permet au propriétaire artisan d'activer ou de suspendre l'affichage de son commerce dans l'annuaire public.
* **En-tête requis** : `Authorization: Bearer <JWT_TOKEN>`
* **Paramètres de requête** : `published=true` (pour publier) ou `published=false` (pour masquer).
* **Réponse (200 OK)** : Retourne le commerce modifié avec le statut `published` mis à jour.

#### 💬 Partage de l'adresse par WhatsApp (`GET /api/businesses/{id}/whatsapp-share`)
Renvoie un lien structuré prêt à être envoyé par WhatsApp pour propager les coordonnées de l'artisan.
* **Réponse (200 OK)** :
```json
{
  "whatsapp_link": "https://wa.me/221771234567?text=%F0%9F%93%85%20*Boulangerie%20Le...",
  "message": "📍 *Boulangerie Le Bon Pain*\n🛠️ Métier : Boulangerie\n..."
}
```

---

### 3. Recherche et Proximité (300 pts)

#### 🔍 Recherche publique (`GET /api/businesses`)
Permet de rechercher des artisans en appliquant des filtres combinés.
* **Paramètres acceptés** :
  - `query` (string) : Recherche textuelle dans le nom et la description.
  - `category` (string) : Filtrage par métier (ex: "Boulangerie", "Couture").
  - `min_rating` (float) : Filtrage par qualité de service minimale (ex: 4.0).
  - `lat` et `lng` (float) : Coordonnées GPS de l'utilisateur pour calculer les distances.
* **Calculateur de distance géolocalisée (Haversine)** :
  Si `lat` et `lng` sont renseignées, l'API calcule la distance physique et ordonne automatiquement les résultats du plus proche au plus éloigné.
  $$\text{Distance} = 2R \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)} \right)$$
* **Réponse (200 OK)** :
```json
[
  {
    "id": 1,
    "name": "Boulangerie Le Bon Pain",
    "category": "Boulangerie",
    "address": "12 Rue de la République, Dakar",
    "latitude": 14.692,
    "longitude": -17.447,
    "distance": 0.45,  // Distance calculée en kilomètres (450m)
    "average_rating": 4.8,
    "reviews_count": 12
  }
]
```

---

### 4. Intelligence Artificielle - Analyse Sentimentale (600 pts)

#### 🤖 Notation Automatique des Commentaires (`POST /api/businesses/{id}/reviews`)
Lorsqu'un citoyen laisse un avis, le backend analyse automatiquement le texte en français pour calculer la note (de 1 à 5 étoiles) et la score de sentiment. Il n'est pas nécessaire pour le client de soumettre une note : l'IA s'en charge.

* **Exemple d'avis Positif** :
  - **Requête** :
    ```json
    {
      "author_name": "Fatou Ndiaye",
      "comment": "Excellent travail, service très rapide et équipe vraiment sympathique ! Je recommande chaudement."
    }
    ```
  - **Réponse (210 Created) - Note attribuée : 5/5** :
    ```json
    {
      "review": {
        "id": 5,
        "business_id": 1,
        "author_name": "Fatou Ndiaye",
        "comment": "Excellent travail, service très rapide et équipe vraiment sympathique ! Je recommande chaudement.",
        "rating": 5,
        "sentiment_score": 8.35,
        "created_at": "2026-06-26T11:24:00Z"
      },
      "ai_analysis": {
        "sentiment_score": 8.35,
        "rating_assigned": 5,
        "sentiment_label": "très positif",
        "detected_keywords": [
          { "word": "excellent", "type": "positive", "score": 3.0 },
          { "word": "rapide", "type": "positive", "score": 2.25 },  // "très" (1.5) * "rapide" (1.5) = 2.25
          { "word": "sympathique", "type": "positive", "score": 1.95 },  // "vraiment" (1.3) * "sympathique" (1.5) = 1.95
          { "word": "recommande", "type": "positive", "score": 2.0 }
        ]
      }
    }
    ```

* **Exemple d'avis Négatif** :
  - **Requête** :
    ```json
    {
      "author_name": "Moussa Sarr",
      "comment": "Travail très mauvais et retard inacceptable. C'est très cher, je ne conseille pas."
    }
    ```
  - **Réponse (210 Created) - Note attribuée : 1/5** :
    ```json
    {
      "review": {
        "id": 6,
        "business_id": 1,
        "author_name": "Moussa Sarr",
        "comment": "Travail très mauvais et retard inacceptable. C'est très cher, je ne conseille pas.",
        "rating": 1,
        "sentiment_score": -9.25,
        "created_at": "2026-06-26T11:25:00Z"
      },
      "ai_analysis": {
        "sentiment_score": -9.25,
        "rating_assigned": 1,
        "sentiment_label": "très négatif",
        "detected_keywords": [
          { "word": "mauvais", "type": "negative", "score": -3.0 }, // "très" (1.5) * "mauvais" (-2.0) = -3.0
          { "word": "retard", "type": "negative", "score": -1.5 },
          { "word": "inacceptable", "type": "negative", "score": -3.0 },
          { "word": "cher", "type": "negative", "score": -2.25 }  // "très" (1.5) * "cher" (-1.5) = -2.25
        ]
      }
    }
    ```

* **Gestion fine des inversions par négation** (ex : *"ce n'est pas mauvais"* ou *"je ne regrette pas"* : le moteur IA détecte le mot de négation `pas` ou `ne` et inverse automatiquement le signe du sentiment associé pour une notation correcte).

---

## 🚀 Guide de Déploiement

### Déploiement Local (Développement)

1. **Cloner le dépôt GitHub**
```bash
git clone [URL_DU_DEPOT_GITHUB]
cd proxiartisan-backend
```

2. **Créer l'environnement virtuel**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
Créer ou modifier le fichier `.env` à la racine :
```env
DATABASE_URL=sqlite:///./dev.db
JWT_SECRET_KEY=votre_cle_secrete_tres_longue_et_aleatoire
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

5. **Lancer le serveur de développement**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible sur `http://localhost:8000`

### Déploiement Production avec PostgreSQL

1. **Installer PostgreSQL** sur le serveur
2. **Créer la base de données**
```sql
CREATE DATABASE proxiartisan;
CREATE USER proxiartisan_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE proxiartisan TO proxiartisan_user;
```

3. **Modifier le .env pour la production**
```env
DATABASE_URL=postgresql://proxiartisan_user:votre_mot_de_passe@localhost:5432/proxiartisan
JWT_SECRET_KEY=une_cle_secrete_tres_longue_et_aleatoire_pour_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

4. **Installer les dépendances de production**
```bash
pip install -r requirements.txt
pip install gunicorn
```

5. **Lancer avec Gunicorn**
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Déploiement avec Docker (Optionnel)

1. **Créer un Dockerfile** (à la racine du projet)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Construire et lancer le conteneur**
```bash
docker build -t proxiartisan-backend .
docker run -p 8000:8000 --env-file .env proxiartisan-backend
```

### Vérification du déploiement

Une fois déployé, vérifiez que :
- `http://votre-domaine.com/` retourne le statut "running"
- `http://votre-domaine.com/docs` affiche la documentation Swagger
- Les endpoints d'inscription et de connexion fonctionnent

### Tests de validation

Lancer la suite de tests complète :
```bash
pytest test_api.py -v
```

Ou exécuter le test manuellement :
```bash
python test_api.py
```
