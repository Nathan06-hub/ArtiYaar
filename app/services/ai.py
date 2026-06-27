import re

# Dictionnaires de mots-clés de sentiment en français adaptés aux services locaux
POSITIVE_WORDS = {
    "excellent": 3.0,
    "excellente": 3.0,
    "parfait": 3.0,
    "parfaite": 3.0,
    "super": 2.5,
    "génial": 2.5,
    "géniale": 2.5,
    "top": 2.0,
    "bon": 1.5,
    "bonne": 1.5,
    "satisfait": 1.5,
    "satisfaite": 1.5,
    "propre": 1.5,
    "rapide": 1.5,
    "efficace": 2.0,
    "professionnel": 2.0,
    "professionnelle": 2.0,
    "aimable": 1.5,
    "recommande": 2.0,
    "recommandé": 2.0,
    "magnifique": 2.5,
    "adoré": 2.5,
    "adore": 2.5,
    "soigné": 1.5,
    "soignée": 1.5,
    "chaleureux": 1.5,
    "chaleureuse": 1.5,
    "honnête": 2.0,
    "sérieux": 1.5,
    "sérieuse": 1.5,
    "agréable": 1.5,
    "ponctuel": 1.5,
    "ponctuelle": 1.5,
    "sympathique": 1.5,
    "sympa": 1.5,
    "ravie": 2.0,
    "ravi": 2.0,
    "superbe": 2.5,
    "merveilleux": 3.0,
    "merci": 1.5,
    "plaisir": 1.5,
    "soigneux": 1.5,
    "réactif": 1.8,
    "réactive": 1.8,
    "compétent": 2.0,
    "compétente": 2.0,
}

NEGATIVE_WORDS = {
    "mauvais": 2.0,
    "mauvaise": 2.0,
    "mécontent": 1.5,
    "mécontente": 1.5,
    "lent": 1.5,
    "lente": 1.5,
    "cher": 1.5,
    "chère": 1.5,
    "excessif": 2.0,
    "excessive": 2.0,
    "désagréable": 2.0,
    "déçu": 2.0,
    "déçue": 2.0,
    "horrible": 3.0,
    "catastrophe": 3.0,
    "arnaque": 3.0,
    "arnaqué": 3.0,
    "éviter": 2.5,
    "nul": 2.5,
    "nulle": 2.5,
    "médiocre": 2.0,
    "retard": 1.5,
    "grossier": 2.5,
    "grossière": 2.5,
    "impoli": 2.5,
    "impolie": 2.5,
    "saleté": 2.0,
    "bâclé": 2.5,
    "bâclée": 2.5,
    "déplorable": 3.0,
    "incompétent": 3.0,
    "incompétente": 3.0,
    "inacceptable": 3.0,
    "regrette": 1.5,
    "regret": 1.5,
    "pire": 3.0,
    "déception": 2.0,
    "mal": 1.5,
    "problème": 1.0,
    "aucun": 1.0,
    "pas": 0.5,
    "sale": 2.0,
    "mensonge": 2.5,
    "voleur": 3.0,
    "arnaqueurs": 3.0,
    "désastreux": 3.0,
    "désastreuse": 3.0,
}

INTENSIFIERS = {
    "très": 1.5,
    "extrêmement": 2.0,
    "vraiment": 1.3,
    "trop": 1.2,
    "particulièrement": 1.5,
    "absolument": 1.8,
    "si": 1.2,
    "tellement": 1.4,
    "beaucoup": 1.3,
    "fortement": 1.4,
}

NEGATIONS = {"pas", "ne", "plus", "jamais", "rien", "aucun", "aucune", "sans"}


def analyze_sentiment(text: str) -> dict:
    """
    Analyse le sentiment d'un texte en français et propose une note sur 5 étoiles.
    Gère les intensificateurs et les négations courantes.
    """
    if not text or not text.strip():
        return {"score": 0.0, "rating": 3, "sentiment": "neutre", "keywords": []}

    # Nettoyage simple
    text_clean = text.lower()
    # Remplacer les apostrophes, tirets et ponctuations par des espaces
    text_clean = re.sub(r"['’\-\.\,\!\?\(\)]", " ", text_clean)
    words = text_clean.split()

    score = 0.0
    detected_keywords = []

    i = 0
    n = len(words)

    while i < n:
        word = words[i]
        word_score = 0.0
        is_pos = False
        is_neg = False
        matched_word = ""

        if word in POSITIVE_WORDS:
            word_score = POSITIVE_WORDS[word]
            is_pos = True
            matched_word = word
        elif word in NEGATIVE_WORDS:
            word_score = NEGATIVE_WORDS[word]
            is_neg = True
            matched_word = word

        if is_pos or is_neg:
            # Vérifier si des modificateurs précèdent le mot (jusqu'à 2 mots avant)
            multiplier = 1.0
            negated = False

            for offset in [1, 2]:
                if i - offset >= 0:
                    prev_word = words[i - offset]
                    if prev_word in INTENSIFIERS:
                        multiplier *= INTENSIFIERS[prev_word]
                    if prev_word in NEGATIONS:
                        negated = not negated

            contribution = word_score * multiplier
            if is_neg:
                contribution = -contribution

            if negated:
                # Inversion du sentiment si négation détectée
                contribution = -contribution

            score += contribution
            detected_keywords.append(
                {
                    "word": matched_word,
                    "type": (
                        "positive"
                        if (is_pos and not negated) or (is_neg and negated)
                        else "negative"
                    ),
                    "score": round(contribution, 2),
                }
            )

        i += 1

    # Conversion du score en note de 1 à 5 étoiles
    if score <= -3.0:
        rating = 1
        sentiment = "très négatif"
    elif score <= -0.5:
        rating = 2
        sentiment = "négatif"
    elif score < 0.5:
        rating = 3
        sentiment = "neutre"
    elif score < 3.0:
        rating = 4
        sentiment = "positif"
    else:
        rating = 5
        sentiment = "très positif"

    return {
        "score": round(score, 2),
        "rating": rating,
        "sentiment": sentiment,
        "keywords": detected_keywords,
    }
