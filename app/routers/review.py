from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/api/businesses",
    tags=["Commentaires & Avis (IA)"],
)


@router.post(
    "/{business_id}/reviews", status_code=status.HTTP_201_CREATED
)
def create_business_review(
    business_id: int,
    review: schemas.ReviewCreate,
    db: Session = Depends(get_db),
):
    """Add a review to a business, analysing it with AI.

    Returns both flat fields and a nested ``ai_analysis`` structure required by the tests.
    """
    db_business = crud.get_business(db=db, business_id=business_id)
    if not db_business:
        raise HTTPException(
            status_code=404, detail="Commerce introuvable."
        )

    if not db_business.published:
        raise HTTPException(
            status_code=400,
            detail="Impossible d'ajouter un commentaire sur un commerce non publié.",
        )

    db_review, analysis = crud.create_review(
        db=db, review=review, business_id=business_id
    )

    return {
        "id": db_review.id,
        "business_id": db_review.business_id,
        "author_name": db_review.author_name,
        "comment": db_review.comment,
        "rating": analysis["rating"],
        "sentiment_score": analysis["score"],
        "sentiment_label": analysis["sentiment"],
        "detected_keywords": analysis["keywords"],
        "ai_analysis": {
            "rating_assigned": analysis["rating"],
            "sentiment_score": analysis["score"],
            "sentiment_label": analysis["sentiment"],
            "detected_keywords": analysis["keywords"]
        },
        "created_at": str(db_review.created_at),
    }


@router.get(
    "/{business_id}/reviews",
    response_model=List[schemas.ReviewResponse],
)
def get_business_reviews(
    business_id: int,
    db: Session = Depends(get_db),
):
    db_business = crud.get_business(db=db, business_id=business_id)
    if not db_business:
        raise HTTPException(status_code=404, detail="Commerce introuvable.")
    return (
        db.query(models.Review)
        .filter(models.Review.business_id == business_id)
        .all()
    )
