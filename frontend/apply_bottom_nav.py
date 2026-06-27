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
bottom_nav_pattern = re.compile(r'<nav class="mobile-bottom-nav">.*?</nav>\s*</body>', re.DOTALL)

for f in files:
    path = os.path.join(r"c:\Users\oumaima\OneDrive\Bureau\Hackathon", f)
    if not os.path.exists(path):
        continue
    
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        
    def get_style(page):
        return 'style="font-weight: 700; color: var(--primary-color);"' if page in f else 'style="font-weight: 500;"'
        
    def get_active(page):
        return 'active' if page in f else ''

    new_header = f"""<header class="header">
    <div class="container" style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
      <a href="index.html" class="logo">
        <img src="img/logo.jpg" alt="Artiyaar Logo" style="height: 100px; object-fit: contain;">
      </a>
      
      <nav class="main-nav desktop-nav" style="display: flex; gap: 2rem; align-items: center;">
        <a href="index.html" class="nav-link" {get_style('index.html')}>Accueil</a>
        <a href="services.html" class="nav-link" {get_style('services.html')}>Services</a>
        <a href="avis.html" class="nav-link" {get_style('avis.html')}>Avis</a>
        <a href="contact.html" class="nav-link" {get_style('contact.html')}>Contact</a>
      </nav>

      <div class="nav-links desktop-nav" id="auth-links" style="display: flex; gap: 1rem; align-items: center;">
        <!-- Injected by app.js -->
      </div>
    </div>
  </header>"""

    content = header_pattern.sub(new_header, content)
    
    bottom_nav = f"""<nav class="mobile-bottom-nav">
    <a href="index.html" class="bottom-nav-item {get_active('index.html')}">
      <i class="fas fa-home"></i>
      <span>Accueil</span>
    </a>
    <a href="services.html" class="bottom-nav-item {get_active('services.html')}">
      <i class="fas fa-search"></i>
      <span>Services</span>
    </a>
    <a href="avis.html" class="bottom-nav-item {get_active('avis.html')}">
      <i class="fas fa-star"></i>
      <span>Avis</span>
    </a>
    <a href="contact.html" class="bottom-nav-item {get_active('contact.html')}">
      <i class="fas fa-envelope"></i>
      <span>Contact</span>
    </a>
    <a href="login.html" class="bottom-nav-item {get_active('dashboard.html')} {get_active('login.html')} {get_active('artisan-profile.html')}" id="mobile-auth-link">
      <i class="fas fa-user"></i>
      <span>Profil</span>
    </a>
  </nav>
</body>"""

    if '<nav class="mobile-bottom-nav">' in content:
        content = bottom_nav_pattern.sub(bottom_nav, content)
    else:
        content = content.replace("</body>", bottom_nav)
    
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Updated {f} with bottom nav")
