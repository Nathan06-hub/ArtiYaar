/**
 * Search Module
 * Handles artisan search, filtering, and display on the landing page
 */
const SearchUI = {
  allArtisans: [],
  filteredArtisans: [],
  currentCategory: 'all',
  userLocation: null,

  async init() {
    this.allArtisans = [];
    this.filteredArtisans = [];
    
    // 1. Charger tous les artisans depuis la base de données au démarrage
    try {
      const all = await window.App.api("/api/businesses");
      this.allArtisans = all.map(b => ({
        id: b.id,
        name: b.name,
        category: b.category,
        address: b.address,
        description: b.description,
        rating: b.average_rating || 0,
        reviewCount: b.reviews_count || 0,
        photos: b.image_urls || [],
        lat: b.latitude,
        lng: b.longitude
      }));
      this.filteredArtisans = [...this.allArtisans];
    } catch (e) {
      console.error("Erreur au chargement des artisans : ", e);
    }
    
    // 2. Construire les filtres et statistiques
    this.buildCategoryFilters();
    this.updateStats();
    this.render();
    if (document.getElementById('artisan-results')) {
      this.getUserLocation();
    }

    // Bind enter key on search
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') this.search();
      });
    }
  },

  buildCategoryFilters() {
    const container = document.getElementById('category-filters');
    if (!container) return;

    const categories = window.App.config.categories;

    // Ajouter les boutons de catégories dynamiquement d'après les artisans présents
    categories.forEach(cat => {
      const count = this.allArtisans.filter(a => a.category === cat).length;
      if (count > 0) {
        const btn = document.createElement('button');
        btn.className = 'btn btn-outline filter-btn';
        btn.dataset.category = cat;
        btn.innerHTML = `${cat} <span class="filter-count">${count}</span>`;
        btn.onclick = () => this.filterByCategory(cat, btn);
        container.appendChild(btn);
      }
    });
  },

  filterByCategory(category, btnElement) {
    this.currentCategory = category;
    
    // Update active state
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    if (btnElement) btnElement.classList.add('active');

    this.applyFilters();
  },

  search() {
    this.applyFilters();
  },

  async applyFilters() {
    const query = (document.getElementById('search-input')?.value || '').trim();

    let path = "/api/businesses?";
    const params = new URLSearchParams();
    if (query) params.append("query", query);
    if (this.currentCategory !== 'all') params.append("category", this.currentCategory);
    if (this.userLocation) {
      params.append("lat", this.userLocation.lat);
      params.append("lng", this.userLocation.lng);
    }

    try {
      const res = await window.App.api(path + params.toString());
      this.filteredArtisans = res.map(b => ({
        id: b.id,
        name: b.name,
        category: b.category,
        address: b.address,
        description: b.description,
        rating: b.average_rating || 0,
        reviewCount: b.reviews_count || 0,
        photos: b.image_urls || [],
        lat: b.latitude,
        lng: b.longitude
      }));

      // Sort
      const sortValue = document.getElementById('sort-select')?.value || 'rating';
      this.sortArtisans(sortValue);

      this.render();
      this.updateResultsTitle();
    } catch (e) {
      console.error("Erreur API de filtrage", e);
    }
  },

  sort(value) {
    this.sortArtisans(value);
    this.render();
  },

  sortArtisans(by) {
    switch (by) {
      case 'rating':
        this.filteredArtisans.sort((a, b) => (b.rating || 0) - (a.rating || 0));
        break;
      case 'name':
        this.filteredArtisans.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'recent':
        this.filteredArtisans.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
        break;
      case 'distance':
        if (this.userLocation) {
          this.filteredArtisans.sort((a, b) => {
            const distA = window.Geolocation.calculateDistance(
              this.userLocation.lat, this.userLocation.lng, a.lat, a.lng
            ) || Infinity;
            const distB = window.Geolocation.calculateDistance(
              this.userLocation.lat, this.userLocation.lng, b.lat, b.lng
            ) || Infinity;
            return distA - distB;
          });
        }
        break;
    }
  },

  getUserLocation() {
    window.Geolocation.captureLocation((result) => {
      if (result.success) {
        this.userLocation = { lat: result.lat, lng: result.lng };
        
        // Add distance sort option
        const sortSelect = document.getElementById('sort-select');
        if (sortSelect && !sortSelect.querySelector('option[value="distance"]')) {
          const opt = document.createElement('option');
          opt.value = 'distance';
          opt.textContent = 'Plus proche';
          sortSelect.appendChild(opt);
        }

        // Re-render to show distances
        this.render();
      }
    });
  },

  updateStats() {
    const artisans = this.allArtisans;
    
    // 1. Nombre d'artisans
    const statArtisans = document.getElementById('stat-artisans');
    if (statArtisans) statArtisans.textContent = artisans.length;
    
    // 2. Nombre de métiers (catégories uniques représentées)
    const uniqueCategories = new Set(artisans.map(a => a.category));
    const statCategories = document.getElementById('stat-categories');
    if (statCategories) statCategories.textContent = uniqueCategories.size;
    
    // 3. Nombre de villes (extrait le dernier mot/ville de l'adresse de l'artisan)
    const cities = artisans.map(a => {
      if (!a.address) return null;
      const parts = a.address.split(',');
      return parts[parts.length - 1].trim();
    }).filter(Boolean);
    const uniqueCities = new Set(cities);
    const statCities = document.getElementById('stat-cities');
    if (statCities) statCities.textContent = uniqueCities.size || 1;
    
    // 4. Nombre total d'avis cumulés
    const totalReviews = artisans.reduce((sum, a) => sum + (a.reviewCount || 0), 0);
    const statReviews = document.getElementById('stat-reviews');
    if (statReviews) statReviews.textContent = totalReviews;
  },

  updateResultsTitle() {
    const title = document.getElementById('results-title');
    if (!title) return;

    if (this.currentCategory !== 'all') {
      title.textContent = `${this.currentCategory} (${this.filteredArtisans.length})`;
    } else {
      title.textContent = `Artisans à proximité (${this.filteredArtisans.length})`;
    }
  },

  render() {
    const container = document.getElementById('artisan-results');
    if (!container) return;

    if (this.filteredArtisans.length === 0) {
      container.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <i class="fas fa-search" style="font-size: 3rem; color: var(--text-muted); opacity: 0.4; margin-bottom: 1rem;"></i>
          <h3 class="text-muted">Aucun artisan trouvé</h3>
          <p class="text-muted">Essayez un autre terme de recherche ou une autre catégorie.</p>
        </div>
      `;
      return;
    }

    let html = '';
    this.filteredArtisans.forEach((artisan, index) => {
      const cover = artisan.photos && artisan.photos.length > 0
        ? window.App.getImageUrl(artisan.photos[0])
        : null;

      let distanceHtml = '';
      if (this.userLocation && artisan.lat && artisan.lng) {
        const dist = window.Geolocation.calculateDistance(
          this.userLocation.lat, this.userLocation.lng, artisan.lat, artisan.lng
        );
        if (dist !== null) {
          distanceHtml = `<span><i class="fas fa-location-dot"></i> ${window.App.formatDistance(dist)}</span>`;
        }
      }

      html += `
        <div class="card artisan-card" style="animation: fadeSlideUp 0.4s ease ${index * 0.08}s both;">
          ${cover 
            ? `<img src="${cover}" class="card-img" alt="${artisan.name}" loading="lazy">`
            : `<div class="card-img-placeholder"><i class="fas fa-tools"></i></div>`
          }
          <div class="artisan-card-header">
            <h3 class="artisan-name">${artisan.name}</h3>
            <div class="artisan-rating">
              <i class="fas fa-star"></i>
              <span>${(artisan.rating || 0).toFixed(1)}</span>
            </div>
          </div>
          <div class="artisan-meta">
            <span><i class="fas fa-tag"></i> ${artisan.category}</span>
            ${distanceHtml}
          </div>
          <p class="artisan-desc text-muted">${(artisan.description || '').substring(0, 100)}${(artisan.description || '').length > 100 ? '...' : ''}</p>
          <a href="artisan-profile.html?id=${artisan.id}" class="btn btn-primary" style="width: 100%; margin-top: auto;">
            <i class="fas fa-eye"></i> Voir le profil
          </a>
        </div>
      `;
    });

    container.innerHTML = html;
  }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  SearchUI.init();
});
