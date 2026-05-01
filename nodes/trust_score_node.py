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
    """Returns 0.0-1.0 based on Tunisian market benchmarks."""
    benchmarks = {
        "nano":  {"min": 3.0, "ideal": 6.0, "max": 15.0},
        "micro": {"min": 2.5, "ideal": 5.0, "max": 12.0},
        "macro": {"min": 1.5, "ideal": 3.5, "max": 10.0},
        "mega":  {"min": 1.0, "ideal": 2.5, "max": 8.0},
    }
    b = benchmarks[tier]
    if er < 0.5:
        return 0.05
    if er > b["max"]:
        # Suspiciously high — penalize
        return max(0.1, 1.0 - (er - b["max"]) / b["max"])
    if er >= b["ideal"]:
        return 1.0
    if er >= b["min"]:
        return 0.5 + 0.5 * (er - b["min"]) / (b["ideal"] - b["min"])
    return 0.2 + 0.3 * (er / b["min"])

def trust_score_node(state: InfluencerState) -> InfluencerState:
    inf = state["influencer"]
    followers = max(inf.get("followers", 1), 1)
    following = max(inf.get("following", 1), 1)
    er = inf.get("engagement_rate", 3.0)
    posts = inf.get("posts_count", 0)
    age_months = max(inf.get("account_age_months", 1), 1)
    has_pic = inf.get("has_profile_pic", 1)
    bio_len = inf.get("bio_length", 0)
    has_url = inf.get("has_external_url", 0)
    bot_score = state.get("bot_score", 3)
    product_match_score = state.get("product_match_score", 0.5)

    try:
        bot_score = int(round(float(bot_score)))
    except (TypeError, ValueError):
        bot_score = 3
    bot_score = max(1, min(5, bot_score))

    try:
        product_match_score = float(product_match_score)
    except (TypeError, ValueError):
        product_match_score = 0.5
    product_match_score = max(0.0, min(1.0, product_match_score))

    tier = get_tier(followers)

    # Signal 1: Engagement rate (25pts)
    sig1 = engagement_score(er, tier) * 25

    # Signal 2: Followers/following ratio (15pts)
    ratio = followers / following
    if ratio >= 3.0:
        sig2 = 15.0
    elif ratio >= 1.0:
        sig2 = 7.5 + 7.5 * (ratio - 1.0) / 2.0
    elif ratio >= 0.3:
        sig2 = 7.5 * (ratio / 1.0)
    else:
        sig2 = 1.5

    # Signal 3: Fake follower estimate from igaudit model (15pts)
    fake_prob = state.get("fake_probability", 0.2)
    sig3 = (1.0 - fake_prob) * 15

    # Signal 4: Bot detection score (10pts)
    sig4 = (5.0 - bot_score) / 4.0 * 10

    # Signal 5: Post consistency (10pts)
    posts_per_month = posts / age_months
    if posts_per_month >= 8:
        sig5 = 10.0
    elif posts_per_month >= 4:
        sig5 = 7.0
    elif posts_per_month >= 1:
        sig5 = 4.0
    else:
        sig5 = 1.0

    # Signal 6: Profile completeness (10pts)
    completeness = 0
    if has_pic:
        completeness += 4
    if bio_len > 20:
        completeness += 3
    if has_url:
        completeness += 3
    sig6 = float(completeness)

    # Signal 7: Account age (5pts)
    if age_months >= 24:
        sig7 = 5.0
    elif age_months >= 12:
        sig7 = 3.5
    elif age_months >= 6:
        sig7 = 2.0
    elif age_months >= 3:
        sig7 = 1.0
    else:
        sig7 = 0.0

    # Signal 8: Product fit (10pts)
    sig8 = product_match_score * 10

    raw = sig1 + sig2 + sig3 + sig4 + sig5 + sig6 + sig7 + sig8
    trust_score = max(0, min(100, int(round(raw))))

    if trust_score >= 80:
        label = "🟢 Certifié"
    elif trust_score >= 50:
        label = "🟡 À surveiller"
    else:
        label = "🔴 Suspect"

    breakdown = {
        "engagement": round(sig1, 1),
        "ratio":      round(sig2, 1),
        "fake_detect": round(sig3, 1),
        "bot_detect": round(sig4, 1),
        "consistency": round(sig5, 1),
        "completeness": round(sig6, 1),
        "age":         round(sig7, 1),
        "product_match": round(sig8, 1),
    }

    return {**state, "trust_score": trust_score, "trust_label": label, "score_breakdown": breakdown}
