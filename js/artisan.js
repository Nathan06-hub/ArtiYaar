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
  
  loadFiches() {
    const list = document.getElementById('my-fiches-list');
    if (!list) return;
    
    const allArtisans = window.Storage.getArtisans();
    const myFiches = allArtisans.filter(a => a.ownerId === this.currentUser.id);
    
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
    
    let html = '';
    myFiches.forEach(fiche => {
      const cover = fiche.photos && fiche.photos.length > 0 
        ? fiche.photos[0] 
        : 'data:image/svg+xml;charset=UTF-8,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100%" height="200" viewBox="0 0 100 100" preserveAspectRatio="none"%3E%3Crect width="100" height="100" fill="%2322263C" /%3E%3Ctext x="50" y="50" fill="%23B0B3C6" font-family="sans-serif" font-size="10" text-anchor="middle" alignment-baseline="middle"%3E%26%23128173; Pas de photo%3C/text%3E%3C/svg%3E';
        
      html += `
        <div class="card artisan-card">
          <img src="${cover}" class="card-img" alt="${fiche.name}">
          <div class="artisan-card-header">
            <h3 class="artisan-name">${fiche.name}</h3>
            <span class="badge ${fiche.active ? 'badge-success' : 'badge-primary'}">
              ${fiche.active ? 'Actif' : 'Inactif'}
            </span>
          </div>
          <p class="text-muted mb-2">${fiche.category}</p>
          
          <div class="artisan-meta">
            <span><i class="fas fa-star"></i> ${fiche.rating || 0} (${fiche.reviewCount || 0} avis)</span>
          </div>
          
          <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
            <button class="btn btn-outline" style="flex: 1; padding: 0.5rem;" onclick="DashboardUI.editFiche('${fiche.id}')">
              <i class="fas fa-edit"></i> Éditer
            </button>
            <button class="btn btn-outline" style="flex: 1; padding: 0.5rem;" onclick="DashboardUI.toggleFicheStatus('${fiche.id}')">
              <i class="fas fa-power-off"></i> ${fiche.active ? 'Désact.' : 'Activ.'}
            </button>
            
            <div style="display: flex; gap: 0.5rem; width: 100%; margin-top: 0.5rem;">
              <button class="btn btn-primary" style="flex: 1; padding: 0.5rem;" onclick="DashboardUI.showQrModal('${fiche.id}')">
                <i class="fas fa-qrcode"></i> QR
              </button>
              <button class="btn btn-success" style="flex: 1; padding: 0.5rem; background-color: #25D366; border-color: #25D366; color: white;" onclick="DashboardUI.shareWhatsApp('${fiche.id}')">
                <i class="fab fa-whatsapp"></i> WhatsApp
              </button>
            </div>
          </div>
        </div>
      `;
    });
    
    list.innerHTML = html;
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
  
  saveFiche(event) {
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
    
    const allArtisans = window.Storage.getArtisans();
    let fiche;
    
    if (id) {
      // Update
      const index = allArtisans.findIndex(a => a.id === id);
      if (index !== -1) {
        fiche = allArtisans[index];
        fiche.name = name;
        fiche.category = category;
        fiche.phone = phone;
        fiche.description = desc;
        fiche.lat = parseFloat(lat);
        fiche.lng = parseFloat(lng);
        fiche.photos = window.Media.getPhotos();
      }
    } else {
      // Create
      fiche = {
        id: 'artisan_' + window.App.generateId(),
        ownerId: this.currentUser.id,
        name: name,
        category: category,
        phone: phone,
        description: desc,
        lat: parseFloat(lat),
        lng: parseFloat(lng),
        photos: window.Media.getPhotos(),
        active: true,
        rating: 0,
        reviewCount: 0,
        createdAt: new Date().toISOString()
      };
      allArtisans.push(fiche);
    }
    
    window.Storage.saveArtisans(allArtisans);
    window.App.showMessage("Fiche enregistrée avec succès !", 'success');
    this.showSection('fiches');
  },
  
  editFiche(id) {
    const allArtisans = window.Storage.getArtisans();
    const fiche = allArtisans.find(a => a.id === id);
    if (!fiche) return;
    
    document.getElementById('fiche-id').value = fiche.id;
    document.getElementById('fiche-name').value = fiche.name;
    document.getElementById('fiche-category').value = fiche.category;
    document.getElementById('fiche-phone').value = fiche.phone || '';
    document.getElementById('fiche-desc').value = fiche.description || '';
    document.getElementById('fiche-lat').value = fiche.lat;
    document.getElementById('fiche-lng').value = fiche.lng;
    
    document.getElementById('form-fiche-title').textContent = 'Éditer Fiche Artisan';
    
    const gpsStatus = document.getElementById('gps-status');
    gpsStatus.innerHTML = `<i class="fas fa-check-circle"></i> Position enregistrée`;
    gpsStatus.style.color = "var(--success)";
    
    window.Media.setPhotos(fiche.photos);
    this.showSection('add-fiche');
  },
  
  toggleFicheStatus(id) {
    const allArtisans = window.Storage.getArtisans();
    const index = allArtisans.findIndex(a => a.id === id);
    if (index !== -1) {
      allArtisans[index].active = !allArtisans[index].active;
      window.Storage.saveArtisans(allArtisans);
      this.loadFiches();
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
  
  // QR Code
  qrCodeInstance: null,
  
  showQrModal(id) {
    const modal = document.getElementById('qr-modal');
    modal.classList.add('active');
    
    const container = document.getElementById('qrcode-container');
    container.innerHTML = ''; // clear previous
    
    // Construct the public URL for this artisan
    // In a real app, this would be a full domain
    const origin = window.location.origin;
    const path = window.location.pathname.substring(0, window.location.pathname.lastIndexOf('/'));
    const url = `${origin}${path}/artisan-profile.html?id=${id}`;
    
    this.qrCodeInstance = new QRCode(container, {
      text: url,
      width: 200,
      height: 200,
      colorDark : "#0F1117",
      colorLight : "#ffffff",
      correctLevel : QRCode.CorrectLevel.H
    });
    
    // Setup download button after a slight delay to allow canvas drawing
    setTimeout(() => {
      const canvas = container.querySelector('canvas');
      const btn = document.getElementById('qr-download-btn');
      if (canvas) {
        btn.href = canvas.toDataURL("image/png");
      }
    }, 500);
  },
  
  closeQrModal() {
    document.getElementById('qr-modal').classList.remove('active');
  },
  
  // WhatsApp Share
  shareWhatsApp(id) {
    const allArtisans = window.Storage.getArtisans();
    const fiche = allArtisans.find(a => a.id === id);
    if (!fiche) return;
    
    const origin = window.location.origin;
    const path = window.location.pathname.substring(0, window.location.pathname.lastIndexOf('/'));
    const url = `${origin}${path}/artisan-profile.html?id=${id}`;
    
    let message = `Découvrez ma vitrine "${fiche.name}" sur Artiyaar ! Cliquez ici : ${url}`;
    
    if (fiche.lat && fiche.lng) {
      const mapsUrl = `https://www.google.com/maps?q=${fiche.lat},${fiche.lng}`;
      message += `\n\nVous pouvez aussi me trouver à cette adresse : ${mapsUrl}`;
    }
    
    const whatsappUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;
    window.open(whatsappUrl, '_blank');
  }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  DashboardUI.init();
});
