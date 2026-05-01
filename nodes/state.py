from typing import TypedDict, Optional

class InfluencerState(TypedDict):
    influencer: dict
    fake_probability: Optional[float]
    bot_score: Optional[int]
    product_match_score: Optional[float]
    trust_score: Optional[int]
    trust_label: Optional[str]
    score_breakdown: Optional[dict]
    recommendation: Optional[str]
    product_description: Optional[str]
