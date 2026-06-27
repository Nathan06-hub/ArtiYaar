/**
 * Auth Module
 * Handles authentication logic (simulated with localStorage)
 */
const Auth = {
  /**
   * Register a new user
   * @param {Object} userData - {name, email, password}
   */
  register(userData) {
    const users = window.Storage.getUsers();
    
    // Check if email already exists
    if (users.find(u => u.email === userData.email)) {
      return { success: false, message: "Cet email est déjà utilisé." };
    }
    
    const newUser = {
      id: 'user_' + window.App.generateId(),
      name: userData.name,
      email: userData.email,
      // In a real app, never store passwords in plain text!
      // This is a hackathon simulation
      password: userData.password, 
      role: userData.role || 'client', 
      createdAt: new Date().toISOString()
    };
    
    users.push(newUser);
    window.Storage.saveUsers(users);
    
    // Auto-login after registration
    window.Storage.setCurrentUser({
      id: newUser.id,
      name: newUser.name,
      email: newUser.email,
      role: newUser.role
    });
    
    return { success: true, user: newUser };
  },

  /**
   * Login user
   * @param {string} email 
   * @param {string} password 
   */
  login(email, password) {
    const users = window.Storage.getUsers();
    const user = users.find(u => u.email === email && u.password === password);
    
    if (user) {
      window.Storage.setCurrentUser({
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role
      });
      return { success: true, user };
    }
    
    return { success: false, message: "Identifiants incorrects." };
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
    
    // Redirect if already logged in
    if (window.App.state.currentUser) {
      window.location.href = 'dashboard.html';
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

  handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorEl = document.getElementById('login-error');
    
    const result = Auth.login(email, password);
    
    if (result.success) {
      errorEl.classList.remove('visible');
      const user = window.Storage.getCurrentUser();
      window.location.href = user && user.role === 'artisan' ? 'dashboard.html' : 'index.html';
    } else {
      errorEl.textContent = result.message;
      errorEl.classList.add('visible');
    }
  },

  handleRegister(event) {
    event.preventDefault();
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    
    // Get role from radio buttons
    let role = 'client';
    const roleRadios = document.getElementsByName('reg-role');
    for (let i = 0; i < roleRadios.length; i++) {
      if (roleRadios[i].checked) {
        role = roleRadios[i].value;
        break;
      }
    }
    
    const errorEl = document.getElementById('register-error');
    
    const result = Auth.register({ name, email, password, role });
    
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
