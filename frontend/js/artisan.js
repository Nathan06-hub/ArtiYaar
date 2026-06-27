/**
 * Artisan Dashboard Controller
 */
const DashboardUI = {
  currentUser: null,
  
  init() {
    this.currentUser = window.Storage.getCurrentUser();
    if (!this.currentUser) return;
    
    if (this.currentUser.role !== 'artisan') {
      window.location.href = 'index.html';
      return;
    }
    
    // Setup UI with user info
    document.getElementById('sidebar-user-name').textContent = this.currentUser.name;
    document.getElementById('profile-name').textContent = this.currentUser.name;
    document.getElementById('profile-email').textContent = this.currentUser.email;
    
    this.populateCategories();
    this.loadFiches();
    this.setupDragAndDrop();
  },
  
  showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.dashboard-section').forEach(el => {
      el.classList.add('hidden');
    });
    
    // Remove active class from all links
    document.querySelectorAll('.sidebar-link').forEach(el => {
      el.classList.remove('active');
    });
    
    // Show requested section
    if (sectionId === 'fiches') {
      document.getElementById('section-fiches').classList.remove('hidden');
      document.querySelector('.sidebar-nav a:nth-child(1)').classList.add('active');
      this.loadFiches();
    } 
    else if (sectionId === 'add-fiche') {
      document.getElementById('section-add-fiche').classList.remove('hidden');
      document.querySelector('.sidebar-nav a:nth-child(2)').classList.add('active');
      
      // Reset form if it's new
      if (!document.getElementById('fiche-id').value) {
        this.resetForm();
      }
    }
    else if (sectionId === 'profile') {
      document.getElementById('section-profile').classList.remove('hidden');
      document.querySelector('.sidebar-nav a:nth-child(3)').classList.add('active');
    }
  },
  
  populateCategories() {
    const select = document.getElementById('fiche-category');
    if (!select) return;
    
    let html = '<option value="">Sélectionnez un métier...</option>';
    window.App.config.categories.forEach(cat => {
      html += `<option value="${cat}">${cat}</option>`;
    });
    select.innerHTML = html;
  },
  
  async loadFiches() {
    const list = document.getElementById('my-fiches-list');
    if (!list) return;
    
    try {
      const myFiches = await window.App.api("/api/businesses/my");
      
      if (myFiches.length === 0) {
        list.innerHTML = `
          <div class="text-center text-muted" style="grid-column: 1 / -1; padding: 3rem;">
            <i class="fas fa-store-slash" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
            <p>Vous n'avez pas encore créé de fiche artisan.</p>
            <button class="btn btn-primary mt-2" onclick="DashboardUI.showSection('add-fiche')">Créer ma première fiche</button>
          </div>
        `;
        return;
      }
      
      const getImgSrc = (url) => {
        if (!url) return 'data:image/svg+xml;charset=UTF-8,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100%" height="200" viewBox="0 0 100 100" preserveAspectRatio="none"%3E%3Crect width="100" height="100" fill="%2322263C" /%3E%3Ctext x="50" y="50" fill="%23B0B3C6" font-family="sans-serif" font-size="10" text-anchor="middle" alignment-baseline="middle"%3E%26%23128173; Pas de photo%3C/text%3E%3C/svg%3E';
        if (url.startsWith("data:") || url.startsWith("http://") || url.startsWith("https://")) return url;
        return window.App.config.apiUrl + url;
      };

      let html = '';
      myFiches.forEach(fiche => {
        const id = fiche.id;
        const name = fiche.name;
        const category = fiche.category;
        const rating = fiche.average_rating || 0;
        const reviewCount = fiche.reviews_count || 0;
        const active = fiche.published;
        const imgSrc = fiche.image_urls && fiche.image_urls.length > 0 ? getImgSrc(fiche.image_urls[0]) : getImgSrc(null);
          
        html += `
          <div class="card artisan-card">
            <img src="${imgSrc}" class="card-img" alt="${name}">
            <div class="artisan-card-header">
              <h3 class="artisan-name">${name}</h3>
              <span class="badge ${active ? 'badge-success' : 'badge-primary'}">
                ${active ? 'Actif' : 'Inactif'}
              </span>
            </div>
            <p class="text-muted mb-2">${category}</p>
            
            <div class="artisan-meta">
              <span><i class="fas fa-star"></i> ${rating} (${reviewCount} avis)</span>
            </div>
            
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
              <button class="btn btn-outline" style="flex: 1; padding: 0.5rem;" onclick="DashboardUI.editFiche('${id}')">
                <i class="fas fa-edit"></i> Éditer
              </button>
              <button class="btn btn-outline" style="flex: 1; padding: 0.5rem;" onclick="DashboardUI.toggleFicheStatus('${id}')">
                <i class="fas fa-power-off"></i> ${active ? 'Désact.' : 'Activ.'}
              </button>
              
              <div style="display: flex; gap: 0.5rem; width: 100%; margin-top: 0.5rem;">
                <button class="btn btn-primary" style="flex: 1; padding: 0.5rem;" onclick="DashboardUI.showQrModal('${id}')">
                  <i class="fas fa-qrcode"></i> QR
                </button>
                <button class="btn btn-success" style="flex: 1; padding: 0.5rem; background-color: #25D366; border-color: #25D366; color: white;" onclick="DashboardUI.shareWhatsApp('${id}')">
                  <i class="fab fa-whatsapp"></i> WhatsApp
                </button>
              </div>
            </div>
          </div>
        `;
      });
      
      list.innerHTML = html;
    } catch (e) {
      window.App.showMessage("Erreur de chargement des fiches : " + e.message, 'error');
    }
  },
  
  resetForm() {
    document.getElementById('fiche-form').reset();
    document.getElementById('fiche-id').value = '';
    document.getElementById('form-fiche-title').textContent = 'Nouvelle Fiche Artisan';
    document.getElementById('fiche-lat').value = '';
    document.getElementById('fiche-lng').value = '';
    document.getElementById('fiche-phone').value = '';
    
    const gpsStatus = document.getElementById('gps-status');
    gpsStatus.textContent = "Position non définie";
    gpsStatus.className = "mb-1 text-muted";
    
    window.Media.reset();
  },
  
  onLocationCaptured(result) {
    const status = document.getElementById('gps-status');
    
    if (result.success) {
      document.getElementById('fiche-lat').value = result.lat;
      document.getElementById('fiche-lng').value = result.lng;
      status.innerHTML = `<i class="fas fa-check-circle"></i> Position capturée (${result.lat.toFixed(4)}, ${result.lng.toFixed(4)})`;
      status.className = "mb-1 text-success";
      status.style.color = "var(--success)";
    } else {
      status.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${result.error}`;
      status.className = "mb-1 form-error visible";
    }
  },
  
  async saveFiche(event) {
    event.preventDefault();
    
    const id = document.getElementById('fiche-id').value;
    const name = document.getElementById('fiche-name').value;
    const category = document.getElementById('fiche-category').value;
    const phone = document.getElementById('fiche-phone').value;
    const desc = document.getElementById('fiche-desc').value;
    const lat = document.getElementById('fiche-lat').value;
    const lng = document.getElementById('fiche-lng').value;
    
    if (!lat || !lng) {
      window.App.showMessage("Veuillez capturer la position GPS de votre atelier.", 'warning');
      return;
    }
    
    const payload = {
      name: name,
      category: category,
      phone: phone,
      description: desc,
      latitude: parseFloat(lat),
      longitude: parseFloat(lng),
      image_urls: window.Media.getPhotos(),
      hours: "Lun-Sam: 8h00 - 19h00"
    };

    try {
      if (id) {
        await window.App.api(`/api/businesses/${id}`, {
          method: "PUT",
          body: JSON.stringify(payload)
        });
        window.App.showMessage("Fiche mise à jour !", 'success');
      } else {
        await window.App.api("/api/businesses", {
          method: "POST",
          body: JSON.stringify(payload)
        });
        window.App.showMessage("Fiche créée avec succès !", 'success');
      }
      this.showSection('fiches');
    } catch (e) {
      window.App.showMessage("Erreur d'enregistrement : " + e.message, 'error');
    }
  },
  
  async editFiche(id) {
    try {
      const fiche = await window.App.api(`/api/businesses/${id}`);
      
      document.getElementById('fiche-id').value = fiche.id;
      document.getElementById('fiche-name').value = fiche.name;
      document.getElementById('fiche-category').value = fiche.category;
      document.getElementById('fiche-phone').value = fiche.phone || '';
      document.getElementById('fiche-desc').value = fiche.description || '';
      document.getElementById('fiche-lat').value = fiche.latitude;
      document.getElementById('fiche-lng').value = fiche.longitude;
      
      document.getElementById('form-fiche-title').textContent = 'Éditer Fiche Artisan';
      
      const gpsStatus = document.getElementById('gps-status');
      gpsStatus.innerHTML = `<i class="fas fa-check-circle"></i> Position enregistrée`;
      gpsStatus.style.color = "var(--success)";
      
      window.Media.setPhotos(fiche.image_urls || []);
      this.showSection('add-fiche');
    } catch (e) {
      window.App.showMessage("Erreur de récupération de la fiche : " + e.message, 'error');
    }
  },
  
  async toggleFicheStatus(id) {
    try {
      const fiche = await window.App.api(`/api/businesses/${id}`);
      const newStatus = !fiche.published;
      
      await window.App.api(`/api/businesses/${id}/publish?published=${newStatus}`, {
        method: "PUT"
      });
      
      window.App.showMessage(newStatus ? "Fiche activée !" : "Fiche désactivée.", 'success');
      this.loadFiches();
    } catch (e) {
      window.App.showMessage("Erreur de modification du statut : " + e.message, 'error');
    }
  },
  
  // Drag and drop for photo upload
  setupDragAndDrop() {
    const dropArea = document.getElementById('upload-area');
    if (!dropArea) return;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults (e) {
      e.preventDefault();
      e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
      dropArea.addEventListener(eventName, () => dropArea.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropArea.addEventListener(eventName, () => dropArea.classList.remove('dragover'), false);
    });

    dropArea.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      window.Media.handleFiles(files);
    }, false);
  },
  
  showQrModal(id) {
    const modal = document.getElementById('qr-modal');
    modal.classList.add('active');
    
    const container = document.getElementById('qrcode-container');
    // Affiche directement l'image PNG générée par le backend
    const qrUrl = `${window.App.config.apiUrl}/api/businesses/${id}/qrcode`;
    container.innerHTML = `<img src="${qrUrl}" alt="QR Code" style="max-width: 100%; border-radius: 8px;">`;
    
    const btn = document.getElementById('qr-download-btn');
    if (btn) {
      btn.href = qrUrl;
      btn.target = "_blank";
    }
  },
  
  closeQrModal() {
    document.getElementById('qr-modal').classList.remove('active');
  },
  
  // WhatsApp Share via API backend
  async shareWhatsApp(id) {
    try {
      const res = await window.App.api(`/api/businesses/${id}/whatsapp-share`);
      window.open(res.whatsapp_link, '_blank');
    } catch (e) {
      window.App.showMessage("Impossible de générer le lien WhatsApp : " + e.message, 'error');
    }
  }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  DashboardUI.init();
});
