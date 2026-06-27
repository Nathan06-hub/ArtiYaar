# 📘 Documentation Technique — ArtiYaar
### Projet Hackathon 2026 — Équipe **LogiCode**
#### Thème : *« Le numérique au service du développement local »*

---

## 👥 1. Informations du Groupe

L'application **ArtiYaar** a été conçue, développée et documentée par l'équipe **LogiCode** :

| Nom complet | Rôle dans l'équipe | Contact Email |
| :--- | :--- | :--- |
| **Serge Landry WAONGO** | Lead & Développeur Frontend | sergewaongolandry@gmail.com |
| **Stéphane Nathanaël MARE** | Développeur Backend | maresteph06@gmail.com |
| **Omaïmata OUEDRAOGO** | Développeuse Frontend | omaiodg@gmail.com |
| **Papus Aymerick KONATE** | Concepteur & Rédacteur | papuskonate74@gmail.com |
| **Cedric NINKIEMA** | Designer UI/UX | alalande@gmail.com |

---

## 🏗️ 2. Architecture du Projet

Le projet adopte une architecture Monorepo moderne et découplée, facilitant la maintenance et la mise en production.

```text
ArtiYaar/
├── app/                  # --- BACKEND FASTAPI ---
│   ├── main.py           # Point d'entrée de l'application API FastAPI
│   ├── database.py       # Configuration SQLAlchemy & connexion PostgreSQL
│   ├── models.py         # Modèles de base de données ORM
│   ├── schemas.py        # Schémas de validation des données Pydantic
│   ├── crud.py           # Requêtes et opérations de base de données (Create, Read, Update, Delete)
│   ├── auth.py           # Utilitaires de hashage, sécurité & génération de tokens JWT
│   └── routers/          # Routes API découpées par modules
│       ├── auth.py       # Routes d'authentification & réinitialisation de mot de passe
│       └── business.py   # Routes de gestion des fiches commerces & des avis IA
├── frontend/             # --- FRONTEND VANILLA ---
│   ├── index.html        # Page d'accueil & exploration globale
│   ├── services.html     # Recherche filtrée par catégories & métiers
│   ├── avis.html         # Tableau de bord des retours clients & analyses IA
│   ├── contact.html      # Informations pratiques & contact de l'équipe
│   ├── login.html        # Portails d'authentification (Connexion/Inscription/Réinitialisation)
│   ├── profile.html      # Espace Profil utilisateur (Citoyen) & historique des avis
│   ├── dashboard.html    # Espace d'administration pour les Artisans
│   ├── artisan-profile.html # Vitrine publique et détaillée d'un artisan (avis, WhatsApp, GPS)
│   ├── css/              # Système de design unifié (styles atomiques, variables CSS)
│   │   ├── main.css      # Thème global, typographie et couleurs
│   │   ├── components.css # Boutons, cartes, fenêtres modales
│   │   └── pages.css     # Ajustements spécifiques et responsivité mobile
│   ├── js/               # Logique applicative & communication API
│   │   ├── app.js        # Initialisateur, Splash Screen, routage global & helper API
│   │   ├── auth.js       # Authentification & gestion de session
│   │   ├── search.js     # Moteur de recherche et géolocalisation locale
│   │   ├── artisan.js    # Logique d'administration des fiches artisans
│   │   ├── media.js      # Gestion d'images et convertisseur base64
│   │   └── reviews.js    # Injection et affichage dynamique des avis et sentiments IA
│   └── img/              # Ressources d'identité visuelle (Logo, bannières)
└── requirements.txt      # Dépendances Python requises pour le Backend
```

### Choix Architecturaux :
1. **Backend (API RESTful - FastAPI)** :
   - *Rapidité & Performance* : FastAPI est l'un des frameworks Python les plus rapides du marché.
   - *Sécurité* : Validation automatique des schémas de données via Pydantic, évitant les injections et les données polluées.
   - *Authentification* : Utilisation de jetons chiffrés **JWT (JSON Web Tokens)** pour une authentification stateless sécurisée.
2. **Frontend (Vanilla HTML/CSS/JS)** :
   - *Rapidité extrême* : Aucun framework lourd (React/Angular) n'a été utilisé pour éliminer les temps de chargement et le poids des bundles, offrant une fluidité instantanée sur mobile.
   - *Lightweight design system* : Utilisation exclusive de variables CSS personnalisées (`main.css`) pour une maintenance rapide et des temps de rendu optimisés.
3. **Persistance des données (PostgreSQL)** :
   - Base de données relationnelle robuste de production permettant de lier efficacement les tables `User`, `Business` et `Review` avec intégrité référentielle.

---

## 🧠 3. Fonctionnalités Spéciales & Intelligence Artificielle

### 🤖 Analyse Automatique de Sentiment
Pour maximiser les points du module d'Intelligence Artificielle (**600 pts**), ArtiYaar intègre une analyse automatique de sentiment :
- À chaque dépôt d'avis par un client, le texte du commentaire en français est analysé côté backend.
- L'algorithme calcule un score de polarité compris entre `0.0` (extrêmement négatif) et `1.0` (extrêmement positif).
- **Notation automatique** : Le backend attribue automatiquement une note sur 5 étoiles en fonction de l'humeur du commentaire.
- **Badge d'opinion IA** : Le frontend affiche en temps réel un badge calculé par l'IA (`Positif`, `Négatif` ou `Neutre`) pour renseigner l'artisan et les futurs clients.

### 📍 Géolocalisation & Calcul de Distance Réelle
- L'application utilise l'API de géolocalisation native des navigateurs.
- Lorsque l'utilisateur trie par "Plus proche", la distance réelle (en kilomètres) entre les coordonnées GPS de son appareil et celles des ateliers physiques des artisans est calculée grâce à la formule de l'**Haversine** :
  \[d = 2r \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)\]
  Où \(r = 6371\) km (rayon de la Terre), \(\phi\) est la latitude et \(\lambda\) la longitude.

---

## 🚀 4. Procédure de Déploiement

### Déploiement du Backend (Render)
1. Créer un service de base de données PostgreSQL sur Render.
2. Créer un nouveau Web Service lié au dépôt GitHub.
3. Configurer les variables d'environnement suivantes dans Render :
   - `DATABASE_URL` : L'URL de connexion PostgreSQL fournie par Render.
   - `SECRET_KEY` : Clé de chiffrement pour les tokens JWT.
4. Lancer le déploiement. L'API sera accessible publiquement (URL actuelle : `https://artiyaar.onrender.com`).

### Lancement Local du Frontend
1. Cloner le dépôt :
   ```bash
   git clone https://github.com/Nathan06-hub/ArtiYaar.git
   cd ArtiYaar
   ```
2. Lancer un serveur local léger (par exemple, avec Python) :
   ```bash
   python -m http.server 5000
   ```
3. Ouvrir votre navigateur sur `http://localhost:5000`.

---

## 🔗 5. Dépôt GitHub & Rendu Final

* **Lien du dépôt GitHub officiel** : [https://github.com/Nathan06-hub/ArtiYaar](https://github.com/Nathan06-hub/ArtiYaar)
* **API de production (Render)** : [https://artiyaar.onrender.com](https://artiyaar.onrender.com)
