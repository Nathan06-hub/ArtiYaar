import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./dev.db")

from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import Base, SessionLocal, engine


def seed():
    # Recreate tables (drop if exists)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    # Create an artisan user
    artisan = crud.create_user(
        db=db,
        user=schemas.UserCreate(
            name="Alice Artisan",
            email="alice@example.com",
            password="Secret123!",
            role="artisan",
            reset_question="Quel est le nom de votre premier animal?",
            reset_answer="Mimi",
        ),
    )

    # Create a business for the artisan
    crud.create_business(
        db=db,
        business=schemas.BusinessCreate(
            name="Boulangerie du Coin",
            category="Boulangerie",
            description="Pain artisanal fait maison",
            address="12 rue du Marché, 75001 Paris",
            latitude=48.8566,
            longitude=2.3522,
            phone="+33 1 23 45 67 89",
            hours="08:00-19:00",
            image_urls=None,
        ),
        owner_id=artisan.id,
    )
    db.close()
    print("Database seeded with sample data")


if __name__ == "__main__":
    seed()
