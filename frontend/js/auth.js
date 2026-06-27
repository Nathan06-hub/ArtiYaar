/**
 * Auth Module
 * Handles authentication logic (simulated with localStorage)
 */
const Auth = {
  /**
   * Register a new user
   * @param {Object} userData - {name, email, password}
   */
  async register(userData) {
    try {
      const res = await window.App.api("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({
          name: userData.name,
          email: userData.email,
          password: userData.password,
          role: userData.role || "citoyen",
          reset_question: userData.reset_question || "Ma ville de naissance?",
          reset_answer: userData.reset_answer || "Dakar"
        })
      });
      
      // Auto-login après inscription
      return await this.login(userData.email, userData.password);
    } catch (e) {
      return { success: false, message: e.message };
    }
  },

  /**
   * Login user via API
   * @param {string} email 
   * @param {string} password 
   */
  async login(email, password) {
    try {
      const res = await window.App.api("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });
      
      // Sauvegarde dans localStorage avec le jeton access_token
      window.Storage.setCurrentUser({
        id: res.id,
        name: res.name,
        email: res.email,
        role: res.role,
        access_token: res.access_token
      });
      
      return { success: true, user: res };
    } catch (e) {
      return { success: false, message: e.message };
    }
  }
};

/**
 * Auth UI Controller
 */
const AuthUI = {
  init() {
    // Check URL parameters for action (e.g. ?action=register)
    const urlParams = new URLSearchParams(window.location.search);
    const action = urlParams.get('action');
    
    if (action === 'register') {
      this.switchTab('register');
    }
    
    // Redirection automatique si déjà connecté
    if (window.App.state.currentUser) {
      const isArtisan = window.App.state.currentUser.role === 'artisan';
      window.location.href = isArtisan ? 'dashboard.html' : 'profile.html';
    }
  },

  switchTab(tab) {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const loginBtn = document.getElementById('btn-login-tab');
    const registerBtn = document.getElementById('btn-register-tab');
    
    // Hide errors
    document.getElementById('login-error').classList.remove('visible');
    document.getElementById('register-error').classList.remove('visible');
    
    if (tab === 'login') {
      loginForm.classList.remove('hidden');
      registerForm.classList.add('hidden');
      loginBtn.classList.add('active');
      registerBtn.classList.remove('active');
    } else {
      loginForm.classList.add('hidden');
      registerForm.classList.remove('hidden');
      loginBtn.classList.remove('active');
      registerBtn.classList.add('active');
    }
  },

  async handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorEl = document.getElementById('login-error');
    
    const result = await Auth.login(email, password);
    
    if (result.success) {
      errorEl.classList.remove('visible');
      const user = window.Storage.getCurrentUser();
      window.location.href = user && user.role === 'artisan' ? 'dashboard.html' : 'index.html';
    } else {
      errorEl.textContent = result.message;
      errorEl.classList.add('visible');
    }
  },

  async handleRegister(event) {
    event.preventDefault();
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    
    // Get role from radio buttons
    let role = 'citoyen';
    const roleRadios = document.getElementsByName('reg-role');
    for (let i = 0; i < roleRadios.length; i++) {
      if (roleRadios[i].checked) {
        role = roleRadios[i].value;
        break;
      }
    }
    
    // Mapping requis pour la validation Pydantic (client -> citoyen)
    if (role === 'client') {
      role = 'citoyen';
    }
    
    const errorEl = document.getElementById('register-error');
    
    const result = await Auth.register({ name, email, password, role });
    
    if (result.success) {
      errorEl.classList.remove('visible');
      const user = window.Storage.getCurrentUser();
      window.location.href = user && user.role === 'artisan' ? 'dashboard.html' : 'index.html';
    } else {
      errorEl.textContent = result.message;
      errorEl.classList.add('visible');
    }
  },
  forgotPassword(event) {
    event.preventDefault();
    // Simulate reset password flow
    const email = prompt("Entrez votre adresse email pour réinitialiser votre mot de passe:");
    if (email) {
      alert("Un lien de réinitialisation a été envoyé (simulation).");
    }
  }
};

// Initialize UI when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  AuthUI.init();
});
