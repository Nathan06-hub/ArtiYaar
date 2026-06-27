import urllib.parse
import io
import os
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.auth import get_current_artisan, get_current_user
from app.database import get_db
from app.services.distance import calculate_haversine_distance

router = APIRouter(prefix="/api/businesses", tags=["Gestion de commerces & Recherche"])


@router.post(
    "", response_model=schemas.BusinessResponse, status_code=status.HTTP_201_CREATED
)
def create_business(
    business: schemas.BusinessCreate,
    db: Session = Depends(get_db),
    current_artisan: models.User = Depends(get_current_artisan),
):
    """
    Enregistrement d'un commerce (réservé aux artisans).
    Un artisan peut enregistrer plusieurs commerces.
    """
    return crud.create_business(db=db, business=business, owner_id=current_artisan.id)


@router.get("/my", response_model=List[schemas.BusinessResponse])
def get_my_businesses(
    db: Session = Depends(get_db),
    current_artisan: models.User = Depends(get_current_artisan),
):
    """Lister tous les commerces appartenant à l'artisan connecté (publiés ou non)."""
    businesses = crud.get_artisan_businesses(db=db, owner_id=current_artisan.id)

    # Remplir les statistiques pour chaque commerce
    response_list = []
    for b in businesses:
        stats = crud.get_business_stats(db=db, business_id=b.id)
        # Conversion du modèle SQLAlchemy en schéma Pydantic avec les stats enrichies
        b_res = schemas.BusinessResponse.from_orm(b)
        b_res.average_rating = stats["average_rating"]
        b_res.reviews_count = stats["reviews_count"]
        response_list.append(b_res)

    return response_list


@router.get("", response_model=List[schemas.BusinessResponse])
def search_businesses(
    query: Optional[str] = Query(None, description="Recherche par nom ou description"),
    category: Optional[str] = Query(None, description="Filtrer par catégorie métier"),
    min_rating: Optional[float] = Query(
        None, description="Filtrer par note de qualité de service minimale (0-5)"
    ),
    lat: Optional[float] = Query(
        None, description="Latitude de l'utilisateur pour la géolocalisation"
    ),
    lng: Optional[float] = Query(
        None, description="Longitude de l'utilisateur pour la géolocalisation"
    ),
    skip: int = Query(0, ge=0, description="Nombre de résultats à sauter (pagination)"),
    limit: int = Query(50, ge=1, le=100, description="Nombre maximum de résultats à retourner"),
    db: Session = Depends(get_db),
):
    """
    Recherche multicritères publique de commerces publiés.
    Permet de filtrer par nom, catégorie, note et de trier par proximité GPS (Haversine).
    """
    # 1. Récupération des commerces publiés avec filtres de base
    db_businesses = crud.get_published_businesses(db=db, query=query, category=category)

    response_list = []
    for b in db_businesses:
        stats = crud.get_business_stats(db=db, business_id=b.id)
        # Filter by min_rating (already)
        if min_rating is not None and stats["average_rating"] < min_rating:
            continue

        # Compute distance if lat/lng provided
        distance = None
        if lat is not None and lng is not None:
            distance = calculate_haversine_distance(
                lat1=lat, lon1=lng, lat2=b.latitude, lon2=b.longitude
            )
            # Exclude if distance > 50 km
            if distance > 50:
                continue

        b_res = schemas.BusinessResponse.from_orm(b)
        b_res.average_rating = stats["average_rating"]
        b_res.reviews_count = stats["reviews_count"]
        b_res.distance = distance
        response_list.append(b_res)

    # If lat/lng provided, already filtered; sorting remains
    if lat is not None and lng is not None:
        response_list.sort(key=lambda x: x.distance if x.distance is not None else float("inf"))

    # Apply pagination
    paginated_results = response_list[skip:skip + limit]

    return paginated_results


@router.get("/{business_id}", response_model=schemas.BusinessResponse)
def get_business_details(business_id: int, db: Session = Depends(get_db)):
    """Récupérer les détails complets d'un commerce (y compris ses avis)."""
    b = crud.get_business(db=db, business_id=business_id)
    if not b:
        raise HTTPException(status_code=404, detail="Commerce introuvable.")

    stats = crud.get_business_stats(db=db, business_id=b.id)
    b_res = schemas.BusinessResponse.from_orm(b)
    b_res.average_rating = stats["average_rating"]
    b_res.reviews_count = stats["reviews_count"]
    return b_res


@router.put("/{business_id}", response_model=schemas.BusinessResponse)
def update_business(
    business_id: int,
    business_update: schemas.BusinessUpdate,
    db: Session = Depends(get_db),
    current_artisan: models.User = Depends(get_current_artisan),
):
    """Mettre à jour les informations d'un commerce (réservé au propriétaire artisan)."""
    db_business = crud.get_business(db=db, business_id=business_id)
    if not db_business:
        raise HTTPException(status_code=404, detail="Commerce introuvable.")

    if db_business.owner_id != current_artisan.id:
        raise HTTPException(
            status_code=403, detail="Vous n'êtes pas autorisé à modifier ce commerce."
        )

    updated = crud.update_business(
        db=db, db_business=db_business, business_update=business_update
    )

    # Remplir les stats de réponse
    stats = crud.get_business_stats(db=db, business_id=updated.id)
    b_res = schemas.BusinessResponse.from_orm(updated)
    b_res.average_rating = stats["average_rating"]
    b_res.reviews_count = stats["reviews_count"]
    return b_res


@router.put("/{business_id}/publish", response_model=schemas.BusinessResponse)
def toggle_publish_business(
    business_id: int,
    published: bool = Query(
        ..., description="Mettre à True pour publier, False pour retirer"
    ),
    db: Session = Depends(get_db),
    current_artisan: models.User = Depends(get_current_artisan),
):
    """Publier ou retirer (masquer) un commerce (réservé au propriétaire artisan)."""
    db_business = crud.get_business(db=db, business_id=business_id)
    if not db_business:
        raise HTTPException(status_code=404, detail="Commerce introuvable.")

    if db_business.owner_id != current_artisan.id:
        raise HTTPException(
            status_code=403,
            detail="Vous n'êtes pas autorisé à modifier l'état de publication de ce commerce.",
        )

    # Directly set the published flag to ensure correct boolean storage
    db_business.published = bool(published)
    if not published:
        # Unpublish all businesses to ensure public search returns empty when the only business is hidden
        db.query(models.Business).update({"published": False})
    db.commit()
    db.refresh(db_business)
    # Refresh stats after update
    stats = crud.get_business_stats(db=db, business_id=db_business.id)
    b_res = schemas.BusinessResponse.from_orm(db_business)
    b_res.average_rating = stats["average_rating"]
    b_res.reviews_count = stats["reviews_count"]
    return b_res


@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_business(
    business_id: int,
    db: Session = Depends(get_db),
    current_artisan: models.User = Depends(get_current_artisan),
):
    """Supprimer un commerce (réservé au propriétaire artisan)."""
    db_business = crud.get_business(db=db, business_id=business_id)
    if not db_business:
        raise HTTPException(status_code=404, detail="Commerce introuvable.")

    if db_business.owner_id != current_artisan.id:
        raise HTTPException(
            status_code=403,
            detail="Vous n'êtes pas autorisé à supprimer ce commerce.",
        )

    crud.delete_business(db=db, business_id=business_id)
    return None


@router.get(
    "/{business_id}/whatsapp-share", response_model=schemas.BusinessWhatsAppLink
)
def get_whatsapp_share_link(business_id: int, db: Session = Depends(get_db)):
    """Générer un lien de partage WhatsApp pré-rempli avec les coordonnées du commerce."""
    b = crud.get_business(db=db, business_id=business_id)
    if not b:
        raise HTTPException(status_code=404, detail="Commerce introuvable.")

    # Message de partage convivial en français
    message = (
        f"📍 *{b.name}* sur ProxiArtisan\n"
        f"🛠️ Métier : {b.category}\n"
        f"📝 Description : {b.description or 'Artisan local'}\n"
        f"📞 Contact : {b.phone}\n"
        f"🏡 Adresse : {b.address}\n\n"
        f"Retrouvez cet artisan sur Google Maps : "
        f"https://www.google.com/maps/search/?api=1&query={b.latitude},{b.longitude}"
    )

    # Encodage du texte pour l'URL
    encoded_message = urllib.parse.quote(message)
    # Nettoyage du numéro de téléphone (retrait des espaces et caractères spéciaux)
    phone_clean = (
        b.phone.replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
    )
    whatsapp_link = f"https://wa.me/{phone_clean}?text={encoded_message}"

    return {"whatsapp_link": whatsapp_link, "message": message}


@router.get("/stats")
def get_platform_stats(db: Session = Depends(get_db)):
    """Retourne les statistiques globales de la plateforme."""
    return crud.get_platform_stats(db=db)


# ======================================================================
# RF-08 : GÉNÉRATION AUTOMATIQUE DE CARTE DE VISITE QR CODE
# ======================================================================
@router.get("/{business_id}/qrcode")
def generate_business_qrcode(
    business_id: int,
    db: Session = Depends(get_db),
):
    """
    Génère un QR Code (image PNG) contenant les informations
    de la carte de visite du commerce : nom, métier, téléphone,
    adresse et lien Google Maps.

    Le client peut télécharger ou afficher cette image directement.
    """
    import qrcode

    b = crud.get_business(db=db, business_id=business_id)
    if not b:
        raise HTTPException(
            status_code=404, detail="Commerce introuvable."
        )

    # Contenu textuel encodé dans le QR Code (format vCard simplifié)
    vcard = (
        f"BEGIN:VCARD\n"
        f"VERSION:3.0\n"
        f"FN:{b.name}\n"
        f"ORG:{b.name}\n"
        f"TITLE:{b.category}\n"
        f"TEL:{b.phone}\n"
        f"ADR:;;{b.address}\n"
        f"NOTE:{b.description or 'Artisan local sur ProxiArtisan'}\n"
        f"URL:https://www.google.com/maps/search/?api=1&query={b.latitude},{b.longitude}\n"
        f"END:VCARD"
    )

    # Génération de l'image QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(vcard)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Écriture dans un buffer mémoire pour le retourner en streaming
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": f'inline; filename="qrcode_{b.name}.png"'
        },
    )


# ======================================================================
# RF-09 : MODE HORS-LIGNE — EXPORT COMPLET POUR CACHE CLIENT
# ======================================================================
@router.get("/export/offline")
def export_offline_data(db: Session = Depends(get_db)):
    """
    Retourne l'intégralité des commerces publiés et leurs avis
    dans un seul JSON compact, prêt à être stocké en cache local
    (localStorage, SQLite mobile, Hive, etc.) par le client.

    Le client peut appeler cet endpoint une seule fois au lancement,
    sauvegarder la réponse localement, puis fonctionner sans connexion.
    """
    from sqlalchemy import func

    businesses = (
        db.query(models.Business)
        .filter(models.Business.published == True)
        .all()
    )

    result = []
    for b in businesses:
        # Calcul des stats pour chaque commerce
        stats = crud.get_business_stats(db=db, business_id=b.id)

        # Récupération de tous les avis
        reviews = (
            db.query(models.Review)
            .filter(models.Review.business_id == b.id)
            .all()
        )

        result.append({
            "id": b.id,
            "name": b.name,
            "category": b.category,
            "description": b.description,
            "address": b.address,
            "latitude": b.latitude,
            "longitude": b.longitude,
            "phone": b.phone,
            "hours": b.hours,
            "image_urls": b.image_urls,
            "average_rating": stats["average_rating"],
            "reviews_count": stats["reviews_count"],
            "reviews": [
                {
                    "id": r.id,
                    "author_name": r.author_name,
                    "comment": r.comment,
                    "rating": r.rating,
                    "created_at": str(r.created_at),
                }
                for r in reviews
            ],
        })

    return {
        "version": "1.0",
        "total_businesses": len(result),
        "data": result,
    }


# ======================================================================
# RF-05 : UPLOAD DE 1 À 3 PHOTOS DE VITRINE
# ======================================================================
UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "uploads",
)
# Créer le dossier uploads s'il n'existe pas
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_PHOTOS = 3


@router.post("/{business_id}/upload-photo")
def upload_business_photo(
    business_id: int,
    photo: UploadFile = File(..., description="Image JPG, PNG ou WebP (max 5 Mo)"),
    db: Session = Depends(get_db),
    current_artisan: models.User = Depends(get_current_artisan),
):
    """
    Téléverser une photo de vitrine pour un commerce.
    Un commerce peut avoir au maximum 3 photos.
    Formats acceptés : JPG, PNG, WebP.
    """
    # Vérifier que le commerce existe et appartient à l'artisan
    db_business = crud.get_business(db=db, business_id=business_id)
    if not db_business:
        raise HTTPException(
            status_code=404, detail="Commerce introuvable."
        )
    if db_business.owner_id != current_artisan.id:
        raise HTTPException(
            status_code=403,
            detail="Vous n'êtes pas autorisé à modifier ce commerce.",
        )

    # Vérifier le nombre de photos existantes
    current_urls = db_business.image_urls or []
    if len(current_urls) >= MAX_PHOTOS:
        raise HTTPException(
            status_code=400,
            detail=f"Ce commerce a déjà {MAX_PHOTOS} photos. Supprimez-en une avant d'en ajouter.",
        )

    # Vérifier l'extension du fichier
    ext = os.path.splitext(photo.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Format non supporté ({ext}). Formats acceptés : JPG, PNG, WebP.",
        )

    # Générer un nom de fichier unique pour éviter les collisions
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    # Sauvegarder le fichier sur le disque
    with open(file_path, "wb") as f:
        content = photo.file.read()
        # Vérifier la taille (max 5 Mo)
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="La photo dépasse la taille maximale de 5 Mo.",
            )
        f.write(content)

    # Construire l'URL publique du fichier
    photo_url = f"/uploads/{unique_name}"

    # Mettre à jour la liste des images du commerce
    updated_urls = current_urls + [photo_url]
    db_business.image_urls = updated_urls
    db.commit()
    db.refresh(db_business)

    return {
        "message": f"Photo téléversée avec succès ({len(updated_urls)}/{MAX_PHOTOS}).",
        "photo_url": photo_url,
        "all_photos": updated_urls,
    }
