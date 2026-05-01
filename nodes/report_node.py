import os
import requests
from nodes.state import InfluencerState

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
_MODEL = "anthropic/claude-haiku-4-5"  # fast & cheap on OpenRouter


def _call_openrouter(prompt: str, api_key: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://trustinflu.tn",
        "X-Title": "TrustInflu",
    }
    payload = {
        "model": _MODEL,
        "max_tokens": 200,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = requests.post(_OPENROUTER_URL, json=payload, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def report_node(state: InfluencerState) -> InfluencerState:
    inf = state["influencer"]
    score = state.get("trust_score", 0)
    label = state.get("trust_label", "")
    breakdown = state.get("score_breakdown", {})
    product = state.get("product_description", "")

    api_key = os.environ.get("OPENROUTER_API_KEY", "")

    if api_key:
        prompt = f"""You are an influencer marketing analyst for the Tunisian market.

Influencer: {inf.get('name')} | {inf.get('city')}, {inf.get('country')} | {inf.get('platform')} | {inf.get('niche')}
Followers: {inf.get('followers'):,} | Engagement: {inf.get('engagement_rate')}%
Final Score: {score}/100 ({label})
Score breakdown: Engagement={breakdown.get('engagement')}/25, Ratio={breakdown.get('ratio')}/15, Fake detection={breakdown.get('fake_detect')}/15, Bot detection={breakdown.get('bot_detect')}/10, Consistency={breakdown.get('consistency')}/10, Completeness={breakdown.get('completeness')}/10, Age={breakdown.get('age')}/5, Product fit={breakdown.get('product_match')}/10
Product/Brand: {product if product else 'General campaign'}

Write a 2-sentence recommendation in French for a Tunisian brand. Be direct and specific."""

        try:
            recommendation = _call_openrouter(prompt, api_key)
        except Exception:
            recommendation = _fallback_recommendation(inf, score, label, breakdown)
    else:
        recommendation = _fallback_recommendation(inf, score, label, breakdown)

    return {**state, "recommendation": recommendation}


def _fallback_recommendation(inf, score, label, breakdown):
    name = inf.get("name", "Cet influenceur")
    niche = inf.get("niche", "")
    city = inf.get("city", "")
    er = inf.get("engagement_rate", 0)

    if score >= 80:
        return (f"{name} ({city}) est un influenceur {niche} hautement fiable avec un score de {score}/100. "
                f"Son taux d'engagement de {er}% et son audience authentique en font un excellent choix pour votre campagne.")
    elif score >= 50:
        return (f"{name} présente un profil acceptable avec un score de {score}/100, mais nécessite une vérification supplémentaire. "
                f"Nous recommandons de surveiller l'évolution de son engagement avant d'investir dans une campagne majeure.")
    else:
        return (f"⚠️ {name} présente des signaux suspects avec un score de {score}/100. "
                f"Nous déconseillons une collaboration sans audit approfondi de son audience.")
