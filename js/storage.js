/**
 * Storage Module
 * Handles all data persistence using localStorage (to simulate a database)
 */
const Storage = {
  // Keys for localStorage
  KEYS: {
    USERS: 'artiyaar_users',
    CURRENT_USER: 'artiyaar_current_user',
    ARTISANS: 'artiyaar_artisans',
    REVIEWS: 'artiyaar_reviews'
  },

  /**
   * Get item from localStorage with JSON parsing
   */
  get(key, defaultValue = null) {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
      console.error(`Error reading ${key} from localStorage`, e);
      return defaultValue;
    }
  },

  /**
   * Set item to localStorage with JSON stringification
   */
  set(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (e) {
      console.error(`Error saving ${key} to localStorage`, e);
      // Handle quota exceeded error if images take too much space
      if (e.name === 'QuotaExceededError') {
        alert("L'espace de stockage est plein. Veuillez supprimer quelques photos.");
      }
      return false;
    }
  },

  /**
   * Remove item from localStorage
   */
  remove(key) {
    localStorage.removeItem(key);
  },

  // --- Domain Specific Helpers --- //

  getUsers() {
    return this.get(this.KEYS.USERS, []);
  },

  saveUsers(users) {
    return this.set(this.KEYS.USERS, users);
  },

  getCurrentUser() {
    return this.get(this.KEYS.CURRENT_USER);
  },

  setCurrentUser(user) {
    return this.set(this.KEYS.CURRENT_USER, user);
  },

  logout() {
    this.remove(this.KEYS.CURRENT_USER);
  },

  getArtisans() {
    return this.get(this.KEYS.ARTISANS, []);
  },

  saveArtisans(artisans) {
    return this.set(this.KEYS.ARTISANS, artisans);
  },
  
  getReviews() {
    return this.get(this.KEYS.REVIEWS, []);
  },
  
  saveReviews(reviews) {
    return this.set(this.KEYS.REVIEWS, reviews);
  },

  /**
   * Initialize demo data if storage is empty
   */
  initDemoData() {
    const artisans = this.getArtisans();
    if (artisans.length === 0) {
      const demoArtisans = [
        {
          id: 'demo-1',
          ownerId: 'demo-user-1',
          name: 'Atelier Kaboré Menuiserie',
          category: 'Menuiserie',
          description: 'Spécialiste en meubles sur mesure, portes et fenêtres en bois rouge.',
          lat: 12.3681, // Ouagadougou
          lng: -1.5271,
          photos: [], // Base64 would go here
          active: true,
          rating: 4.8,
          reviewCount: 12,
          createdAt: new Date().toISOString()
        },
        {
          id: 'demo-2',
          ownerId: 'demo-user-2',
          name: 'Sita Couture',
          category: 'Couture',
          description: 'Création de tenues traditionnelles et modernes. Faso Danfani.',
          lat: 12.3700,
          lng: -1.5300,
          photos: [],
          active: true,
          rating: 4.5,
          reviewCount: 8,
          createdAt: new Date().toISOString()
        }
      ];
      this.saveArtisans(demoArtisans);
    }
  }
};

// Expose globally
window.Storage = Storage;
