import re
import time
import os
from datetime import datetime, timezone
from pathlib import Path

import instaloader

SESSION_USER = "chellyoussama35"
SESSION_FILE = str(Path(__file__).parent.parent / "instagram_session")

# ── Niche detection ───────────────────────────────────────────────────────────
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

# ── Ad / sponsored hashtags ───────────────────────────────────────────────────
# Normalised (lowercase, no accents stripped — matching is done on lowercased tags).
# Covers: English, French, Arabic, Tunisian/Maghreb slang, and platform-specific tags.
AD_HASHTAGS = {
    # ── English — explicit disclosure ────────────────────────────────────────
    "ad", "ads", "advertisement", "advertisements",
    "sponsored", "sponsorship", "sponsoredpost", "sponsoredcontent",
    "sponsoredby", "sponsoredad", "sponsoredlink",
    "paid", "paidpartnership", "paidcollaboration", "paidpromo",
    "paidpost", "paidadvertisement",
    "partner", "partners", "partnership", "inpartnershipwith",
    "brandpartner", "brandpartnership", "brandambassador", "ambassador",
    "branddeal", "brandcollaboration", "brandcollab",
    "gifted", "giftedbybrand", "giftedproduct", "gifteditems",
    "gifted_by", "giftedbyme", "complimentary",
    "collab", "collaboration", "collaborationpost",
    "promo", "promotion", "promotional", "promotionalpost",
    "endorse", "endorsed", "endorsement",
    "affiliate", "affiliatelink", "affiliatecode", "affiliatemarketing",
    "referral", "referralcode", "referrallink",
    "discount", "discountcode", "couponcode", "exclusivecode",
    "productreview", "reviewpost", "reviewedby",
    "notanad",          # ironic disclosure trap — people say this when it IS an ad
    "thisisanad",
    "iworkwith",
    "workedwith",

    # ── French — explicit disclosure ─────────────────────────────────────────
    "pub", "publicite", "publicité",
    "annonce", "annoncecommerciale", "annoncecommerciale",
    "sponsor", "sponsorisé", "sponsorise", "sponsorisedby",
    "partenariat", "partenaire", "partenaires",
    "partenairecommercial", "partenariatscommercial",
    "encartpublicitaire", "insertioncommerciale",
    "collaboration", "encollaboration", "encollaborationavec",
    "offertpar", "offertby", "produitoffert", "offerteparlamaque",
    "marque", "marquepartenaire",
    "cadeau", "cadeaumarque", "cadeaupresse", "pressgift",
    "code", "codecommercial", "codepromo", "codereduction",
    "promotion", "promotioncommerciale",
    "ambassadeur", "ambassadrice", "ambassadeurdemarque",
    "testproduit", "testetunapprouve", "jelateste",
    "placement", "placementproduit",

    # ── Arabic — explicit disclosure ─────────────────────────────────────────
    "اعلان", "إعلان", "اعلانات", "إعلانات",
    "اعلان_مدفوع", "اعلان_مموّل", "اعلان_ممول",
    "ممول", "مموّل",
    "دعاية", "دعايه", "دعاية_وإعلان",
    "شراكة", "شراكه", "شراكة_تجارية",
    "تعاون", "تعاون_تجاري",
    "راعي", "رعاية", "برعاية",
    "سبونسر",
    "عرض", "عرض_خاص",
    "كود", "كود_خصم", "كوبون",
    "هدية", "هديه", "هدية_من",
    "تقييم", "تجربة", "جربت",
    "منتج", "منتج_ممول", "اختبار_منتج",

    # ── Tunisian / Maghreb slang ─────────────────────────────────────────────
    "mrawin",       # Tunisian for "sponsored" (مرووين)
    "sponsori",     # Tunisian/French blend
    "pub_payante",
    "mourawin",
    "b9alet",       # Tunisian slang for a paid plug
    "3ardhom",      # "they offered me"
    "mawhoba",      # "gifted" in Tunisian dialect
    "collab_tn",
    "marque_tn",
    "partenariat_tn",

    # ── Platform / meta tags ─────────────────────────────────────────────────
    "instagrampartner",
    "creatorpartner",
    "ugccreator", "ugc", "ugccontentcreator",
    "contentcreator",       # not always ad, but paired with brand tags
    "influencer",
    "influencermarketing",
    "influencerad",
    "microinfluencer",
    "nanoinfluencer",
}

# Patterns that appear INSIDE hashtags (substring match) and always signal an ad.
# e.g. #nike_ad, #pepsi_sponsored, #tunisietelecom_partenariat
_AD_SUBSTRINGS = (
    "_ad", "ad_", "_sponsored", "_collab", "_partner",
    "_promo", "_pub", "_annonce", "_partenariat",
    "_sponsorise", "_sponsor", "_ambassadeur",
    "_gifted", "_offert", "_كود", "_اعلان",
)

# ── Comment sentiment keywords ─────────────────────────────────────────────────
_POSITIVE_KW = {
    # French
    "super","bien","magnifique","excellent","bravo","incroyable","génial","parfait",
    "merci","felicitations","félicitations","top","trop bien","beauté","beau","belle",
    "fier","fière","inspirant","motivant","waou","waouh",
    # English
    "love","amazing","great","fantastic","wonderful","perfect","beautiful","awesome",
    "incredible","nice","good","best","excellent","brilliant","stunning","gorgeous",
    "thank","congrats","congratulations","fire","lit","dope","sick",
    # Arabic/Tunisian
    "برافو","ربي يعطيك","مبروك","رائع","ممتاز","جميل","تبارك","ماشاء","الله يبارك",
    "زين","مزيان","واو","احسنت","شكرا",
    # Emojis (as text)
    "❤","🔥","😍","👏","💪","🙌","💯","✨","🥰","😊","👍","🫶","💪",
}

_NEGATIVE_KW = {
    # French
    "nul","horrible","arnaque","faux","menteur","escroquerie","déçu","terrible",
    "raté","honte","scandaleux","dégoûtant","pathétique","ridicule","lamentable",
    "arnaquer","vole","voleur","trompeur","manipulation","médiocre",
    # English
    "fake","scam","fraud","liar","lie","disgusting","pathetic","hate","terrible",
    "awful","horrible","disappointing","dishonest","trash","garbage","worst",
    "stop","unfollow","block","report",
    # Arabic/Tunisian
    "كذاب","نصاب","حرام","خسارة","مسخرة","غلط","باطل","عيب","مزيف",
    "فك","احتيال","تضليل","مشعل","مخزي",
    # Emojis
    "🤮","🤢","💩","😡","😤","🖕","😒","👎","😠",
}

_INSULT_KW = {
    # French insults (mild to strong)
    "idiot","imbécile","stupide","débile","crétin","abruti","con","connard",
    "naze","bouffon","clown","minus","raté",
    # English
    "idiot","stupid","moron","dumb","loser","clown","fool","jerk",
    # Tunisian/Arabic
    "حمار","غبي","بهيمة","فاشل","مجنون","حقير","وسخ",
}


def detect_niche(bio: str, captions: list) -> str:
    text = (bio + " " + " ".join(captions)).lower()
    scores = {niche: sum(1 for kw in kws if kw.lower() in text)
              for niche, kws in NICHE_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Music"


# ── Caption-level ad patterns (no hashtag needed) ────────────────────────────
_AD_CAPTION_PATTERNS = re.compile(
    r"""
    # ── Brand collab "X" notation ─────────────────────────────────────────────
    # "hoodies x aid", "Nour × brand", "collection x store"
    \b\w[\w]*\s+[xX×]\s+\w+

    # ── English commercial signals ─────────────────────────────────────────────
    | link\s+in\s+(my\s+)?bio
    | check\s+(my\s+)?bio
    | bio\s+link
    | swipe\s+up
    | use\s+(my\s+)?code\b
    | use\s+(my\s+)?link\b
    | available\s+(now|online|at|on|in)
    | shop\s+(now|here|link|my|at)
    | order\s+(now|here|via|from)
    | get\s+(yours|it\s+now|yours\s+now)
    | \bcollab\b
    | \bpartnership\b
    | \bsponsored\b
    | \baffiliate\b
    | discount\s+code
    | promo\s+code
    | coupon\s+code
    | \d+\s*%\s+off
    | free\s+shipping
    | limited\s+(time|offer|stock|edition)
    | dm\s+(me\s+)?(to\s+)?(order|buy|get|for)
    | message\s+(me\s+)?(to\s+)?(order|buy|get|for)
    | whatsapp\s+(me|us|to\s+order)

    # ── French commercial signals ──────────────────────────────────────────────
    | lien\s+en\s+bio
    | lien\s+dans\s+(ma\s+|la\s+)?bio
    | voir\s+(ma\s+)?bio
    | code\s+promo
    | code\s+r[eé]duc(tion)?
    | r[eé]duction\s+de\s+\d+
    | \d+\s*%\s+de\s+r[eé]duc
    | disponible\s+(sur|en|au|dans|chez)
    | commandez?\s+(sur|ici|maintenant|via|au)
    | achetez?\s+(sur|ici|maintenant|via|au)
    | livraison\s+(gratuite|offerte|rapide|partout)
    | livr[eé]\s+(partout|en\s+tunisie|au\s+maroc)
    | \bcollab\b
    | \bpartenariat\b
    | \bcollaboration\b
    | offert\s+par
    | en\s+partenariat\s+avec
    | en\s+collaboration\s+avec
    | contactez[- ]nous
    | contacte[- ](moi|nous)
    | envoyez?\s+(un\s+)?message
    | whatsapp\s*:\s*\+?\d
    | num[eé]ro\s+(whatsapp|de\s+contact)
    | stock\s+limit[eé]
    | derni[eè]res?\s+pi[eè]ces?

    # ── Tunisian / Maghreb dialect signals ────────────────────────────────────
    | wa\.me\/
    | whatsapp\.com\/
    | lien\s+bio
    | bio\s+fi\s+link
    | في\s+البيو
    | في\s+البايو
    | رابط\s+في\s+البيو
    | الرابط\s+في\s+البيو
    | لينك\s+في\s+البيو
    | متوفر\s*(الآن|عندنا|لدينا|على|في)?
    | اطلب\s*(الآن|من|عبر|هنا)?
    | كود\s*خصم
    | بكود
    | كوبون
    | تسوق\s*الآن
    | تواصل\s*معنا
    | تواصلوا\s*معنا
    | ارسل\s*(رسالة|واتساب|ماساج)
    | واتساب\s*:\s*\+?\d
    | للطلب\s*(واتساب|هنا|كلمنا|تواصل)
    | للاستفسار
    | مش\s+هتلاقي\s+أحسن    # "you won't find better"
    | توصيل\s*(مجاني|لكل|لجميع)
    | متاح\s*(الآن|للطلب|على)
    | اسعار\s*خاصة
    | عروض\s*خاصة
    | عرض\s*محدود

    # ── Price / currency patterns (product being sold) ────────────────────────
    | \d+\s*(dt|dinar|tnd|mad|dzd|€|euro|dollars?)
    | prix\s*:\s*\d
    | price\s*:\s*\d
    | سعر\s*:\s*\d
    | ثمن\s*:\s*\d
    """,
    re.VERBOSE | re.IGNORECASE,
)

# ── Brand-like account patterns ───────────────────────────────────────────────
# Applied to @mentions in caption, tagged-in-photo users, and collab co-authors.
_BRAND_ACCOUNT_RE = re.compile(
    r"""
    # TLD-style endings
    \.tn | \.ma | \.dz | \.com | \.shop | \.store | \.fr | \.net

    # Commerce words anywhere in the handle
    | store | shop | boutique | market | mall | center | centre
    | brand | brands | label
    | official | officia | offcial          # typos included
    | collection | collections | collab
    | fashion | mode | style | wear | apparel | clothing | clothes | outfit
    | beauty | beaute | cosmet | makeup | skincare | parfum | fragrance
    | food | resto | restaurant | cafe | coffee | patisserie | boulangerie
    | tech | digital | agency | agence | media | studio | creative
    | group | grp | holding | company | corp | enterprise | sarl | suarl
    | tunisie | tunisia | tunis | maroc | algerie | maghreb | sfax | sousse | nabeul
    | trading | import | export | wholesale | grossiste | distribution

    # Known Tunisian / Maghreb brands and patterns
    | predator | new_chic | aurea | beoutq | ooredoo | topnet | ttelecom
    | monoprix | geant | carrefour | poulina | delice | vitalait | syphax
    | ennakl | artes | utic | stb | biat | attijari | zitouna
    | jumia | glovo | hellocoins | flouci
    """,
    re.VERBOSE | re.IGNORECASE,
)


def _extract_hashtags(text: str) -> list:
    """Return lowercased hashtag strings (without #) found in text."""
    return [tag.lstrip("#").lower() for tag in re.findall(r'#\w+', text or "")]


def _extract_mentions(text: str) -> list:
    """Return lowercased @mention strings (without @) found in text."""
    return [m.lstrip("@").lower() for m in re.findall(r'@[\w.]+', text or "")]


def _is_brand_account(username: str) -> bool:
    """Return True if the username looks like a brand / commercial account."""
    return bool(_BRAND_ACCOUNT_RE.search(username))


def _is_ad_post(
    caption: str,
    is_sponsored: bool,
    coauthors: list = None,
    tagged_users: list = None,
) -> tuple:
    """
    Returns (is_ad: bool, reasons: list[str]).

    6-layer detection:
      1. Instagram native branded-content / is_sponsored flag
      2. Instagram Collab co-author that looks like a brand (@store.new_chic)
      3. Hashtag exact match against AD_HASHTAGS
      4. Hashtag substring match  (#pepsi_ad, #nike_sponsored)
      5. Caption text patterns    (collab "x" notation, commercial phrases,
                                   WhatsApp links, prices, Arabic CTA phrases,
                                   brand @mentions inside caption)
      6. Photo-tagged users       (brand tagged IN the image, not in caption)
    """
    reasons = []
    caption = caption or ""
    seen = set()   # deduplicate reason strings

    def _add(r):
        if r not in seen:
            seen.add(r)
            reasons.append(r)

    # Layer 1 — Instagram native branded-content flag
    if is_sponsored:
        _add("[Instagram Branded Content]")

    # Layer 2 — Instagram Collab co-author
    for coauthor in (coauthors or []):
        uname = (coauthor.get("username") or "").lower().strip()
        if uname and _is_brand_account(uname):
            _add(f"[Collab: @{uname}]")

    # Layer 3 & 4 — Hashtag detection (exact + substring)
    for tag in _extract_hashtags(caption):
        if tag in AD_HASHTAGS:
            _add(f"#{tag}")
        elif any(sub in tag for sub in _AD_SUBSTRINGS):
            _add(f"#{tag}")

    # Layer 5a — Caption commercial phrases
    for match in _AD_CAPTION_PATTERNS.finditer(caption):
        snippet = match.group(0).strip()[:45]
        _add(f'["{snippet}"]')

    # Layer 5b — @mentions of brand-like accounts inside caption text
    for mention in _extract_mentions(caption):
        if _is_brand_account(mention):
            _add(f"[@{mention}]")

    # Layer 6 — Users tagged IN the photo/video (not in caption)
    for uname in (tagged_users or []):
        uname = uname.lower().strip()
        if uname and _is_brand_account(uname):
            _add(f"[tagged in photo: @{uname}]")

    return bool(reasons), reasons


def _classify_comment(text: str) -> str:
    """Return 'positive', 'negative', 'insult', or 'neutral'."""
    t = text.lower()
    has_insult = any(kw in t for kw in _INSULT_KW)
    has_negative = any(kw in t for kw in _NEGATIVE_KW)
    has_positive = any(kw in t for kw in _POSITIVE_KW)

    if has_insult:
        return "insult"
    if has_negative and not has_positive:
        return "negative"
    if has_positive and not has_negative:
        return "positive"
    if has_positive and has_negative:
        return "mixed"
    return "neutral"


def _analyze_comments(comments: list) -> dict:
    """
    Returns counts and ratios of positive / negative / insult / neutral comments.
    Error markers injected by the scraper (starting with __error__) are filtered out.
    """
    scrape_errors = [c for c in comments if c.startswith("__error__")]
    real_comments = [c for c in comments if not c.startswith("__error__")]

    counts = {"positive": 0, "negative": 0, "insult": 0, "mixed": 0, "neutral": 0}
    for c in real_comments:
        label = _classify_comment(c)
        counts[label] += 1
    comments = real_comments

    total = max(len(comments), 1)

    # Each comment belongs to exactly one bucket → the 4 ratios sum to 100%
    positive_ratio = counts["positive"] / total
    neutral_ratio  = (counts["neutral"] + counts["mixed"]) / total
    negative_ratio = counts["negative"] / total
    insult_ratio   = counts["insult"] / total

    # Community health score 0-1:
    #   Driven by how much NEGATIVE/INSULT content exists (not by lack of positives).
    #   A mostly neutral community is healthy; only penalise actual bad signals.
    toxicity = negative_ratio * 0.6 + insult_ratio * 1.0
    sentiment_score = round(max(0.0, min(1.0, 1.0 - toxicity)), 3)

    return {
        "counts": counts,
        "total": len(comments),
        "positive_ratio": round(positive_ratio, 3),
        "neutral_ratio":  round(neutral_ratio, 3),
        "negative_ratio": round(negative_ratio, 3),
        "insult_ratio":   round(insult_ratio, 3),
        "sentiment_score": sentiment_score,
        "scrape_errors": len(scrape_errors),
        "sample_positive": [],
        "sample_negative": [],
    }


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
        download_comments=True,   # must be True for get_comments() to work
        save_metadata=False,
    )
    # Load session — try instaloader format first, fall back to cookies JSON
    _cookies_json = SESSION_FILE + "_cookies.json"
    if os.path.exists(SESSION_FILE):
        L.load_session_from_file(SESSION_USER, SESSION_FILE)
    elif os.path.exists(_cookies_json):
        import json as _json
        _raw = _json.load(open(_cookies_json))
        # Inject cookies directly into the existing instaloader session
        _cookie_dict = {
            c["name"]: c["value"]
            for c in _raw
            if "instagram.com" in c.get("domain", "")
        }
        L.context._session.cookies.update(_cookie_dict)
        # Set required headers instaloader expects
        _csrf = _cookie_dict.get("csrftoken", "")
        L.context._session.headers.update({
            "x-csrftoken": _csrf,
            "x-ig-app-id": "936619743392459",
            "x-requested-with": "XMLHttpRequest",
        })
        L.context.username = SESSION_USER
    else:
        raise FileNotFoundError("No Instagram session found. Run login_instagram.py first.")

    # Verify the session is actually authenticated
    logged_in_user = L.test_login()
    if not logged_in_user:
        raise ConnectionError(
            "Session expirée ou invalide. Relancez login_instagram.py pour reconnecter le compte."
        )

    profile = instaloader.Profile.from_username(L.context, username)

    # ── Posts + comments ──────────────────────────────────────────────────────
    raw_posts   = []
    captions    = []
    oldest_date = None
    ad_count    = 0
    all_comments      = []    # flat list of comment texts
    sample_positive   = []
    sample_negative   = []

    try:
      post_iter = profile.get_posts()
    except (KeyError, TypeError) as e:
      raise RuntimeError(f"Impossible de charger les posts ({e}). Le compte est peut-être privé ou Instagram a limité l'accès.") from e

    for i, post in enumerate(post_iter):
        if i >= 20:
            break

        caption = post.caption or ""

        # Layer 2: Instagram Collab co-authors (the "et @brand" in the UI)
        coauthors = []
        try:
            raw_coauthors = post._node.get("coauthor_producers") or []
            coauthors = [{"username": c.get("username", "")} for c in raw_coauthors]
        except Exception:
            pass

        # Layer 6: users tagged IN the photo/video
        tagged_users = []
        try:
            tagged_users = list(post.tagged_users)
        except Exception:
            pass

        is_ad, ad_tags = _is_ad_post(caption, post.is_sponsored, coauthors, tagged_users)
        if is_ad:
            ad_count += 1

        post_comments_text = []

        # Scrape comments for first 10 posts, up to 30 comments each
        if i < 10:
            try:
                for j, comment in enumerate(post.get_comments()):
                    if j >= 30:
                        break
                    ctext = (comment.text or "").strip()
                    if ctext:
                        post_comments_text.append(ctext)
                        all_comments.append(ctext)
                        label = _classify_comment(ctext)
                        if label == "positive" and len(sample_positive) < 5:
                            sample_positive.append(ctext[:150])
                        elif label in ("negative", "insult") and len(sample_negative) < 5:
                            sample_negative.append(ctext[:150])
                    time.sleep(0.15)
            except (KeyError, TypeError, StopIteration):
                # Instagram returned unexpected structure (rate limit or private)
                pass
            except Exception as e:
                all_comments.append(f"__error__{e}")

        raw_posts.append({
            "shortcode": post.shortcode,
            "date": post.date_utc.isoformat(),
            "likes": post.likes,
            "comments": post.comments,
            "is_video": post.is_video,
            "video_view_count": post.video_view_count if post.is_video else None,
            "is_sponsored": is_ad,
            "ad_tags": ad_tags,
            "caption": caption[:300],
            "url": f"https://www.instagram.com/p/{post.shortcode}/",
            "comment_texts": post_comments_text,
        })
        captions.append(caption)
        oldest_date = post.date_utc
        time.sleep(0.5)

    # ── Comment sentiment analysis ────────────────────────────────────────────
    sentiment_data = _analyze_comments(all_comments)
    sentiment_data["sample_positive"] = sample_positive
    sentiment_data["sample_negative"] = sample_negative

    # ── Derived metrics ───────────────────────────────────────────────────────
    followers    = profile.followers or 1
    avg_likes    = (sum(p["likes"] for p in raw_posts) / len(raw_posts)) if raw_posts else 0
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
        # Core schema fields
        "id":                 abs(hash(username)) % 1_000_000,
        "name":               profile.full_name or username,
        "city":               "N/A",
        "country":            "TN",
        "platform":           "Instagram",
        "niche":              niche,
        "followers":          profile.followers,
        "following":          profile.followees,
        "engagement_rate":    engagement_rate,
        "posts_count":        profile.mediacount,
        "account_age_months": account_age_months,
        "has_profile_pic":    1 if profile.profile_pic_url else 0,
        "bio_length":         len(profile.biography or ""),
        "has_external_url":   1 if profile.external_url else 0,
        "is_private":         1 if profile.is_private else 0,
        "trust_score":        0,
        "profile_pic_url":    profile.profile_pic_url or "",
        "bio":                profile.biography or "",
        # Extra display fields
        "_username":          username,
        "_is_verified":       profile.is_verified,
        "_posts":             raw_posts,
        "_ad_count":          ad_count,
        "_ad_ratio":          round(ad_count / max(len(raw_posts), 1), 3),
        "_scraped_at":        datetime.now(timezone.utc).isoformat(),
        # Comment sentiment
        "_comment_sentiment": sentiment_data,
    }
