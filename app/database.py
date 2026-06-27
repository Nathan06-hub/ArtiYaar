from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Création du moteur SQLAlchemy pour PostgreSQL
engine = create_engine(settings.DATABASE_URL)

# Configuration de la session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base declarative pour les modèles
Base = declarative_base()


# Dépendance FastAPI pour obtenir la session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
