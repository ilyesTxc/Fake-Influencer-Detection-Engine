import joblib
import numpy as np
import os
from nodes.state import InfluencerState

_model = None

def _load_model():
    global _model
    if _model is None:
        path = os.path.join(os.path.dirname(__file__), "..", "models", "igaudit_clf.pkl")
        _model = joblib.load(path)
    return _model

def build_igaudit_features(inf: dict) -> list:
    username = inf.get("name", "").replace(" ", "_").lower()
    fullname = inf.get("name", "")
    followers = inf.get("followers", 1)
    following = inf.get("following", 1)

    profile_pic = int(inf.get("has_profile_pic", 1))
    nums_ratio_username = sum(c.isdigit() for c in username) / max(len(username), 1)
    fullname_words = len(fullname.split())
    nums_ratio_fullname = sum(c.isdigit() for c in fullname) / max(len(fullname), 1)
    name_eq_username = 1 if fullname.replace(" ", "_").lower() == username else 0
    bio_length = int(inf.get("bio_length", 0))
    external_url = int(inf.get("has_external_url", 0))
    private = int(inf.get("is_private", 0))
    posts = int(inf.get("posts_count", 0))

    return [profile_pic, nums_ratio_username, fullname_words, nums_ratio_fullname,
            name_eq_username, bio_length, external_url, private, posts, followers, following]

def profile_analysis_node(state: InfluencerState) -> InfluencerState:
    inf = state["influencer"]
    try:
        model = _load_model()
        features = build_igaudit_features(inf)
        proba = model.predict_proba([features])[0]
        fake_prob = float(proba[1]) if len(proba) > 1 else 0.0
    except Exception:
        # Fallback: estimate from engagement rate
        er = inf.get("engagement_rate", 3.0)
        followers = inf.get("followers", 1)
        following = inf.get("following", 1)
        ratio = following / max(followers, 1)
        fake_prob = 0.0
        if ratio > 0.5:
            fake_prob += 0.3
        if er > 15:
            fake_prob += 0.4
        if er < 0.5:
            fake_prob += 0.4
        fake_prob = min(fake_prob, 0.99)

    return {**state, "fake_probability": round(fake_prob, 3)}
