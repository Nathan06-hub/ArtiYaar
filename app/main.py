from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.config import settings
from app.database import Base, engine
from app.routers import auth, business, categories, review


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

# Initialisation automatique de la base de données PostgreSQL/SQLite
# Crée les tables si elles n'existent pas encore
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ProxiArtisan API",
    description="API REST d'annuaire géolocalisé pour artisans de proximité, incluant authentification, géolocalisation et notation IA automatique des avis.",
    version="1.0.0",
)

# Configuration CORS pour permettre le raccordement facile d'un frontend
# En production, définir BACKEND_CORS_ORIGINS dans le .env avec les domaines autorisés
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ajouter les headers de sécurité HTTP
app.add_middleware(SecurityHeadersMiddleware)

# Enregistrement des routes de l'API
app.include_router(auth.router)
app.include_router(business.router)
app.include_router(categories.router)
app.include_router(review.router)


@app.get("/", tags=["Général"])
def read_root():
    """Vérification de l'état du serveur API."""
    return {
        "name": "ProxiArtisan Backend API",
        "status": "running",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }
