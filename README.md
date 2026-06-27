# 🌟 ArtiYaar — Le numérique au service du développement local

**ArtiYaar** est une application d'annuaire géolocalisé et intelligent conçue pour propulser les artisans locaux (menuisiers, couturiers, soudeurs, mécaniciens, etc.) dans l'écosystème numérique. 

Ce projet a été réalisé par l'équipe **LogiCode** dans le cadre du Hackathon 2026.

---

## 🔗 Liens Rapides & Livrables

*   💻 **Dépôt GitHub** : [https://github.com/Nathan06-hub/ArtiYaar](https://github.com/Nathan06-hub/ArtiYaar)
*   🌍 **API de production (Render)** : [https://artiyaar.onrender.com](https://artiyaar.onrender.com)
*   📘 **Documentation Technique Complète** : [Consulter DOCUMENTATION.md](./DOCUMENTATION.md)

---

## 👥 Notre Équipe (LogiCode)

*   **Serge Landry WAONGO** : Lead & Développeur Frontend (sergewaongolandry@gmail.com)
*   **Stéphane Nathanaël MARE** : Développeur Backend (maresteph06@gmail.com)
*   **Omaïmata OUEDRAOGO** : Développeuse Frontend (omaiodg@gmail.com)
*   **Papus Aymerick KONATE** : Concepteur & Rédacteur (papuskonate74@gmail.com)
*   **Cedric NINKIEMA** : Designer UI/UX (alalande@gmail.com)

---

## ⚙️ Fonctionnalités Implémentées (1 700 points)

Conformément au cahier des charges et à la grille d'évaluation du jury :

1.  **🔑 Gestion de Comptes (200 pts)** : Inscription avec forces de mot de passe, connexion JWT sécurisée et réinitialisation de mot de passe via question/réponse secrète en base de données.
2.  **🏪 Gestion de Commerces (400 pts)** : Enregistrement multi-commerces, géolocalisation précise, activation/désactivation dynamique des fiches et partage direct sur WhatsApp.
3.  **🔍 Recherche & Filtres (300 pts)** : Recherche dynamique multicritères par nom, métier, ville, note moyenne ou par proximité réelle (calcul GPS par formule d'Haversine).
4.  **🤖 Intelligence Artificielle (600 pts)** : Système d'analyse de sentiment automatique sur les commentaires en français pour attribuer une note étoilée et afficher le badge d'opinion d'IA.
5.  **📘 Documentation (200 pts)** : Documentation technique détaillée disponible dans le fichier [DOCUMENTATION.md](./DOCUMENTATION.md).

---

## 🚀 Lancement Rapide (Local)

### Frontend (Statique)
Il suffit d'ouvrir le dossier `frontend/` à l'aide d'un serveur HTTP local :
```bash
cd frontend
python -m http.server 5000
```
Puis accédez à `http://localhost:5000` sur votre navigateur.

### Backend (FastAPI)
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---
*Développé avec passion par **LogiCode** pour valoriser le savoir-faire local.*
