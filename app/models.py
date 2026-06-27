from sqlalchemy import (JSON, Boolean, Column, DateTime, Float, ForeignKey,
                        Integer, String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'artisan' ou 'citoyen'
    reset_question = Column(String, nullable=False)
    reset_answer_hashed = Column(String, nullable=False)

    businesses = relationship(
        "Business", back_populates="owner", cascade="all, delete-orphan"
    )


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    phone = Column(String, nullable=False)
    hours = Column(String, nullable=True)
    published = Column(Boolean, default=True, index=True)
    image_urls = Column(
        JSON, nullable=True
    )  # Stocké sous forme de JSON (ex: ["url1", "url2"])

    owner = relationship("User", back_populates="businesses")
    reviews = relationship(
        "Review", back_populates="business", cascade="all, delete-orphan"
    )


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(
        Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    author_name = Column(String, nullable=False)
    comment = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)  # Note calculée par l'IA (1 à 5)
    sentiment_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="reviews")
