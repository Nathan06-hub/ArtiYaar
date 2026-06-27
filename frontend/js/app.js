/**
 * App Module
 * Global configuration, utility functions, and initialization
 */
const App = {
  config: {
    appName: 'Artiyaar',
    apiUrl: 'https://artiyaar.onrender.com',
    categories: [
      "Boulangerie", "Boucherie", "Couture", "Coiffure", "Mécanique",
      "Menuiserie", "Soudure", "Plomberie", "Électricité", "Maçonnerie",
      "Peinture", "Réparation", "Cordonnerie", "Tailleur", "Forgeron",
      "Tapisserie", "Maroquinerie", "Poterie", "Joaillerie", "Autre"
    ]
  },

  /**
   * Helper function for making API requests to the backend
   */
  async api(path, opts = {}) {
    const headers = { ...opts.headers };
    
    if (!(opts.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }
    
    const currentUser = window.Storage ? window.Storage.getCurrentUser() : null;
    if (currentUser && currentUser.access_token) {
      headers['Authorization'] = `Bearer ${currentUser.access_token}`;
    }
    
    const res = await fetch(`${this.config.apiUrl}${path}`, { ...opts, headers });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Erreur réseau" }));
      let msg = "Erreur inconnue";
      if (err.detail) {
        if (Array.isArray(err.detail)) {
          msg = err.detail.map(d => {
            // Nettoyage simple des messages longs (ex: "Value error, ...")
            return d.msg.replace("Value error, ", "");
          }).join(", ");
        } else {
          msg = err.detail;
        }
      }
      throw new Error(msg);
    }
    if (res.status === 204) return null;
    return res.json();
  },

  state: {
    currentUser: null
  },

  /**
   * Initialize the application
   */
  init() {
    this.showSplashScreen();
    console.log(`${this.config.appName} initialized`);
    
    // Initialize storage & demo data
    if (window.Storage) {
      window.Storage.initDemoData();
      this.state.currentUser = window.Storage.getCurrentUser();
    }
    
    this.updateNavigation();
  },

  /**
   * Affichage d'un écran de chargement (Splash Screen) avec pulsation du logo
   */
  showSplashScreen() {
    // N'afficher le splash screen qu'une seule fois par session
    if (sessionStorage.getItem('has_seen_splash')) {
      return;
    }
    sessionStorage.setItem('has_seen_splash', 'true');

    // Injecter les animations CSS si non présentes
    if (!document.getElementById('splash-keyframes')) {
      const style = document.createElement('style');
      style.id = 'splash-keyframes';
      style.textContent = `
        @keyframes splash-pulse {
          0%, 100% { transform: scale(0.95); opacity: 0.85; }
          50% { transform: scale(1.05); opacity: 1; filter: drop-shadow(0 6px 15px rgba(56, 142, 60, 0.15)); }
        }
        @keyframes splash-dot {
          0%, 100% { transform: scale(0.6); opacity: 0.4; }
          50% { transform: scale(1.2); opacity: 1; }
        }
      `;
      document.head.appendChild(style);
    }
    
    const splash = document.createElement('div');
    splash.id = 'app-splash-screen';
    splash.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: #ffffff;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      z-index: 100000;
      transition: opacity 0.4s ease, visibility 0.4s ease;
    `;
    
    splash.innerHTML = `
      <div style="text-align: center;">
        <img src="img/logo.jpg" alt="Artiyaar Logo" style="height: 110px; object-fit: contain; animation: splash-pulse 1.6s ease-in-out infinite; margin-bottom: 1rem;">
        <div style="display: flex; gap: 0.4rem; justify-content: center; align-items: center; margin-top: 0.5rem;">
          <span style="width: 8px; height: 8px; border-radius: 50%; background-color: #388e3c; animation: splash-dot 1.2s infinite 0s;"></span>
          <span style="width: 8px; height: 8px; border-radius: 50%; background-color: #388e3c; animation: splash-dot 1.2s infinite 0.2s;"></span>
          <span style="width: 8px; height: 8px; border-radius: 50%; background-color: #388e3c; animation: splash-dot 1.2s infinite 0.4s;"></span>
        </div>
      </div>
    `;
    
    document.body.appendChild(splash);
    
    // Dissoudre l'overlay après 1,2s
    setTimeout(() => {
      splash.style.opacity = '0';
      splash.style.pointerEvents = 'none';
      setTimeout(() => splash.remove(), 400);
    }, 1200);
  },

  /**
   * Update header navigation based on auth state
   */
  updateNavigation() {
    const authLinks = document.getElementById('auth-links');
    const mobileAuthLink = document.getElementById('mobile-auth-link');
    
    if (this.state.currentUser) {
      // User is logged in
      const isArtisan = this.state.currentUser.role === 'artisan';
      
      if (authLinks) {
        authLinks.innerHTML = `
          <a href="${isArtisan ? 'dashboard.html' : 'profile.html'}" class="nav-link" style="margin-right: 1rem;">
            <i class="fas fa-user-circle"></i> Mon Profil
          </a>
          <button onclick="App.logout()" class="btn btn-outline" style="padding: 0.5rem 1rem;">Déconnexion</button>
        `;
      }
      
      if (mobileAuthLink) {
        mobileAuthLink.href = isArtisan ? 'dashboard.html' : 'profile.html';
      }
    } else {
      // User is not logged in
      if (authLinks) {
        authLinks.innerHTML = `
          <a href="login.html" class="nav-link">Connexion</a>
          <a href="login.html?action=register" class="btn btn-primary" style="padding: 0.5rem 1rem;">S'inscrire</a>
        `;
      }
      
      if (mobileAuthLink) {
        mobileAuthLink.href = 'login.html';
      }
    }
  },

  /**
   * Logout handler
   */
  logout() {
    if (window.Storage) {
      window.Storage.logout();
      this.state.currentUser = null;
      window.location.href = 'index.html';
    }
  },

  // --- UI Helpers --- //

  /**
   * Show a toast notification message
   */
  showMessage(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) {
      // Fallback if toast container doesn't exist on this page
      alert(message);
      return;
    }

    const icons = {
      success: 'fas fa-check-circle',
      error: 'fas fa-exclamation-circle',
      warning: 'fas fa-exclamation-triangle'
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <i class="${icons[type] || icons.success} toast-icon"></i>
      <span class="toast-message">${message}</span>
      <button class="toast-close" onclick="this.parentElement.classList.add('toast-exit'); setTimeout(() => this.parentElement.remove(), 300);">
        <i class="fas fa-times"></i>
      </button>
    `;

    container.appendChild(toast);

    // Auto-dismiss after 4 seconds
    setTimeout(() => {
      if (toast.parentElement) {
        toast.classList.add('toast-exit');
        setTimeout(() => toast.remove(), 300);
      }
    }, 4000);
  },

  /**
   * Generate a unique ID
   */
  generateId() {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
  },

  /**
   * Format distance safely
   */
  formatDistance(meters) {
    if (!meters && meters !== 0) return '';
    if (meters < 1000) {
      return `${Math.round(meters)} m`;
    }
    return `${(meters / 1000).toFixed(1)} km`;
  },
  
  /**
   * Render stars based on rating
   */
  renderStars(rating) {
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 >= 0.5 ? 1 : 0;
    const emptyStars = 5 - fullStars - halfStar;
    
    let html = '';
    for(let i=0; i<fullStars; i++) html += '<i class="fas fa-star"></i>';
    if(halfStar) html += '<i class="fas fa-star-half-alt"></i>';
    for(let i=0; i<emptyStars; i++) html += '<i class="far fa-star"></i>';
    
    return html;
  },

  /**
   * Format and sanitize image URLs (supports base64, absolute and relative backend urls)
   */
  getImageUrl(url) {
    if (!url) return 'data:image/svg+xml;charset=UTF-8,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100%" height="200" viewBox="0 0 100 100" preserveAspectRatio="none"%3E%3Crect width="100" height="100" fill="%2322263C" /%3E%3Ctext x="50" y="50" fill="%23B0B3C6" font-family="sans-serif" font-size="10" text-anchor="middle" alignment-baseline="middle"%3EPas de photo%3C/text%3E%3C/svg%3E';
    if (url.startsWith('data:') || url.startsWith('http://') || url.startsWith('https://')) {
      return url;
    }
    return `${this.config.apiUrl}${url.startsWith('/') ? '' : '/'}${url}`;
  }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});

// Expose globally
window.App = App;
