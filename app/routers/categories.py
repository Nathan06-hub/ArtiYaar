from fastapi import APIRouter

from app.schemas import VALID_CATEGORIES

router = APIRouter(prefix="/api/categories", tags=["Catégories"])


@router.get("", response_model=list[str])
def get_categories():
    """Retourne la liste des catégories de métiers disponibles."""
    return VALID_CATEGORIES
