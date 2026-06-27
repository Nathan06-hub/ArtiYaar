from datetime import datetime
from typing import List, Optional
import re

from pydantic import BaseModel, EmailStr, Field, field_validator

# --- CATÉGORIES PRÉDÉFINIES ---
VALID_CATEGORIES = [
    "Boulangerie", "Boucherie", "Couture", "Coiffure", "Mécanique",
    "Menuiserie", "Soudure", "Plomberie", "Électricité", "Maçonnerie",
    "Peinture", "Réparation", "Cordonnerie", "Tailleur", "Forgeron",
    "Tapisserie", "Maroquinerie", "Poterie", "Joaillerie", "Autre"
]

# --- SCHÉMAS D'AUTHENTIFICATION ---


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Nom complet (2-50 caractères)")
    email: EmailStr
    role: str = Field(..., description="Le rôle doit être 'artisan' ou 'citoyen'")

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['artisan', 'citoyen']:
            raise ValueError('Le rôle doit être "artisan" ou "citoyen"')
        return v


class UserCreate(UserBase):
    password: str
    reset_question: str
    reset_answer: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not re.search(r'[a-z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not re.search(r'[0-9]', v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        return v


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[int] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetQuestionResponse(BaseModel):
    email: EmailStr
    reset_question: str


class PasswordResetSubmit(BaseModel):
    email: EmailStr
    reset_answer: str
    new_password: str


# --- SCHÉMAS DES AVIS ---


class ReviewBase(BaseModel):
    author_name: str
    comment: str


class ReviewCreate(ReviewBase):
    """Modèle de création d'un avis.
    Exemple :
        {
            "author_name": "Alice",
            "comment": "Service excellent, très sympathique !"
        }
    """
    pass

    class Config:
        schema_extra = {
            "example": {
                "author_name": "Alice",
                "comment": "Service excellent, très sympathique !"
            }
        }


class ReviewResponse(ReviewBase):
    id: int
    business_id: int
    rating: int
    sentiment_score: float
    created_at: datetime

    class Config:
        from_attributes = True


# --- SCHÉMAS DES COMMERCES ---


class BusinessBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Nom du commerce (2-100 caractères)")
    category: str
    description: Optional[str] = Field(None, max_length=500, description="Description du commerce (max 500 caractères)")
    address: str = Field(..., min_length=5, max_length=200, description="Adresse (5-200 caractères)")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude entre -90 et 90")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude entre -180 et 180")
    phone: str
    hours: Optional[str] = Field(None, max_length=100, description="Horaires (max 100 caractères)")
    image_urls: Optional[List[str]] = None

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if v not in VALID_CATEGORIES:
            raise ValueError(f'Catégorie invalide. Catégories valides: {", ".join(VALID_CATEGORIES)}')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        # Regex pour numéros internationaux (accepte formats: +221771234567, +33 1 23 45 67 89, 0771234567)
        phone_pattern = r'^\+?[0-9\s\-\(\)]{7,20}$'
        if not re.match(phone_pattern, v.replace(' ', '')):
            raise ValueError('Format de téléphone invalide')
        return v

    @field_validator('image_urls')
    @classmethod
    def validate_image_urls(cls, v):
        if v is not None:
            if len(v) > 3:
                raise ValueError('Maximum 3 URLs d\'images autorisées')
            # Valider que chaque URL est une URL valide
            url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            for url in v:
                if not re.match(url_pattern, url):
                    raise ValueError(f'URL d\'image invalide: {url}')
        return v


class BusinessCreate(BusinessBase):
    """Modèle de création d'un commerce.
    Exemple :
        {
            "name": "Boulangerie Le Bon Pain",
            "category": "Boulangerie",
            "description": "Boulangerie traditionnelle",
            "address": "10 rue du Pain, 75001 Paris",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "phone": "+33 1 23 45 67 89",
            "hours": "09:00-18:00",
            "image_urls": ["https://example.com/image1.jpg"]
        }
    """
    pass

    class Config:
        schema_extra = {
            "example": {
                "name": "Boulangerie Le Bon Pain",
                "category": "Boulangerie",
                "description": "Boulangerie traditionnelle",
                "address": "10 rue du Pain, 75001 Paris",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "phone": "+33 1 23 45 67 89",
                "hours": "09:00-18:00",
                "image_urls": ["https://example.com/image1.jpg"]
            }
        }



class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    hours: Optional[str] = None
    image_urls: Optional[List[str]] = None
    published: Optional[bool] = None


class BusinessResponse(BusinessBase):
    id: int
    owner_id: int
    published: bool
    average_rating: float = 0.0
    reviews_count: int = 0
    distance: Optional[float] = (
        None  # Distance en km si l'utilisateur fournit ses coordonnées
    )
    reviews: List[ReviewResponse] = []

    class Config:
        from_attributes = True


class BusinessWhatsAppLink(BaseModel):
    whatsapp_link: str
    message: str
