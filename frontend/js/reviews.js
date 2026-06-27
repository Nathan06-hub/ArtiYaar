/**
 * Reviews Module
 * Fetches and displays all reviews dynamically from the backend database
 */
const ReviewsUI = {
  async init() {
    const container = document.getElementById('reviews-list');
    if (!container) return;
    
    container.innerHTML = `
      <div class="text-center text-muted" style="grid-column: 1 / -1; padding: 3rem;">
        <i class="fas fa-spinner fa-spin" style="font-size: 2rem; margin-bottom: 1rem;"></i>
        <p>Chargement des avis en cours...</p>
      </div>
    `;
    
    try {
      const businesses = await window.App.api('/api/businesses');
      const allReviews = [];
      
      businesses.forEach(b => {
        if (b.reviews && b.reviews.length > 0) {
          b.reviews.forEach(r => {
            allReviews.push({
              ...r,
              businessName: b.name,
              businessId: b.id
            });
          });
        }
      });
      
      // Sort reviews by date descending (newest first)
      allReviews.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      
      if (allReviews.length === 0) {
        container.innerHTML = `
          <div class="text-center text-muted" style="grid-column: 1 / -1; padding: 4rem;">
            <i class="fas fa-comment-slash" style="font-size: 3rem; opacity: 0.3; margin-bottom: 1rem;"></i>
            <h3>Aucun avis enregistré</h3>
            <p>Soyez le premier à laisser un avis sur la page de profil d'un artisan !</p>
          </div>
        `;
        return;
      }
      
      let html = '';
      allReviews.forEach(r => {
        const initial = r.author_name ? r.author_name.charAt(0).toUpperCase() : 'C';
        const dateStr = new Date(r.created_at).toLocaleDateString('fr-FR', {
          day: 'numeric', month: 'short', year: 'numeric'
        });
        const starsHtml = window.App.renderStars(r.rating);
        
        // Sentiment indicator badge
        let sentimentClass = 'badge-muted';
        let sentimentText = 'Neutre';
        if (r.sentiment_score > 0.6) {
          sentimentClass = 'badge-success';
          sentimentText = 'Positif';
        } else if (r.sentiment_score < 0.4) {
          sentimentClass = 'badge-danger';
          sentimentText = 'Négatif';
        }
        
        html += `
          <div class="card glass-panel" style="padding: 2rem; display: flex; flex-direction: column; justify-content: space-between; min-height: 180px; animation: fadeSlideUp 0.4s ease both;">
            <div>
              <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <div style="width: 50px; height: 50px; border-radius: 50%; background: var(--primary-light); display: flex; align-items: center; justify-content: center; color: var(--primary-color); font-weight: bold; font-size: 1.2rem;">
                  ${initial}
                </div>
                <div style="flex: 1;">
                  <h3 style="margin: 0; font-size: 1.1rem; display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; flex-wrap: wrap;">
                    <span>${r.author_name}</span>
                    <small style="font-size: 0.8rem; font-weight: normal;" class="text-muted">${dateStr}</small>
                  </h3>
                  <div style="display: flex; align-items: center; gap: 0.5rem; margin-top: 0.2rem;">
                    <div style="color: var(--warning); font-size: 0.9rem;">
                      ${starsHtml}
                    </div>
                    <span class="badge ${sentimentClass}" style="font-size: 0.7rem; padding: 0.1rem 0.4rem; display: inline-flex; align-items: center; gap: 0.2rem;">
                      <i class="fas fa-robot"></i> IA: ${sentimentText}
                    </span>
                  </div>
                </div>
              </div>
              <p class="text-muted" style="font-style: italic;">"${r.comment}"</p>
            </div>
            
            <div style="margin-top: 1.5rem; text-align: right; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 0.8rem;">
              <a href="artisan-profile.html?id=${r.businessId}" class="text-primary" style="font-size: 0.85rem; font-weight: 500; text-decoration: none; display: inline-flex; align-items: center; gap: 0.3rem;">
                Chez : ${r.businessName} <i class="fas fa-arrow-right" style="font-size: 0.75rem;"></i>
              </a>
            </div>
          </div>
        `;
      });
      container.innerHTML = html;
      
    } catch (e) {
      container.innerHTML = `
        <div class="text-center text-danger" style="grid-column: 1 / -1; padding: 3rem;">
          <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
          <p>Erreur lors du chargement des avis : ${e.message}</p>
        </div>
      `;
    }
  }
};

document.addEventListener('DOMContentLoaded', () => {
  ReviewsUI.init();
});
