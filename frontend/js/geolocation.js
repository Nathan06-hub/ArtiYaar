/**
 * Geolocation Module
 * Handles HTML5 Geolocation API for capturing GPS coordinates
 */
const Geolocation = {
  /**
   * Capture user's current position
   * @param {Function} callback - Called with {lat, lng, success, error}
   */
  captureLocation(callback) {
    if (!navigator.geolocation) {
      callback({ success: false, error: "La géolocalisation n'est pas supportée par votre navigateur." });
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        callback({
          success: true,
          lat: position.coords.latitude,
          lng: position.coords.longitude
        });
      },
      (error) => {
        let msg = "Erreur de géolocalisation.";
        switch(error.code) {
          case error.PERMISSION_DENIED:
            msg = "Vous avez refusé la demande de géolocalisation.";
            break;
          case error.POSITION_UNAVAILABLE:
            msg = "Les informations de localisation sont indisponibles.";
            break;
          case error.TIMEOUT:
            msg = "La demande de géolocalisation a expiré.";
            break;
        }
        callback({ success: false, error: msg });
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  },

  /**
   * Calculate distance between two coordinates using Haversine formula
   * @returns Distance in meters
   */
  calculateDistance(lat1, lon1, lat2, lon2) {
    if (!lat1 || !lon1 || !lat2 || !lon2) return null;
    
    const R = 6371e3; // Earth radius in meters
    const φ1 = lat1 * Math.PI/180;
    const φ2 = lat2 * Math.PI/180;
    const Δφ = (lat2-lat1) * Math.PI/180;
    const Δλ = (lon2-lon1) * Math.PI/180;

    const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
              Math.cos(φ1) * Math.cos(φ2) *
              Math.sin(Δλ/2) * Math.sin(Δλ/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    return R * c; 
  }
};

window.Geolocation = Geolocation;
