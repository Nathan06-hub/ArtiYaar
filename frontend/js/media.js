/**
 * Media Module
 * Handles photo uploads, previews, and compression via Canvas
 */
const Media = {
  photos: [], // Store current photos being uploaded
  maxPhotos: 3,
  
  /**
   * Handle files selected from input
   */
  handleFiles(files) {
    if (!files || files.length === 0) return;
    
    const remainingSlots = this.maxPhotos - this.photos.length;
    if (remainingSlots <= 0) {
      window.App.showMessage(`Vous ne pouvez pas ajouter plus de ${this.maxPhotos} photos.`, 'warning');
      return;
    }
    
    // Convert FileList to Array and limit to remaining slots
    const filesArray = Array.from(files).slice(0, remainingSlots);
    
    filesArray.forEach(file => {
      if (!file.type.match('image.*')) {
        return; // Skip non-images
      }
      
      this.compressAndRead(file, (base64) => {
        this.photos.push(base64);
        this.renderPreviews();
      });
    });
  },
  
  /**
   * Compress image using Canvas to save localStorage space
   */
  compressAndRead(file, callback) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const MAX_WIDTH = 800;
        const MAX_HEIGHT = 800;
        let width = img.width;
        let height = img.height;

        if (width > height) {
          if (width > MAX_WIDTH) {
            height *= MAX_WIDTH / width;
            width = MAX_WIDTH;
          }
        } else {
          if (height > MAX_HEIGHT) {
            width *= MAX_HEIGHT / height;
            height = MAX_HEIGHT;
          }
        }

        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);
        
        // Compress to JPEG with 0.7 quality
        const dataUrl = canvas.toDataURL('image/jpeg', 0.7);
        callback(dataUrl);
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  },
  
  /**
   * Remove a photo from current state
   */
  removePhoto(index) {
    this.photos.splice(index, 1);
    this.renderPreviews();
  },
  
  /**
   * Render previews in DOM
   */
  renderPreviews() {
    const grid = document.getElementById('photo-preview-grid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    this.photos.forEach((photo, index) => {
      const div = document.createElement('div');
      div.className = 'preview-item';
      const imgSrc = window.App ? window.App.getImageUrl(photo) : photo;
      div.innerHTML = `
        <img src="${imgSrc}" alt="Preview">
        <button type="button" class="remove-preview" onclick="Media.removePhoto(${index})">
          <i class="fas fa-times"></i>
        </button>
      `;
      grid.appendChild(div);
    });
  },
  
  /**
   * Reset media state
   */
  reset() {
    this.photos = [];
    this.renderPreviews();
  },
  
  /**
   * Set photos (for editing existing fiche)
   */
  setPhotos(photosArray) {
    this.photos = [...(photosArray || [])];
    this.renderPreviews();
  },
  
  /**
   * Get current photos base64 array
   */
  getPhotos() {
    return [...this.photos];
  }
};

window.Media = Media;
