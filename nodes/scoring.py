from langgraph.graph import StateGraph, END
from nodes.state import InfluencerState
from nodes.profile_analysis_node import profile_analysis_node
from nodes.bot_detection_node import bot_detection_node
from nodes.post_compliance_node import post_compliance_node
from nodes.trust_score_node import trust_score_node

# Compiled once, reused for every call
_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        g = StateGraph(InfluencerState)
        g.add_node("profile_analysis_node", profile_analysis_node)
        g.add_node("bot_detection_node",    bot_detection_node)
        g.add_node("post_compliance_node",  post_compliance_node)
        g.add_node("trust_score_node",      trust_score_node)
        g.set_entry_point("profile_analysis_node")
        g.add_edge("profile_analysis_node", "bot_detection_node")
        g.add_edge("bot_detection_node",    "post_compliance_node")
        g.add_edge("post_compliance_node",  "trust_score_node")
        g.add_edge("trust_score_node",      END)
        _pipeline = g.compile()
    return _pipeline


def _initial_state(influencer: dict, product_description: str = "") -> InfluencerState:
    return {
        "influencer":              influencer,
        "fake_probability":        None,
        "fake_follower_estimate":  None,
        "fake_follower_detail":    None,
        "bot_score":               None,
        "product_match_score":     None,
        "trust_score":             None,
        "trust_label":             None,
        "score_breakdown":         None,
        "recommendation":          None,
        "product_description":     product_description,
        "comment_sentiment_score": None,
    }


def score_influencer(influencer: dict, product_description: str = "") -> InfluencerState:
    return _get_pipeline().invoke(_initial_state(influencer, product_description))
