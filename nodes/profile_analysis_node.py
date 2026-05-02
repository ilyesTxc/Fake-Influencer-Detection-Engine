import joblib
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
    username  = inf.get("name", "").replace(" ", "_").lower()
    fullname  = inf.get("name", "")
    followers = inf.get("followers", 1)
    following = inf.get("following", 1)

    profile_pic         = int(inf.get("has_profile_pic", 1))
    nums_ratio_username = sum(c.isdigit() for c in username) / max(len(username), 1)
    fullname_words      = len(fullname.split())
    nums_ratio_fullname = sum(c.isdigit() for c in fullname) / max(len(fullname), 1)
    name_eq_username    = 1 if fullname.replace(" ", "_").lower() == username else 0
    bio_length          = int(inf.get("bio_length", 0))
    external_url        = int(inf.get("has_external_url", 0))
    private             = int(inf.get("is_private", 0))
    posts               = int(inf.get("posts_count", 0))

    return [profile_pic, nums_ratio_username, fullname_words, nums_ratio_fullname,
            name_eq_username, bio_length, external_url, private, posts, followers, following]


# Expected engagement rates per tier (Tunisian/Maghreb market benchmarks)
_ER_BENCHMARKS = {
    "nano":  3.5,   # < 10K
    "micro": 2.5,   # 10K – 100K
    "macro": 1.5,   # 100K – 500K
    "mega":  1.0,   # 500K+
}

def _get_tier(followers: int) -> str:
    if followers < 10_000:   return "nano"
    if followers < 100_000:  return "micro"
    if followers < 500_000:  return "macro"
    return "mega"


def _estimate_fake_followers(inf: dict, igaudit_score: float) -> tuple:
    """
    Estimate the proportion of fake / bought / ghost followers (0.0 – 1.0).

    Three independent signals:

    1. Engagement-rate gap  (60% weight)
       Industry standard used by HypeAuditor, Modash, etc.
       If real ER << expected ER for the follower tier, the gap is filled
       by ghost/inactive/bought followers.

    2. IGAudit profile score (25% weight)
       A suspicious-looking profile tends to have more fake followers.

    3. Follower/following anomaly (15% weight)
       Extreme ratios that don't match organic growth patterns.
    """
    followers  = max(inf.get("followers", 1), 1)
    following  = max(inf.get("following", 1), 1)
    er         = inf.get("engagement_rate", 0.0)
    posts      = inf.get("posts_count", 0)
    tier       = _get_tier(followers)
    expected   = _ER_BENCHMARKS[tier]

    signals = {}

    # ── Signal 1: Engagement-rate gap ───────────────────────────────────────
    if er <= 0:
        er_signal = 0.90          # zero engagement → almost certainly all fake
    elif er >= expected:
        er_signal = 0.05          # at or above benchmark → baseline ghost followers
    else:
        # Linear: ER at 0 → 90%, ER at expected → 5%
        ratio     = er / expected
        er_signal = 0.90 - ratio * 0.85
    signals["engagement_gap"] = round(er_signal, 3)

    # ── Signal 2: IGAudit profile suspiciousness ─────────────────────────────
    # igaudit_score is probability the ACCOUNT ITSELF is fake.
    # A suspicious account is more likely to have bought followers too.
    igaudit_signal = igaudit_score * 0.6   # dampen: profile fake ≠ all followers fake
    signals["igaudit_profile"] = round(igaudit_signal, 3)

    # ── Signal 3: Follower / following ratio anomaly ─────────────────────────
    ratio = followers / following
    if ratio > 200:
        # Way too many followers for the following count — likely purchased
        ratio_signal = min(0.6, (ratio - 200) / 800)
    elif ratio < 0.1:
        # Following 10x more than followers — suspicious mass-follow behaviour
        ratio_signal = 0.4
    else:
        ratio_signal = 0.0
    signals["ratio_anomaly"] = round(ratio_signal, 3)

    # ── Weighted combination ─────────────────────────────────────────────────
    fake_est = (
        er_signal      * 0.60 +
        igaudit_signal * 0.25 +
        ratio_signal   * 0.15
    )
    fake_est = round(min(0.95, max(0.02, fake_est)), 3)

    detail = {
        "estimated_pct":   round(fake_est * 100, 1),
        "tier":            tier,
        "expected_er":     expected,
        "actual_er":       er,
        "signals":         signals,
    }
    return fake_est, detail


def profile_analysis_node(state: InfluencerState) -> InfluencerState:
    inf = state["influencer"]

    # ── IGAudit model: is the account itself fake? ───────────────────────────
    try:
        model    = _load_model()
        features = build_igaudit_features(inf)
        proba    = model.predict_proba([features])[0]
        fake_prob = float(proba[1]) if len(proba) > 1 else 0.0
    except Exception:
        er         = inf.get("engagement_rate", 3.0)
        followers  = inf.get("followers", 1)
        following  = inf.get("following", 1)
        ratio      = following / max(followers, 1)
        fake_prob  = 0.0
        if ratio > 0.5:   fake_prob += 0.3
        if er > 15:       fake_prob += 0.4
        if er < 0.5:      fake_prob += 0.4
        fake_prob = min(fake_prob, 0.99)

    # ── Fake follower estimator ──────────────────────────────────────────────
    fake_follower_estimate, fake_follower_detail = _estimate_fake_followers(inf, fake_prob)

    return {
        **state,
        "fake_probability":       round(fake_prob, 3),
        "fake_follower_estimate": fake_follower_estimate,
        "fake_follower_detail":   fake_follower_detail,
    }
