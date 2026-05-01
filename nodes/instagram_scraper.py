import time
import os
from datetime import datetime, timezone
from pathlib import Path

import instaloader

SESSION_USER = "chellyoussama35"
# Session file lives at Hackathon 1/instagram_session (two levels up from nodes/)
SESSION_FILE = str(Path(__file__).parent.parent.parent / "instagram_session")

NICHE_KEYWORDS = {
    "Music":        ["music","musique","song","rap","rnb","album","single","concert",
                     "singer","chanteur","artiste","artist","beat","studio","dj","trap"],
    "Fashion":      ["fashion","mode","style","outfit","ootd","clothes","vêtements",
                     "brand","collection","tendance","look","modeling","model"],
    "Beauty":       ["beauty","beauté","makeup","maquillage","skincare","cosmetic",
                     "cosmétique","hair","cheveux","nails","routine","glow"],
    "Sport":        ["sport","fitness","gym","workout","football","basketball",
                     "running","coach","training","musculation","foot","tennis"],
    "Food & Resto": ["food","nourriture","restaurant","cuisine","chef","recette",
                     "recipe","eat","manger","gastro","cook","boulangerie","café"],
    "Travel":       ["travel","voyage","trip","tourism","tourisme","explore",
                     "adventure","aventure","destination","wanderlust","backpack"],
    "Tech & Gaming":["tech","technology","gaming","game","jeu","developer","coding",
                     "ai","startup","digital","programmer","software","hardware"],
    "Cuisine TN":   ["tunisian","tunisie","tunisien","couscous","lablabi","brik",
                     "makloub","merguez","ojja","harissa","Tunisia"],
}


def detect_niche(bio: str, captions: list[str]) -> str:
    text = (bio + " " + " ".join(captions)).lower()
    scores = {niche: sum(1 for kw in kws if kw.lower() in text)
              for niche, kws in NICHE_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Music"


def scrape_profile(username: str) -> dict:
    """
    Scrape an Instagram profile and return a dict compatible with
    the TrustInflu influencer schema + extra fields for display.
    Raises on login failure or profile not found.
    """
    L = instaloader.Instaloader(
        max_connection_attempts=3,
        request_timeout=30,
        quiet=True,
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
    )
    L.load_session_from_file(SESSION_USER, SESSION_FILE)

    profile = instaloader.Profile.from_username(L.context, username)

    # ── Posts ────────────────────────────────────────────────────────────────
    raw_posts = []
    captions = []
    oldest_date = None
    ad_count = 0

    for i, post in enumerate(profile.get_posts()):
        if i >= 20:
            break
        raw_posts.append({
            "shortcode": post.shortcode,
            "date": post.date_utc.isoformat(),
            "likes": post.likes,
            "comments": post.comments,
            "is_video": post.is_video,
            "video_view_count": post.video_view_count if post.is_video else None,
            "is_sponsored": post.is_sponsored,
            "caption": (post.caption or "")[:300],
            "url": f"https://www.instagram.com/p/{post.shortcode}/",
        })
        captions.append(post.caption or "")
        if post.is_sponsored:
            ad_count += 1
        oldest_date = post.date_utc
        time.sleep(0.5)

    # ── Derived metrics ───────────────────────────────────────────────────────
    followers = profile.followers or 1
    avg_likes = (sum(p["likes"] for p in raw_posts) / len(raw_posts)) if raw_posts else 0
    engagement_rate = round(avg_likes / followers * 100, 2) if followers > 0 else 0.0

    if oldest_date:
        now = datetime.now(timezone.utc)
        if oldest_date.tzinfo is None:
            oldest_date = oldest_date.replace(tzinfo=timezone.utc)
        account_age_months = max(1, int((now - oldest_date).days / 30))
    else:
        account_age_months = 12

    niche = detect_niche(profile.biography or "", captions)

    # ── Return dict ───────────────────────────────────────────────────────────
    return {
        # ── Core schema fields (match influencers.csv) ──
        "id": abs(hash(username)) % 1_000_000,
        "name": profile.full_name or username,
        "city": "N/A",
        "country": "TN",
        "platform": "Instagram",
        "niche": niche,
        "followers": profile.followers,
        "following": profile.followees,
        "engagement_rate": engagement_rate,
        "posts_count": profile.mediacount,
        "account_age_months": account_age_months,
        "has_profile_pic": 1 if profile.profile_pic_url else 0,
        "bio_length": len(profile.biography or ""),
        "has_external_url": 1 if profile.external_url else 0,
        "is_private": 1 if profile.is_private else 0,
        "trust_score": 0,
        "profile_pic_url": profile.profile_pic_url or "",
        "bio": profile.biography or "",
        # ── Extra display fields ──
        "_username": username,
        "_is_verified": profile.is_verified,
        "_posts": raw_posts,
        "_ad_count": ad_count,
        "_scraped_at": datetime.now(timezone.utc).isoformat(),
    }
