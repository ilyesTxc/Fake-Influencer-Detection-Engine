from typing import TypedDict, Optional


class InfluencerState(TypedDict):
    influencer: dict
    fake_probability: Optional[float]        # account-level fake signal (IGAudit)
    fake_follower_estimate: Optional[float]  # 0.0-1.0 estimated % of bought/ghost followers
    fake_follower_detail: Optional[dict]     # breakdown of signals used
    bot_score: Optional[int]
    product_match_score: Optional[float]
    trust_score: Optional[int]
    trust_label: Optional[str]
    score_breakdown: Optional[dict]
    recommendation: Optional[str]
    product_description: Optional[str]
    comment_sentiment_score: Optional[float]
