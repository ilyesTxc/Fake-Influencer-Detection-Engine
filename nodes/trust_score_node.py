from nodes.state import InfluencerState


def get_tier(followers: int) -> str:
    if followers < 10000:
        return "nano"
    elif followers < 100000:
        return "micro"
    elif followers < 500000:
        return "macro"
    return "mega"


def engagement_score(er: float, tier: str) -> float:
    """
    Tunisian/Maghreb market benchmarks.
    Average real ER on Instagram: nano ~3-5%, micro ~2-3%, macro ~1-2%, mega ~0.5-1.5%.
    'ideal' = solidly good. 'min' = acceptable floor. 'suspicious' = bot-like inflated.
    """
    benchmarks = {
        "nano":  {"min": 1.0, "ideal": 3.5, "suspicious": 35.0},
        "micro": {"min": 0.8, "ideal": 2.5, "suspicious": 25.0},
        "macro": {"min": 0.5, "ideal": 1.5, "suspicious": 20.0},
        "mega":  {"min": 0.3, "ideal": 1.0, "suspicious": 15.0},
    }
    b = benchmarks[tier]
    if er < 0.1:
        return 0.05                         # completely dead account
    if er >= b["suspicious"]:
        # Extremely inflated — likely fake engagement
        return max(0.15, 1.0 - (er - b["suspicious"]) / b["suspicious"])
    if er >= b["ideal"]:
        return 1.0                          # at or above ideal → full score
    if er >= b["min"]:
        # Linear ramp from 0.5 at min up to 1.0 at ideal
        return 0.5 + 0.5 * (er - b["min"]) / (b["ideal"] - b["min"])
    # Below min but not dead — partial score (never below 0.15)
    return max(0.15, 0.5 * (er / b["min"]))


def trust_score_node(state: InfluencerState) -> InfluencerState:
    inf = state["influencer"]
    followers  = max(inf.get("followers", 1), 1)
    following  = max(inf.get("following", 1), 1)
    er         = inf.get("engagement_rate", 3.0)
    posts      = inf.get("posts_count", 0)
    age_months = max(inf.get("account_age_months", 1), 1)
    has_pic    = inf.get("has_profile_pic", 1)
    bio_len    = inf.get("bio_length", 0)
    has_url    = inf.get("has_external_url", 0)

    bot_score = state.get("bot_score", 3)
    try:
        bot_score = int(round(float(bot_score)))
    except (TypeError, ValueError):
        bot_score = 3
    bot_score = max(1, min(5, bot_score))

    product_match_score = state.get("product_match_score", 0.5)
    try:
        product_match_score = float(product_match_score)
    except (TypeError, ValueError):
        product_match_score = 0.5
    product_match_score = max(0.0, min(1.0, product_match_score))

    # Comment sentiment from scraper (None when not scraped)
    comment_sentiment = state.get("comment_sentiment_score")
    if comment_sentiment is None:
        # Try to pull it from the influencer's scraped data
        sent_data = inf.get("_comment_sentiment")
        if sent_data and sent_data.get("total", 0) > 0:
            comment_sentiment = sent_data.get("sentiment_score")

    tier = get_tier(followers)

    # Signal 1: Engagement rate (25 pts)
    sig1 = engagement_score(er, tier) * 25

    # Signal 2: Followers / following ratio (15 pts)
    ratio = followers / following
    if ratio >= 3.0:
        sig2 = 15.0
    elif ratio >= 1.0:
        sig2 = 7.5 + 7.5 * (ratio - 1.0) / 2.0
    elif ratio >= 0.3:
        sig2 = 7.5 * (ratio / 1.0)
    else:
        sig2 = 1.5

    # Signal 3: Fake follower estimate — combined ER-gap + IGAudit (15 pts)
    fake_follower_est = state.get("fake_follower_estimate")
    if fake_follower_est is None:
        fake_follower_est = state.get("fake_probability", 0.2)
    sig3 = (1.0 - float(fake_follower_est)) * 15

    # Signal 4: Bot detection score (10 pts)
    sig4 = (5.0 - bot_score) / 4.0 * 10

    # Signal 5: Post consistency (10 pts)
    posts_per_month = posts / age_months
    if posts_per_month >= 8:
        sig5 = 10.0
    elif posts_per_month >= 4:
        sig5 = 7.0
    elif posts_per_month >= 1:
        sig5 = 4.0
    else:
        sig5 = 1.0

    # Signal 6: Profile completeness (10 pts)
    completeness = 0
    if has_pic:
        completeness += 4
    if bio_len > 20:
        completeness += 3
    if has_url:
        completeness += 3
    sig6 = float(completeness)

    # Signal 7: Product fit (10 pts)
    sig8 = product_match_score * 10

    raw = sig1 + sig2 + sig3 + sig4 + sig5 + sig6 + sig8

    # ── Signal 9: Comment sentiment modifier ──────────────────────────────────
    # Only applied when we have real scraped comments.
    # sentiment_score 0-1:  ≥0.70 → bonus, ≤0.30 → penalty.
    sig9 = None
    sentiment_modifier = 0.0
    if comment_sentiment is not None:
        s = float(comment_sentiment)
        if s >= 0.70:
            # Very positive community → up to +5 pts bonus
            sentiment_modifier = (s - 0.70) / 0.30 * 5.0
        elif s <= 0.30:
            # Toxic / very negative → up to -10 pts penalty
            sentiment_modifier = -(0.30 - s) / 0.30 * 10.0
        # Between 0.30 and 0.70 → no change (neutral zone)
        raw += sentiment_modifier
        sig9 = round(sentiment_modifier, 1)

    trust_score = max(0, min(100, int(round(raw))))

    if trust_score >= 80:
        label = "🟢 Certifié"
    elif trust_score >= 50:
        label = "🟡 À surveiller"
    else:
        label = "🔴 Suspect"

    breakdown = {
        "engagement":    round(sig1, 1),
        "ratio":         round(sig2, 1),
        "fake_detect":   round(sig3, 1),
        "bot_detect":    round(sig4, 1),
        "consistency":   round(sig5, 1),
        "completeness":  round(sig6, 1),
        "product_match": round(sig8, 1),
        "sentiment":     sig9,           # None for mock data, float for scraped
    }

    return {
        **state,
        "trust_score":           trust_score,
        "trust_label":           label,
        "score_breakdown":       breakdown,
        "comment_sentiment_score": comment_sentiment,
    }
