/**
 * App Module
 * Global configuration, utility functions, and initialization
 */
const App = {
  config: {
    appName: 'Artiyaar',
    categories: [
      'Menuiserie',
      'Couture',
      'Soudure',
      'Mécanique',
      'Maçonnerie',
      'Électricité',
      'Plomberie',
      'Coiffure',
      'Restauration',
      'Autre'
    ]
  },

  state: {
    currentUser: null
  },

  /**
   * Initialize the application
   */
  init() {
    console.log(`${this.config.appName} initialized`);
    
    // Initialize storage & demo data
    if (window.Storage) {
      window.Storage.initDemoData();
      this.state.currentUser = window.Storage.getCurrentUser();
    }
    
    this.updateNavigation();
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
          ${isArtisan ? '<a href="dashboard.html" class="nav-link">Dashboard</a>' : ''}
          <span class="nav-link text-muted" style="margin-right: 1rem;"><i class="fas fa-user"></i> ${this.state.currentUser.name}</span>
          <button onclick="App.logout()" class="btn btn-outline" style="padding: 0.5rem 1rem;">Déconnexion</button>
        `;
      }
      
      if (mobileAuthLink) {
        mobileAuthLink.href = isArtisan ? 'dashboard.html' : '#';
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
  }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});

// Expose globally
window.App = App;
