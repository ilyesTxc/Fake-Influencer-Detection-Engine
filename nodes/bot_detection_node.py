import joblib
import numpy as np
import os
from nodes.state import InfluencerState

_model = None

def _load_model():
    global _model
    if _model is None:
        path = os.path.join(os.path.dirname(__file__), "..", "models", "tiktokclf.pkl")
        _model = joblib.load(path)
    return _model


def build_instagram_features(inf: dict) -> list:
    followers  = inf.get("followers", 1000)
    following  = inf.get("following", 500)
    posts      = inf.get("posts_count", 100)
    er         = inf.get("engagement_rate", 3.0)
    has_pic    = inf.get("has_profile_pic", 1)
    bio_len    = inf.get("bio_length", 50)

    avg_likes    = followers * er / 100
    avg_comments = avg_likes * 0.05
    avg_shares   = avg_likes * 0.02
    avg_hashtags = 5.0
    avg_linked   = 1.0
    avg_views    = avg_likes * 10
    has_bio      = 1 if bio_len > 0 else 0

    return [
        has_pic,
        following,
        followers,
        has_bio,
        avg_likes * posts,
        posts,
        avg_hashtags,
        avg_comments,
        avg_shares,
        avg_likes,
        avg_linked,
        avg_views,
    ]


def bot_detection_node(state: InfluencerState) -> InfluencerState:
    inf = state["influencer"]

    try:
        model    = _load_model()
        features = build_instagram_features(inf)

        n_features = model.n_features_in_
        features = features[:n_features]
        while len(features) < n_features:
            features.append(0.0)

        prediction = model.predict([features])[0]
        try:
            proba    = model.predict_proba([features])[0]
            bot_prob = float(proba[1]) if len(proba) > 1 else float(prediction)
        except Exception:
            bot_prob = float(prediction)

        bot_score = int(round(bot_prob * 4)) + 1

    except Exception:
        followers = inf.get("followers", 1000)
        following = inf.get("following", 500)
        er        = inf.get("engagement_rate", 3.0)
        ratio     = following / max(followers, 1)
        if ratio > 0.5 or er > 15 or er < 0.5:
            bot_score = 4
        elif ratio > 0.3:
            bot_score = 3
        else:
            bot_score = 2

    return {**state, "bot_score": int(bot_score)}
