import os
from nodes.state import InfluencerState

NICHE_KEYWORDS = {
    "Food & Resto": ["food", "restaurant", "eat", "cuisine", "meal", "drink", "recipe", "cooking", "nourriture", "manger", "recette", "repas"],
    "Cuisine TN": ["tunisian", "couscous", "brik", "lablabi", "merguez", "tajine", "tunisie", "food", "cuisine", "طبخ", "تونسي", "وصفات"],
    "Fashion": ["fashion", "style", "outfit", "clothing", "mode", "vêtement", "tendance", "look", "wear", "dress"],
    "Beauty": ["beauty", "makeup", "skincare", "cosmetic", "beauté", "maquillage", "soin", "peau", "lip", "foundation"],
    "Sport": ["sport", "fitness", "workout", "football", "gym", "training", "muscle", "health", "football", "coach"],
    "Music": ["music", "song", "rap", "artist", "musique", "chanson", "chanteur", "beat", "album", "concert"],
    "Travel": ["travel", "voyage", "tourism", "trip", "destination", "hotel", "beach", "tourisme", "djerba", "sousse"],
    "Tech & Gaming": ["tech", "technology", "gaming", "game", "software", "app", "digital", "smartphone", "pc", "review"],
}

BRAND_NICHE_MAP = {
    "Tunisie Telecom": ["Tech & Gaming", "Music", "Sport"],
    "Pepsi Tunisia": ["Food & Resto", "Sport", "Music"],
    "Poulina Group": ["Food & Resto", "Cuisine TN"],
    "Monoprix Tunisia": ["Food & Resto", "Fashion", "Beauty"],
    "Topnet": ["Tech & Gaming", "Music"],
    "BIAT": ["Sport", "Fashion", "Tech & Gaming"],
    "Délice": ["Food & Resto", "Cuisine TN", "Beauty"],
    "Office du Tourisme Tunisien": ["Travel", "Food & Resto", "Cuisine TN"],
}

def compute_match_score(niche: str, product_description: str) -> float:
    if not product_description:
        return 0.5

    desc_lower = product_description.lower()
    keywords = NICHE_KEYWORDS.get(niche, [])
    if not keywords:
        return 0.3

    hits = sum(1 for kw in keywords if kw in desc_lower)
    score = min(hits / max(len(keywords) * 0.4, 1), 1.0)

    # Bonus if the niche name itself appears
    if niche.lower().split("&")[0].strip() in desc_lower:
        score = min(score + 0.3, 1.0)

    return round(score, 3)

def post_compliance_node(state: InfluencerState) -> InfluencerState:
    inf = state["influencer"]
    niche = inf.get("niche", "")
    product_description = state.get("product_description", "")
    match_score = compute_match_score(niche, product_description)
    return {**state, "product_match_score": match_score}
