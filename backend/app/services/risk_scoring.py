from app.models import InstanceFactorScore, CollectionInstance

# Seuils de classification — plus une table, codés en dur comme demandé
CLASSIFICATION_BANDS = [
    (0, 33.99, "Low", "green"),
    (34, 66.99, "Medium", "orange"),
    (67, 100, "High", "red"),
]


class IncompleteScoringDataError(Exception):
    """Levée quand une instance n'a pas de note pour chacun des 7 facteurs."""
    pass


def classify_score(normalized_score):
    for low, high, label, color in CLASSIFICATION_BANDS:
        if low <= normalized_score <= high:
            return {"label": label, "color": color}

    # Fallback de sécurité : ne devrait jamais arriver avec des bandes
    # correctement contiguës, mais évite un crash 500 si jamais un score
    # tombe dans un trou entre deux bandes.
    if normalized_score < 0:
        return {"label": "Low", "color": "green"}
    return {"label": "High", "color": "red"}


def compute_instance_score(id_instance):
    """Retourne le score normalisé (0-100) d'une instance de collecte, ou lève
    IncompleteScoringDataError si les 7 facteurs ne sont pas tous notés."""
    scores = InstanceFactorScore.query.filter_by(id_instance=id_instance).all()

    if len(scores) != 7:
        raise IncompleteScoringDataError(
            f"Instance {id_instance} must have ratings for all 7 risk factors."
        )

    impact_ratings = [s.rating for s in scores if s.factor.group.name == "impact"]
    likelihood_ratings = [s.rating for s in scores if s.factor.group.name == "likelihood"]

    if len(impact_ratings) != 4 or len(likelihood_ratings) != 3:
        raise IncompleteScoringDataError(
            f"Instance {id_instance} must have 4 impact and 3 likelihood ratings."
        )

    impact = sum(impact_ratings) / len(impact_ratings)
    likelihood = sum(likelihood_ratings) / len(likelihood_ratings)

    score = (impact * likelihood / 16) * 100
    return round(score, 2)


def compute_device_score(id_device):
    instances = CollectionInstance.query.filter_by(id_device=id_device).all()

    if len(instances) == 0:
        return 0.0, {"label": "No Risk", "color": "gray"}

    scores = []
    for instance in instances:
        try:
            scores.append(compute_instance_score(instance.id_instance))
        except IncompleteScoringDataError:
            continue

    if len(scores) == 0:
        return 0.0, {"label": "No Risk", "color": "gray"}

    max_score = max(scores)
    return max_score, classify_score(max_score)