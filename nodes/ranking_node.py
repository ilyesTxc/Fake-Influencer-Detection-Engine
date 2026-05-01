from typing import List
from nodes.state import InfluencerState

def rank_influencers(results: List[InfluencerState]) -> List[InfluencerState]:
    return sorted(results, key=lambda x: x.get("trust_score", 0), reverse=True)
