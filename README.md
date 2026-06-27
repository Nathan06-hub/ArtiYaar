#  ArtiYaar - Trouvez l'artisan qu'il vous faut

**ArtiYaar** est une plateforme web moderne conçue pour connecter facilement les utilisateurs avec les meilleurs artisans locaux (menuisiers, couturiers, soudeurs, mécaniciens, etc.) de leur quartier. Le projet vise à soutenir l'artisanat local en offrant une visibilité numérique aux travailleurs manuels.

![Aperçu du Projet](img/logo.jpg)

##  Fonctionnalités Principales

*   ** Recherche Avancée** : Trouvez des commerces et ateliers à proximité par nom, par catégorie métier, ou par la qualité de leur service (les mieux notés).
*   ** Géolocalisation** : Option de tri "Plus proche" permettant de calculer la distance réelle entre l'utilisateur et les artisans.
*   ** Design 100% Responsive & Mobile-First** : 
    *   Interface parfaitement adaptée aux téléphones avec une **Bottom Navigation Bar** type application native.
    *   Vue bureau spacieuse et élégante.
*   ** UI/UX Moderne** :
    *   Design épuré avec des palettes de couleurs harmonieuses (`var(--primary-color)`).
    *   Effets "Glassmorphism" et micro-animations fluides.
*   ** Espace Artisan (Dashboard)** : 
    *   Tableau de bord dédié aux artisans pour créer, modifier et gérer leurs "fiches" (ateliers).
    *   Gestion de profil et suivi des avis clients.

##  Technologies Utilisées

Ce projet (branche `front`) est construit exclusivement avec des technologies web standards, sans framework lourd, pour garantir des performances optimales et un contrôle total sur le design :

*   **HTML5** : Structure sémantique complète.
*   **CSS3 (Vanilla)** : Système de design basé sur des variables CSS personnalisées (`main.css`), Flexbox, CSS Grid et Media Queries.
*   **JavaScript (Vanilla)** : Logique de l'application (`app.js`, `search.js`), gestion de l'état de l'utilisateur, tri dynamique et interactivité.
*   **FontAwesome** : Bibliothèque d'icônes vectorielles.

##  Structure du Projet

```text
Hackathon/
├── index.html           # Page d'accueil avec barre de recherche
├── services.html        # Liste des catégories et services
├── avis.html            # Section des témoignages clients
├── contact.html         # Formulaire et informations de contact
├── login.html           # Page de connexion / inscription
├── dashboard.html       # Espace de gestion privé pour les artisans
├── artisan-profile.html # Page publique de présentation d'un artisan
├── css/
│   ├── main.css         # Variables de couleurs, typographie et base
│   ├── components.css   # Styles des boutons, cartes, navigation
│   └── pages.css        # Styles spécifiques à chaque vue (dashboard, etc.)
├── js/
│   ├── app.js           # Navigation dynamique, auth state, utilitaires
│   └── search.js        # Moteur de recherche et algorithme de tri
└── img/                 # Ressources graphiques et logos
```

##  Installation & Lancement

Le projet étant un site web statique, il est très simple à déployer et à tester :

1.  **Cloner le dépôt :**
    ```bash
    git clone https://github.com/Nathan06-hub/ArtiYaar.git
    cd ArtiYaar
    ```
2.  **Basculer sur la branche front :**
    ```bash
    git checkout front
    ```
3.  **Lancer le projet :**
    Il vous suffit d'ouvrir le fichier `index.html` dans n'importe quel navigateur web moderne.
    *Note : Pour une meilleure expérience (notamment pour tester la géolocalisation ou éviter les problèmes de CORS avec certains imports), il est recommandé d'utiliser une extension comme "Live Server" sur VS Code.*

##  Contribution

Si vous souhaitez contribuer à l'amélioration de l'interface ou ajouter de nouvelles fonctionnalités :

1.  Faites un Fork du projet
2.  Créez votre branche de fonctionnalité (`git checkout -b feature/NouvelleFonctionnalite`)
3.  Commitez vos changements (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`)
4.  Poussez vers la branche (`git push origin feature/NouvelleFonctionnalite`)
5.  Ouvrez une Pull Request

---
*Réalisée par logicode pour soutenir l'artisanat local.*
