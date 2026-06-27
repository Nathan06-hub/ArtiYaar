from datetime import timedelta, datetime
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.auth import create_access_token, get_current_user, verify_password
from app.database import get_db

router = APIRouter(prefix="/api/auth", tags=["Authentification"])

# Rate limiting simple en mémoire pour les tentatives de connexion
login_attempts = defaultdict(list)
MAX_ATTEMPTS = 5
ATTEMPT_WINDOW = 60  # secondes


@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur (artisan ou citoyen)."""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400, detail="Cette adresse email est déjà enregistrée."
        )
    return crud.create_user(db=db, user=user)


@router.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Connexion avec identifiants JSON pour obtenir un jeton d'accès JWT."""
    # Vérifier le rate limiting
    now = datetime.utcnow()
    email = user_credentials.email
    # Nettoyer les anciennes tentatives
    login_attempts[email] = [t for t in login_attempts[email] if (now - t).total_seconds() < ATTEMPT_WINDOW]

    if len(login_attempts[email]) >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Trop de tentatives de connexion. Réessayez dans {ATTEMPT_WINDOW} secondes.",
        )

    user = crud.get_user_by_email(db, email=user_credentials.email)
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        # Enregistrer la tentative échouée
        login_attempts[email].append(now)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Adresse email ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Réinitialiser les tentatives en cas de succès
    login_attempts[email] = []

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "name": user.name,
    }


@router.post("/token", response_model=schemas.Token, include_in_schema=False)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Endpoint masqué compatible avec le bouton 'Authorize' de Swagger UI
    qui utilise le format x-www-form-urlencoded.
    """
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Adresse email ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "name": user.name,
    }


@router.post(
    "/reset-password-request", response_model=schemas.PasswordResetQuestionResponse
)
def reset_password_request(
    request: schemas.PasswordResetRequest, db: Session = Depends(get_db)
):
    """Demande de réinitialisation. Retourne la question de sécurité configurée."""
    user = crud.get_user_by_email(db, email=request.email)
    if not user:
        raise HTTPException(
            status_code=404, detail="Aucun compte n'est associé à cette adresse email."
        )
    return {"email": user.email, "reset_question": user.reset_question}


@router.post("/reset-password")
def reset_password(submit: schemas.PasswordResetSubmit, db: Session = Depends(get_db)):
    """Validation de la réponse de sécurité et modification du mot de passe."""
    user = crud.get_user_by_email(db, email=submit.email)
    if not user:
        raise HTTPException(status_code=404, detail="Aucun compte trouvé.")

    # Vérification de la réponse à la question de sécurité (insensible à la casse, nettoyée)
    answer_clean = submit.reset_answer.strip().lower()
    if not verify_password(answer_clean, user.reset_answer_hashed):
        raise HTTPException(
            status_code=400,
            detail="La réponse à la question de sécurité est incorrecte.",
        )

    # Mise à jour du mot de passe
    crud.update_user_password(db=db, user=user, new_password=submit.new_password)
    return {"message": "Le mot de passe a été réinitialisé avec succès."}


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    """Retourne les détails de l'utilisateur actuellement connecté."""
    return current_user
