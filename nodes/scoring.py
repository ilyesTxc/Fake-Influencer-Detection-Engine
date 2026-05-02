from nodes.state import InfluencerState
from nodes.profile_analysis_node import profile_analysis_node
from nodes.bot_detection_node import bot_detection_node
from nodes.post_compliance_node import post_compliance_node
from nodes.trust_score_node import trust_score_node


def _initial_state(influencer: dict, product_description: str = "") -> InfluencerState:
    return {
        "influencer": influencer,
        "fake_probability": None,
        "fake_follower_estimate": None,
        "fake_follower_detail": None,
        "bot_score": None,
        "product_match_score": None,
        "trust_score": None,
        "trust_label": None,
        "score_breakdown": None,
        "recommendation": None,
        "product_description": product_description,
        "comment_sentiment_score": None,
    }


def score_influencer(influencer: dict, product_description: str = "") -> InfluencerState:
    state = _initial_state(influencer, product_description)
    state = profile_analysis_node(state)
    state = bot_detection_node(state)
    state = post_compliance_node(state)
    return trust_score_node(state)