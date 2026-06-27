/**
 * Profile Module
 * Handles the public artisan profile page and reviews
 */
const ProfileUI = {
  artisan: null,
  currentRating: 0,
  artisanId: null,

  async init() {
    // Get artisan ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    this.artisanId = urlParams.get('id');

    if (!this.artisanId) {
      this.showError('Aucun artisan spécifié.');
      return;
    }

    try {
      const res = await window.App.api(`/api/businesses/${this.artisanId}`);
      this.artisan = {
        id: res.id,
        name: res.name,
        category: res.category,
        description: res.description,
        rating: res.average_rating || 0,
        reviewCount: res.reviews_count || 0,
        photos: res.image_urls || [],
        lat: res.latitude,
        lng: res.longitude,
        phone: res.phone,
        hours: res.hours,
        active: res.published,
        createdAt: res.created_at,
        ownerId: res.owner_id
      };

      this.renderProfile();
      await this.renderReviews();
      this.setupReviewForm();

      // Update page title
      document.title = `${this.artisan.name} — Artiyaar`;
    } catch(e) {
      this.showError('Artisan introuvable : ' + e.message);
    }
  },

  showError(message) {
    const container = document.getElementById('profile-content');
    container.innerHTML = `
      <div class="text-center" style="padding: 4rem; grid-column: 1 / -1;">
        <i class="fas fa-exclamation-circle text-primary" style="font-size: 3rem; margin-bottom: 1rem;"></i>
        <h2>${message}</h2>
        <a href="index.html" class="btn btn-primary mt-3">Retour à l'accueil</a>
      </div>
    `;
  },

  renderProfile() {
    const container = document.getElementById('profile-content');
    const a = this.artisan;

    // Build photo gallery
    let galleryHtml = '';
    if (a.photos && a.photos.length > 0) {
      galleryHtml = `
        <div class="profile-gallery">
          <div class="gallery-main">
            <img src="${window.App.getImageUrl(a.photos[0])}" alt="${a.name}" id="gallery-main-img">
          </div>
          ${a.photos.length > 1 ? `
            <div class="gallery-thumbs">
              ${a.photos.map((photo, i) => `
                <img src="${window.App.getImageUrl(photo)}" alt="Photo ${i + 1}" 
                     class="gallery-thumb ${i === 0 ? 'active' : ''}"
                     onclick="ProfileUI.switchPhoto(${i})">
              `).join('')}
            </div>
          ` : ''}
        </div>
      `;
    } else {
      galleryHtml = `
        <div class="profile-gallery">
          <div class="gallery-placeholder">
            <i class="fas fa-tools"></i>
            <span>Pas de photos</span>
          </div>
        </div>
      `;
    }

    // Build info section
    const starsHtml = window.App.renderStars(a.rating || 0);

    container.innerHTML = `
      ${galleryHtml}
      <div class="profile-info">
        <div class="profile-info-card card glass-panel">
          <span class="badge badge-primary mb-2">${a.category}</span>
          <h1 class="profile-name">${a.name}</h1>
          
          <div class="profile-rating mb-3">
            <div class="stars">${starsHtml}</div>
            <span class="text-muted">${(a.rating || 0).toFixed(1)} · ${a.reviewCount || 0} avis</span>
          </div>
          
          ${a.description ? `
            <div class="profile-description mb-3">
              <h3><i class="fas fa-info-circle text-primary"></i> À propos</h3>
              <p class="text-muted">${a.description}</p>
            </div>
          ` : ''}
          
          <div class="profile-details">
            ${a.lat && a.lng ? `
              <div class="profile-detail-item">
                <i class="fas fa-map-marker-alt text-primary"></i>
                <span class="text-muted">GPS: ${a.lat.toFixed(4)}, ${a.lng.toFixed(4)}</span>
              </div>
            ` : ''}
            <div class="profile-detail-item">
              <i class="fas fa-calendar text-primary"></i>
              <span class="text-muted">Membre depuis ${new Date(a.createdAt).toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })}</span>
            </div>
            <div class="profile-detail-item">
              <i class="fas fa-circle ${a.active ? 'text-success' : 'text-muted'}"></i>
              <span class="${a.active ? '' : 'text-muted'}">${a.active ? 'Actuellement actif' : 'Inactif'}</span>
            </div>
          </div>

          ${a.lat && a.lng ? `
            <a href="https://www.google.com/maps?q=${a.lat},${a.lng}" target="_blank" class="btn btn-secondary mt-3" style="width: 100%;">
              <i class="fas fa-directions"></i> Itinéraire Google Maps
            </a>
          ` : ''}

          ${a.phone ? `
            <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
              <a href="tel:${a.phone}" class="btn btn-primary" style="flex: 1; text-align: center; background-color: var(--warning); border-color: var(--warning);">
                <i class="fas fa-phone"></i> Appeler
              </a>
              <a href="https://wa.me/${a.phone.replace(/[^0-9]/g, '')}?text=${encodeURIComponent('Bonjour, j\'ai vu votre profil sur Artiyaar.')}" target="_blank" class="btn btn-success" style="flex: 1; text-align: center; background-color: #25D366; border-color: #25D366; color: white;">
                <i class="fab fa-whatsapp"></i> WhatsApp
              </a>
            </div>
          ` : ''}
        </div>
      </div>
    `;

    // Show reviews section
    document.getElementById('reviews-section').style.display = 'block';
  },

  switchPhoto(index) {
    const mainImg = document.getElementById('gallery-main-img');
    const thumbs = document.querySelectorAll('.gallery-thumb');
    
    if (this.artisan.photos[index]) {
      mainImg.src = window.App.getImageUrl(this.artisan.photos[index]);
      thumbs.forEach((t, i) => t.classList.toggle('active', i === index));
    }
  },

  setupReviewForm() {
    const currentUser = window.Storage.getCurrentUser();
    const formContainer = document.getElementById('review-form-container');
    
    if (currentUser && formContainer) {
      // Don't let artisan review their own fiche
      if (currentUser.id !== this.artisan.ownerId) {
        formContainer.style.display = 'block';
      }
    }
  },

  setRating(rating) {
    this.currentRating = rating;
    const stars = document.querySelectorAll('#star-rating-input i');
    stars.forEach((star, i) => {
      if (i < rating) {
        star.className = 'fas fa-star';
        star.style.color = 'var(--warning)';
      } else {
        star.className = 'far fa-star';
        star.style.color = '';
      }
    });
  },

  analyzeSentiment() {
    const text = document.getElementById('review-text').value.toLowerCase();
    const btn = document.getElementById('submit-review-btn');
    const status = document.getElementById('ai-status');
    
    if (text.length < 10) {
      this.setRating(0);
      status.textContent = "Commencez à écrire, l'IA évaluera votre sentiment...";
      btn.disabled = true;
      return;
    }
    
    btn.disabled = false;
    
    const positiveWords = ['excellent', 'parfait', 'super', 'génial', 'incroyable', 'bravo', 'recommande', 'rapide', 'professionnel', 'bien', 'bon', 'satisfait', 'magnifique', 'top'];
    const negativeWords = ['mauvais', 'nul', 'horrible', 'catastrophe', 'déçu', 'lent', 'arnaque', 'décevant', 'pire', 'fuyez', 'médiocre', 'retard'];
    
    let score = 3; // Base score (Neutral)
    let posCount = 0;
    let negCount = 0;
    
    positiveWords.forEach(word => {
      if (text.includes(word)) posCount++;
    });
    
    negativeWords.forEach(word => {
      if (text.includes(word)) negCount++;
    });
    
    if (posCount > 0 && negCount === 0) {
      score = posCount > 1 ? 5 : 4;
    } else if (negCount > 0 && posCount === 0) {
      score = negCount > 1 ? 1 : 2;
    } else if (posCount > negCount) {
      score = 4;
    } else if (negCount > posCount) {
      score = 2;
    } else {
      score = 3;
    }
    
    this.setRating(score);
    status.innerHTML = `<span class="text-success"><i class="fas fa-check-circle"></i> Note calculée : ${score}/5 étoiles</span>`;
  },

  async submitReview(event) {
    event.preventDefault();

    const currentUser = window.Storage.getCurrentUser();
    if (!currentUser) {
      window.App.showMessage('Veuillez vous connecter pour laisser un avis.', 'error');
      return;
    }

    const text = document.getElementById('review-text').value;
    if (!text.trim()) {
      window.App.showMessage('Veuillez écrire un commentaire.', 'error');
      return;
    }

    try {
      const res = await window.App.api(`/api/businesses/${this.artisanId}/reviews`, {
        method: "POST",
        body: JSON.stringify({
          author_name: currentUser.name,
          comment: text
        })
      });

      window.App.showMessage(`Merci pour votre avis ! Note attribuée par l'IA : ${res.rating}/5`, 'success');

      // Reset form
      document.getElementById('review-form').reset();
      this.setRating(0);
      document.getElementById('ai-status').textContent = "Commencez à écrire, l'IA évaluera votre sentiment...";

      // Re-load profile and reviews
      await this.init();
    } catch (e) {
      window.App.showMessage('Erreur lors de l\'envoi de l\'avis : ' + e.message, 'error');
    }
  },

  async renderReviews() {
    const list = document.getElementById('reviews-list');
    if (!list) return;

    try {
      const reviews = await window.App.api(`/api/businesses/${this.artisanId}/reviews`);

      if (reviews.length === 0) {
        list.innerHTML = '<p class="text-muted text-center" style="padding: 2rem;">Aucun avis pour le moment. Soyez le premier !</p>';
        return;
      }

      let html = '';
      reviews.forEach(review => {
        const starsHtml = window.App.renderStars(review.rating);
        const date = new Date(review.created_at).toLocaleDateString('fr-FR', {
          day: 'numeric', month: 'long', year: 'numeric'
        });

        html += `
          <div class="review-card card" style="margin-bottom: 1rem;">
            <div class="review-header">
              <div class="review-author">
                <div class="review-avatar">${review.author_name.charAt(0).toUpperCase()}</div>
                <div>
                  <strong>${review.author_name}</strong>
                  <div class="review-date text-muted">${date}</div>
                </div>
              </div>
              <div class="review-stars">${starsHtml}</div>
            </div>
            <p class="review-text">${review.comment}</p>
          </div>
        `;
      });

      list.innerHTML = html;
    } catch (e) {
      list.innerHTML = '<p class="text-danger text-center">Erreur lors du chargement des avis.</p>';
    }
  }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  ProfileUI.init();
});
