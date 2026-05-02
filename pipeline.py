from langgraph.graph import StateGraph, END
from nodes.state import InfluencerState
from nodes.profile_analysis_node import profile_analysis_node
from nodes.bot_detection_node import bot_detection_node
from nodes.post_compliance_node import post_compliance_node
from nodes.trust_score_node import trust_score_node
from nodes.report_node import report_node

def build_pipeline():
    graph = StateGraph(InfluencerState)

    graph.add_node("profile_analysis_node", profile_analysis_node)
    graph.add_node("bot_detection_node", bot_detection_node)
    graph.add_node("post_compliance_node", post_compliance_node)
    graph.add_node("trust_score_node", trust_score_node)
    graph.add_node("report_node", report_node)

    graph.set_entry_point("profile_analysis_node")
    graph.add_edge("profile_analysis_node", "bot_detection_node")
    graph.add_edge("bot_detection_node", "post_compliance_node")
    graph.add_edge("post_compliance_node", "trust_score_node")
    graph.add_edge("trust_score_node", "report_node")
    graph.add_edge("report_node", END)

    return graph.compile()

def run_pipeline(influencer: dict, product_description: str = "") -> InfluencerState:
    pipeline = build_pipeline()
    initial_state: InfluencerState = {
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
    result = pipeline.invoke(initial_state)
    return result

