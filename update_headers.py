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
        
    # Extract the original nav links to preserve their bold/color state
    match = header_pattern.search(content)
    if not match:
        continue
    
    header_content = match.group(0)
    
    # We need to preserve the nav links
    nav_match = re.search(r'<nav class="main-nav".*?>(.*?)</nav>', header_content, re.DOTALL)
    nav_links = nav_match.group(1) if nav_match else ""
    
    # Clean up the inline styles from nav links
    nav_links_cleaned = re.sub(r'style="[^"]*"', '', nav_links)
    
    # Wait, some nav links have font-weight: 700; color: var(--primary-color);
    # To keep the active state logic, I can just use a class 'active' instead.
    # Let's see if we can identify which one is active.
    
    new_header = f"""<header class="header">
    <div class="container header-container">
      <a href="index.html" class="logo">
        <img src="img/logo.jpg" alt="Artiyaar Logo">
      </a>
      
      <button class="mobile-menu-toggle" aria-label="Menu" id="mobile-menu-btn">
        <i class="fas fa-bars"></i>
      </button>

      <div class="nav-wrapper" id="nav-wrapper">
        <nav class="main-nav">
          <a href="index.html" class="nav-link{' active' if 'index.html' in f else ''}">Accueil</a>
          <a href="services.html" class="nav-link{' active' if 'services.html' in f else ''}">Services</a>
          <a href="avis.html" class="nav-link{' active' if 'avis.html' in f else ''}">Avis</a>
          <a href="contact.html" class="nav-link{' active' if 'contact.html' in f else ''}">Contact</a>
        </nav>

        <div class="nav-links" id="auth-links">
          <!-- Injected by app.js -->
        </div>
      </div>
    </div>
  </header>"""

    new_content = header_pattern.sub(new_header, content)
    
    with open(path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print(f"Updated {f}")
