# DOCUMENTATION TECHNIQUE
## PROJET HACKATHON 2026 — ARTIYAAR

---

### **INFORMATIONS GÉNÉRALES**
*   **Nom du Projet** : ArtiYaar
*   **Groupe de Développement** : LogiCode
*   **Date** : 27 Juin 2026
*   **Lien du Dépôt GitHub** : [https://github.com/Nathan06-hub/ArtiYaar.git](https://github.com/Nathan06-hub/ArtiYaar.git)
*   **Branche Principale** : `main`

---

## SOMMAIRE
1.  **Présentation Générale du Projet**
    *   Le Concept
    *   Fonctionnalités Clés
2.  **Architecture du Projet**
    *   Choix Technologiques
    *   Structure des Fichiers
    *   Fonctionnement des Modules JavaScript
    *   Système de Design & Charte Graphique (CSS)
3.  **Procédure de Déploiement**
    *   Lancement Local (Développement)
    *   Déploiement en Production (GitHub Pages)
4.  **Informations du Groupe**

---

\newpage

## 1. PRÉSENTATION GÉNÉRALE DU PROJET

### Le Concept
**ArtiYaar** est une plateforme web intuitive conçue pour connecter rapidement et sans intermédiaire les utilisateurs avec les meilleurs artisans locaux (menuisiers, couturiers, soudeurs, mécaniciens, électriciens, plombiers, etc.) de leur quartier. 

Dans de nombreux pays en développement, l'artisanat local souffre d'un manque de visibilité numérique. ArtiYaar résout ce problème en offrant une vitrine technologique accessible aussi bien sur ordinateur que sur téléphone mobile, valorisant ainsi le savoir-faire local.

### Fonctionnalités Clés
*   **Moteur de Recherche Avancé** : Recherche instantanée d'artisans par mot-clé, par catégorie d'activité ou par nom de commerce.
*   **Algorithme de Tri Dynamique** : Tri par note (les mieux notés), ordre alphabétique, nouveautés, et tri par proximité.
*   **Géolocalisation & Proximité** : Utilisation de l'API de géolocalisation HTML5 pour localiser l'utilisateur et calculer sa distance réelle par rapport aux ateliers des artisans, avec visualisation sur une mini-carte interactive.
*   **Espace Artisan (Dashboard)** : Espace privé sécurisé permettant à chaque artisan de gérer son profil, d'ajouter ou modifier ses fiches d'ateliers, d'insérer des photos de ses réalisations et de suivre les avis.
*   **Système d'Avis Analysé par Intelligence Artificielle** : Les clients peuvent évaluer les services d'un artisan. Un algorithme d'analyse de sentiment automatique simule une IA pour déduire la note en étoiles à partir du texte rédigé par l'utilisateur.
*   **Génération de QR Code** : Permet à un artisan de partager facilement sa fiche en ligne grâce à un QR code unique associé à son profil.
*   **Expérience Utilisateur Mobile Exceptionnelle** : Interface PWA-ready avec un écran de démarrage (Splash Screen) animé et une barre de navigation fixée en bas de l'écran (Bottom Navigation Bar) similaire aux applications mobiles natives.

---

## 2. ARCHITECTURE DU PROJET

### Choix Technologiques
Afin de garantir des performances maximales (chargement instantané même sur des connexions mobiles limitées) et une compatibilité totale sans dépendances lourdes, l'équipe **LogiCode** a opté pour du **Vanilla Web Development** :

*   **HTML5** : Utilisation stricte de la structure sémantique (balises `<header>`, `<main>`, `<footer>`, `<section>`) conforme aux exigences SEO.
*   **CSS3 (Pur)** : Système modulaire basé sur des variables CSS centralisées (`main.css`) pour une maintenance rapide et des performances de rendu élevées. Aucun framework (comme TailwindCSS ou Bootstrap) n'a été utilisé pour conserver une légèreté totale et un design unique fait main.
*   **JavaScript (ES6+)** : Organisation modulaire en fichiers séparés gérant des responsabilités distinctes (Authentification, Stockage, Profil, Recherche, Médias).
*   **Persistance locale (Storage API)** : Utilisation du `localStorage` pour simuler une base de données côté client. Les utilisateurs, artisans, ateliers et avis sont persistés d'une session à l'autre sans nécessiter l'installation complexe d'un serveur tiers pour le jury.

### Structure des Fichiers
```text
ArtiYaar/
├── index.html           # Page d'accueil avec barre de recherche & CTA
├── services.html        # Liste de recherche des artisans avec filtres & carte
├── avis.html            # Section globale de témoignages des clients
├── contact.html         # Formulaire de contact client responsive
├── login.html           # Espace de connexion & inscription d'utilisateurs/artisans
├── dashboard.html       # Tableau de bord d'administration des fiches artisans
├── artisan-profile.html # Fiche publique d'un artisan (photos, avis IA, QR code)
├── css/
│   ├── main.css         # Variables globales, typographie, réinitialisation
│   ├── components.css   # Styles des boutons, cartes, navigations, splash screen
│   └── pages.css        # Styles spécifiques (grid de recherche, dashboard, footer)
├── js/
│   ├── app.js           # Point d'entrée de l'app, état d'auth, splash screen
│   ├── storage.js       # Gestion de la base de données localStorage & Données de démo
│   ├── auth.js          # Inscription, connexion, rôles (client/artisan)
│   ├── search.js        # Logique de recherche textuelle et de géolocalisation
│   ├── profile.js       # Rendu du profil public, avis clients & simulation d'analyse IA
│   ├── artisan.js       # Logique du dashboard (création/édition des fiches d'ateliers)
│   ├── media.js         # Téléchargement et compression des photos de réalisations
│   └── geolocation.js   # API HTML5 pour la capture de la position géographique
└── img/
    └── logo.jpg         # Identité visuelle d'ArtiYaar
```

### Fonctionnement des Modules JavaScript
1.  **`app.js`** : Initialise l'application, gère l'état de l'utilisateur connecté, met à jour dynamiquement les menus sur ordinateur et injecte la barre d'outils mobile en bas de l'écran. Il gère également le **Splash Screen** d'introduction.
2.  **`storage.js`** : Initialise un ensemble complet de données d'artisans de démonstration réalistes (coordonnées GPS, spécialités, photos) pour que le projet soit fonctionnel et testable dès le premier chargement par le jury.
3.  **`search.js`** : Gère les filtres par catégorie, la recherche par mots-clés, le calcul des distances (formule trigonométrique de calcul de distance sur la sphère terrestre) et le tri dynamique.
4.  **`profile.js`** : Affiche les détails du profil. Il inclut un script d'analyse de sentiment : à mesure que l'utilisateur écrit son avis, le script évalue les mots employés (mots positifs/négatifs) pour changer en temps réel la note en étoiles attribuée par l'IA.
5.  **`media.js`** : Utilise l'API Canvas HTML5 pour compresser les images téléchargées par l'artisan avant de les stocker au format Base64, évitant de surcharger le quota de stockage du navigateur.

### Charte Graphique & UI/UX
*   **Palette de couleurs** : Le vert naturel (`#388e3c`) évoquant la confiance et le développement durable local, associé à un fond ultra-léger (`#fafdfa`).
*   **Typographie** : Combinaison de `Inter` pour les titres (lisibilité et modernité) et `DM Sans` pour le corps du texte (confort de lecture).
*   **Responsive** : Grid s'adaptant de 1 à 4 colonnes selon la largeur de l'écran. Le pied de page s'auto-épure sur mobile et se centre harmonieusement sur PC.

---

## 3. PROCÉDURE DE DÉPLOIEMENT

### Lancement Local (Développement)
Pour exécuter et tester ArtiYaar sur votre machine locale :

1.  **Récupérer le code source** :
    ```bash
    git clone https://github.com/Nathan06-hub/ArtiYaar.git
    cd ArtiYaar
    ```
2.  **Accéder à la branche stable** :
    ```bash
    git checkout main
    ```
3.  **Lancer le serveur de développement** :
    Puisque le projet est conçu en HTML/CSS/JS statique, il n'y a pas d'étape de compilation complexe. Cependant, pour utiliser pleinement l'iframe de la carte de géolocalisation, il est fortement conseillé de le lancer via un serveur HTTP local léger :
    *   **Option VS Code** : Installer l'extension **Live Server**, puis faire un clic droit sur `index.html` -> *Open with Live Server*.
    *   **Option Python** : Si vous avez Python installé, lancez dans votre terminal :
        ```bash
        python -m http.server 5500
        ```
        Puis ouvrez `http://localhost:5500` dans votre navigateur.

### Déploiement en Production (GitHub Pages)
L'hébergement statique d'ArtiYaar est extrêmement simple et gratuit grâce à GitHub Pages :
1.  Allez sur votre dépôt GitHub.
2.  Cliquez sur **Settings** (Paramètres) -> **Pages**.
3.  Sous **Build and deployment** -> **Source**, sélectionnez **Deploy from a branch**.
4.  Sous **Branch**, choisissez `main` (dossier `/ (root)`) et cliquez sur **Save**.
5.  Votre site est alors en ligne à l'adresse suivante : `https://Nathan06-hub.github.io/ArtiYaar/`.

---

## 4. INFORMATIONS DU GROUPE

*   **Nom du Groupe** : LogiCode
*   **Équipe de Développement** :

| Nom complet | Rôle dans l'équipe | Contact (E-mail / Téléphone) |
| :--- | :--- | :--- |
| **[Membre 1 - À renseigner]** | Chef de projet / Lead Dev | [Email / Tél] |
| **[Membre 2 - À renseigner]** | Développeur Front-end / UI Designer | [Email / Tél] |
| **[Membre 3 - À renseigner]** | Rédacteur technique / Testeur | [Email / Tél] |

*(Veuillez remplir ce tableau avec les informations de vos coéquipiers avant d'exporter ce document en PDF pour le jury)*

---
*Fait avec passion par l'équipe LogiCode pour le Hackathon 2026.*
