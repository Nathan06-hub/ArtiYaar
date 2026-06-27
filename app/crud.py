from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_password_hash
from app.services.ai import analyze_sentiment

# --- CRUD UTILISATEURS ---


def get_user(db: Session, user_id: int):
    """Récupère un utilisateur par son ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    """Récupère un utilisateur par son adresse email."""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    """Crée un nouvel utilisateur en hachant le mot de passe et la réponse de sécurité."""
    hashed_password = get_password_hash(user.password)
    # On hache la réponse en minuscule pour rendre la vérification insensible à la casse
    hashed_answer = get_password_hash(user.reset_answer.strip().lower())

    db_user = models.User(
        name=user.name,
        email=user.email,
        role=user.role,
        hashed_password=hashed_password,
        reset_question=user.reset_question,
        reset_answer_hashed=hashed_answer,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_password(db: Session, user: models.User, new_password: str):
    """Met à jour le mot de passe d'un utilisateur."""
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user


# --- CRUD COMMERCES ---


def get_business(db: Session, business_id: int):
    """Récupère un commerce par son ID."""
    return db.query(models.Business).filter(models.Business.id == business_id).first()


def get_artisan_businesses(db: Session, owner_id: int):
    """Récupère la liste de tous les commerces créés par un artisan spécifique."""
    return db.query(models.Business).filter(models.Business.owner_id == owner_id).all()


def get_published_businesses(
    db: Session, query: Optional[str] = None, category: Optional[str] = None
):
    """Récupère les commerces publiés avec filtres optionnels par nom/description et catégorie."""
    q = db.query(models.Business).filter(models.Business.published == True)

    if query:
        search_filter = f"%{query}%"
        q = q.filter(
            (models.Business.name.ilike(search_filter))
            | (models.Business.description.ilike(search_filter))
        )
    if category:
        q = q.filter(models.Business.category.ilike(category))

    return q.all()


def create_business(db: Session, business: schemas.BusinessCreate, owner_id: int):
    """Crée un nouveau commerce pour un artisan."""
    db_business = models.Business(
        owner_id=owner_id,
        name=business.name,
        category=business.category,
        description=business.description,
        address=business.address,
        latitude=business.latitude,
        longitude=business.longitude,
        phone=business.phone,
        hours=business.hours,
        image_urls=business.image_urls,
    )
    db.add(db_business)
    db.commit()
    db.refresh(db_business)
    return db_business


def update_business(
    db: Session, db_business: models.Business, business_update: schemas.BusinessUpdate
):
    """Met à jour les informations d'un commerce."""
    update_data = business_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_business, key, value)
    db.commit()
    db.refresh(db_business)
    return db_business


def delete_business(db: Session, business_id: int):
    """Supprime un commerce de la base de données."""
    db_business = db.query(models.Business).filter(models.Business.id == business_id).first()
    if db_business:
        db.delete(db_business)
        db.commit()
    return db_business


def get_business_stats(db: Session, business_id: int):
    """Calcule la note moyenne et le nombre de commentaires pour un commerce."""
    stats = (
        db.query(
            func.avg(models.Review.rating).label("average"),
            func.count(models.Review.id).label("count"),
        )
        .filter(models.Review.business_id == business_id)
        .first()
    )

    return {
        "average_rating": (
            round(float(stats.average), 1) if stats.average is not None else 0.0
        ),
        "reviews_count": stats.count or 0,
    }


def get_platform_stats(db: Session):
    """Calcule les statistiques globales de la plateforme."""
    total_businesses = db.query(func.count(models.Business.id)).scalar()
    published_businesses = db.query(func.count(models.Business.id)).filter(models.Business.published == True).scalar()
    total_reviews = db.query(func.count(models.Review.id)).scalar()
    
    avg_rating = db.query(func.avg(models.Review.rating)).scalar()
    avg_rating = round(float(avg_rating), 1) if avg_rating is not None else 0.0
    
    return {
        "total_businesses": total_businesses or 0,
        "published_businesses": published_businesses or 0,
        "total_reviews": total_reviews or 0,
        "average_rating": avg_rating,
    }


# --- CRUD AVIS (REVIEWS) ---


def create_review(db: Session, review: schemas.ReviewCreate, business_id: int):
    """Crée un commentaire et utilise l'IA pour attribuer automatiquement la note sur 5 étoiles."""
    # Analyse de sentiment avec le moteur d'IA en français
    analysis = analyze_sentiment(review.comment)

    db_review = models.Review(
        business_id=business_id,
        author_name=review.author_name,
        comment=review.comment,
        rating=analysis["rating"],
        sentiment_score=analysis["score"],
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review, analysis
