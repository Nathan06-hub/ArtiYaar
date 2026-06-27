import os
import re

files = [
    "artisan-profile.html",
    "avis.html",
    "contact.html",
    "dashboard.html",
    "index.html",
    "login.html",
    "services.html"
]

header_pattern = re.compile(r'<header class="header">.*?</header>', re.DOTALL)

for f in files:
    path = os.path.join(r"c:\Users\oumaima\OneDrive\Bureau\Hackathon", f)
    if not os.path.exists(path):
        continue
    
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        
    def get_style(page):
        return 'style="font-weight: 700; color: var(--primary-color);"' if page in f else 'style="font-weight: 500;"'

    new_header = f"""<header class="header">
    <div class="container" style="display: flex; justify-content: space-between; align-items: center; width: 100%; position: relative;">
      <a href="index.html" class="logo">
        <img src="img/logo.jpg" alt="Artiyaar Logo" style="height: 100px; object-fit: contain;">
      </a>
      
      <button class="mobile-menu-toggle" aria-label="Menu" id="mobile-menu-btn">
        <i class="fas fa-bars"></i>
      </button>

      <div class="nav-wrapper" id="nav-wrapper">
        <nav class="main-nav" style="display: flex; gap: 2rem; align-items: center;">
          <a href="index.html" class="nav-link" {get_style('index.html')}>Accueil</a>
          <a href="services.html" class="nav-link" {get_style('services.html')}>Services</a>
          <a href="avis.html" class="nav-link" {get_style('avis.html')}>Avis</a>
          <a href="contact.html" class="nav-link" {get_style('contact.html')}>Contact</a>
        </nav>

        <div class="nav-links" id="auth-links" style="display: flex; gap: 1rem; align-items: center;">
          <!-- Injected by app.js -->
        </div>
      </div>
    </div>
  </header>"""

    new_content = header_pattern.sub(new_header, content)
    
    with open(path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print(f"Added hamburger to {f}")
