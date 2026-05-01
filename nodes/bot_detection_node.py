import joblib
import numpy as np
import os
from nodes.state import InfluencerState

_twitter_model = None
_tiktok_model = None

def _load_twitter():
    global _twitter_model
    if _twitter_model is None:
        path = os.path.join(os.path.dirname(__file__), "..", "models", "twitterclf.pkl")
        _twitter_model = joblib.load(path)
    return _twitter_model

def _load_tiktok():
    global _tiktok_model
    if _tiktok_model is None:
        path = os.path.join(os.path.dirname(__file__), "..", "models", "tiktokclf.pkl")
        _tiktok_model = joblib.load(path)
    return _tiktok_model

def build_twitter_features(inf: dict) -> list:
    followers = inf.get("followers", 1000)
    following = inf.get("following", 500)
    posts = inf.get("posts_count", 100)
    er = inf.get("engagement_rate", 3.0)
    age = inf.get("account_age_months", 24)

    statuses = posts
    date_joined = max(age, 1)
    most_recent_post = 7
    favourites = int(followers * er / 100 * 0.5)
    lists = max(int(followers / 5000), 0)
    tweets_this_week = max(int(posts / (age * 4)), 1)
    retweet = 0.3
    retweeted_count = int(posts * 0.2)
    username_score = 0.8
    avg_tweets_by_day = max(tweets_this_week / 7, 0.1)
    engagement_rate = er / 100

    return [statuses, date_joined, most_recent_post, following, followers,
            favourites, lists, tweets_this_week, retweet, retweeted_count,
            username_score, avg_tweets_by_day, engagement_rate]

def build_tiktok_features(inf: dict) -> list:
    followers = inf.get("followers", 1000)
    following = inf.get("following", 500)
    posts = inf.get("posts_count", 100)
    er = inf.get("engagement_rate", 3.0)
    has_pic = inf.get("has_profile_pic", 1)
    bio_len = inf.get("bio_length", 50)

    has_profile_pic = has_pic
    avg_likes = followers * er / 100
    avg_comments = avg_likes * 0.05
    avg_shares = avg_likes * 0.02
    avg_hashtags = 5.0
    avg_linked = 1.0
    avg_views = avg_likes * 10
    has_bio = 1 if bio_len > 0 else 0

    return [has_profile_pic, following, followers, has_bio,
            avg_likes * posts, posts, avg_hashtags, avg_comments,
            avg_shares, avg_likes, avg_linked, avg_views]

def score_to_bot_probability(raw_score) -> float:
    # raw_score is 1-5 from model or class label 0/1
    if isinstance(raw_score, (list, np.ndarray)):
        raw_score = raw_score[0]
    if raw_score in [0, 1]:
        return float(raw_score)
    return (raw_score - 1) / 4.0

def bot_detection_node(state: InfluencerState) -> InfluencerState:
    inf = state["influencer"]
    platform = inf.get("platform", "Instagram").lower()

    try:
        if platform in ["twitter", "x"]:
            model = _load_twitter()
            features = build_twitter_features(inf)
        else:
            model = _load_tiktok()
            features = build_tiktok_features(inf)

        n_features = model.n_features_in_
        features = features[:n_features]
        while len(features) < n_features:
            features.append(0.0)

        prediction = model.predict([features])[0]
        try:
            proba = model.predict_proba([features])[0]
            bot_prob = float(proba[1]) if len(proba) > 1 else float(prediction)
        except Exception:
            bot_prob = float(prediction)

        bot_score = int(round(bot_prob * 4)) + 1
    except Exception:
        followers = inf.get("followers", 1000)
        following = inf.get("following", 500)
        er = inf.get("engagement_rate", 3.0)
        ratio = following / max(followers, 1)
        if ratio > 0.5 or er > 15 or er < 0.5:
            bot_score = 4
        elif ratio > 0.3:
            bot_score = 3
        else:
            bot_score = 2

    return {**state, "bot_score": int(bot_score)}
