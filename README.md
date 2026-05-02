# TrustInflu 🇹🇳

> **AI-powered influencer trust scoring for the Maghreb market.**  
> Help Tunisian brands vet influencers before they sign a deal — not after.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45-red?logo=streamlit&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.3-blueviolet)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.6-orange?logo=scikit-learn&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

---

## The Problem

The maghreb influencer market is growing fast, but brand safety tools built for Western markets don't account for Tunisian/Arabic content, local slang, or Maghreb engagement benchmarks. Brands routinely pay for fake reach and don't find out until after the campaign flops.

TrustInflu is a single-platform solution that scores any influencer's authenticity from 0 to 100 using four ML models, a LangGraph pipeline, and market-calibrated benchmarks — with a French-language UI built for Tunisian marketers.

---

## Features

| Feature | Description |
|---|---|
| **Trust Score 0–100** | 8-signal composite score calibrated to Maghreb ER benchmarks |
| **Fake follower estimation** | ER-gap + IGAudit model + ratio anomaly (3-signal weighted blend) |
| **Bot detection** | ML classifier trained on Instagram/TikTok behaviour patterns |
| **Ad transparency** | 6-layer sponsored-post detector (hashtags, captions, collab tags, Arabic CTA phrases, prices) |
| **Comment sentiment** | Keyword classifier across French / English / Arabic / Tunisian dialect |
| **Live Instagram scraping** | Instaloader-based real-time profile scraper with session auth |
| **Brand Match** | Rank influencers by product fit for 8 Tunisian brands |
| **Score tracking** | Trust score history curve per username over time |
| **AI recommendation** | Grok (via OpenRouter) generates a 2-sentence French recommendation |

---

## LangGraph Pipeline

Every influencer analysis runs through a 5-node directed graph:

```
influencer scraper
      │
      ▼
┌─────────────────────┐
│  profile_analysis   │  IGAudit sklearn model → fake_probability
│       _node         │  ER-gap + ratio → fake_follower_estimate (0–1)
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   bot_detection     │  TikTok/Instagram sklearn classifier → bot_score (1–5)
│       _node         │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  post_compliance    │  Niche × product keyword matching → product_match_score
│       _node         │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   trust_score       │  8-signal weighted sum → trust_score (0–100)
│       _node         │  + comment sentiment modifier (±10 pts, scraped data only)
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│    report_node      │  Grok via OpenRouter → French recommendation
│  (AI button only)   │  Fallback: rule-based French text (no API key needed)
└─────────────────────┘
```

`score_influencer()` runs nodes 1–4 only (fast, no LLM).  
The **"Générer l'analyse IA"** button in the Audit page triggers the full 5-node graph.

---

## Trust Score Signals

| Signal | Max pts | Method |
|---|---|---|
| Engagement rate | 25 | Tier-calibrated benchmarks (nano/micro/macro/mega) |
| Followers/following ratio | 15 | Organic growth curve |
| Fake follower estimate | 15 | ER-gap (60%) + IGAudit (25%) + ratio anomaly (15%) |
| Bot detection | 10 | ML classifier |
| Post consistency | 10 | Posts/month  |
| Profile completeness | 10 | Pic + bio + external URL |
| Product fit | 10 | Niche × product description keyword overlap |
| Comment sentiment | ±10 | Only applied when live comments are scraped |

**Score labels:** `≥ 80` → Certifié ✅ &nbsp;|&nbsp; `50–79` → À surveiller ⚠️ &nbsp;|&nbsp; `< 50` → Suspect ❌

---

## Tech Stack

- **Frontend:** Streamlit (single-page, session-state navigation)
- **AI orchestration:** LangGraph `StateGraph`
- **ML models:** scikit-learn (IGAudit fake-account classifier, bot detector)
- **LLM:** Claude Haiku 4.5 via [OpenRouter](https://openrouter.ai/)
- **Scraping:** Instaloader (with session cookie auth)
- **Charts:** Plotly (radar, donut, bar, time-series)
- **NLP:** Keyword-based sentiment (French / English / Arabic / Tunisian dialect)

---

## Project Structure

```
TrustInflu/
├── app.py                        # Streamlit app — all 5 pages
├── pipeline.py                   # LangGraph graph builder + run_pipeline()
├── nodes/
│   ├── state.py                  # InfluencerState TypedDict
│   ├── profile_analysis_node.py  # Fake follower estimator (IGAudit + ER-gap)
│   ├── bot_detection_node.py     # Bot classifier
│   ├── post_compliance_node.py   # Product–niche keyword matching
│   ├── trust_score_node.py       # Composite 0–100 scorer
│   ├── report_node.py            # Claude AI recommendation (OpenRouter)
│   ├── instagram_scraper.py      # Live Instagram scraper + ad + sentiment detection
│   ├── history.py                # Trust score history persistence
│   └── scoring.py                # score_influencer() — fast ML-only entry point
├── models/
│   ├── igaudit_clf.pkl           # Fake-account classifier (trained on IGAudit dataset)
│   └── tiktokclf.pkl             # Bot classifier
├── data/
│   ├── influencers.csv           # Seed dataset — 30 Maghreb influencers
│   └── brands.csv                # 8 Tunisian brands with niche targets
├── static/
│   └── style.css                 # Dark theme (#080810 bg, #e53e3e accent)
├── .env.example                  # Environment variable template
└── requirements.txt
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- An [OpenRouter](https://openrouter.ai/) API key *(optional — the app works without one)*
- An Instagram account session *(optional — only needed for the Scrape page)*

### Installation

```bash
git clone https://github.com/your-username/TrustInflu.git
cd TrustInflu

python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
# Edit .env and paste your OPENROUTER_API_KEY
```

### Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

### Instagram scraping (optional)

The Scrape Instagram page requires an active session file.  
Export your Instagram cookies from a browser extension (e.g. *Cookie-Editor*) as JSON and save them as `instagram_session_cookies.json` in the project root. The scraper picks them up automatically.

> The session file is listed in `.gitignore` — it will never be committed.

---

## Pages

| Page | Slug | Description |
|---|---|---|
| Accueil | `/` | Hero landing with pipeline overview |
| Audit | `audit` | Full influencer breakdown — radar, donut, 4-panel stats, AI recommendation |
| Brand Match | `brand` | Select a Tunisian brand → get top 5 matched influencers |
| Classement | `classement` | Leaderboard with niche filter and platform charts |
| Scrape Instagram | `ig` | Live scrape → score → sentiment → track history |

---

## Architecture Notes

- **`score_influencer(influencer, product_description)`** is the single public entry point for all non-AI scoring. It compiles the 4-node graph once (module-level singleton) and is safe to call from `@st.cache_data`.
- `InfluencerState` is a `TypedDict` — the LangGraph state flows through all nodes without mutation; each node returns `{**state, ...new_fields}`.
- The ad detection system (`instagram_scraper.py`) uses 6 independent detection layers including Arabic/Tunisian dialect hashtags and caption patterns (WhatsApp CTA, price patterns, brand `@mention` heuristics).
- Comment sentiment uses a language-aware keyword classifier with separate `_POSITIVE_KW`, `_NEGATIVE_KW`, and `_INSULT_KW` sets covering French, English, Arabic, and Tunisian slang.

---

## License

MIT
