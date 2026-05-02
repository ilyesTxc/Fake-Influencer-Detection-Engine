import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys, os
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
from nodes.scoring import score_influencer

st.set_page_config(
    page_title="TrustInflu",
    page_icon="🇹🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS ──────────────────────────────────────────────────────────────
with open(os.path.join(os.path.dirname(__file__), "static", "style.css"), encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_influencers():
    frame = pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "influencers.csv"))
    frame = frame.copy()
    frame["trust_score"] = [score_influencer(row.to_dict())["trust_score"] for _, row in frame.iterrows()]
    return frame

@st.cache_data
def load_brands():
    return pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "brands.csv"))

df = load_influencers()
brands_df = load_brands()

# ── Helpers ──────────────────────────────────────────────────────────────────
def score_tier(score):
    if score >= 80:
        return "green"
    if score >= 50:
        return "amber"
    return "red"

def badge_color(score):
    if score >= 80: return "#10b981"
    if score >= 50: return "#f59e0b"
    return "#ef4444"

def badge_label(score):
    if score >= 80: return "🟢 Certifié"
    if score >= 50: return "🟡 À surveiller"
    return "🔴 Suspect"

def platform_icon(p):
    return {"Instagram": "📸", "TikTok": "🎵", "YouTube": "▶️"}.get(p, "🌐")

def country_flag(c):
    return {"TN": "🇹🇳", "MA": "🇲🇦", "DZ": "🇩🇿"}.get(c, "🌍")

def render_score_badge(score, size=64):
    tier = score_tier(score)
    return (
        f'<div class="score-badge badge-{tier} tier-{tier}" '
        f'style="--score-size:{size}px"><span>{score}</span></div>'
    )

def render_influencer_card(row):
    tier = score_tier(row.trust_score)
    flag = country_flag(row.country)
    icon = platform_icon(row.platform)
    st.markdown(
        f"""
        <div class="inf-card tier-{tier}">
            <div class="inf-header">
                <div class="inf-avatar">
                    <img src="{row.profile_pic_url}" width="56" height="56" style="border-radius:50%">
                    <span class="inf-platform">{icon}</span>
                </div>
                <div>
                    <div class="inf-name">{row['name']} {flag}</div>
                    <div class="inf-meta">{row.platform} · {row.city} · {row.niche}</div>
                    <div class="inf-stats">
                        <span class="inf-chip">👥 {row.followers:,}</span>
                        <span class="inf-chip">❤️ {row.engagement_rate}%</span>
                        <span class="inf-chip">📝 {row.posts_count:,}</span>
                    </div>
                </div>
                <div class="inf-score">
                    {render_score_badge(row.trust_score, 52)}
                    <div class="inf-score-label">{badge_label(row.trust_score)}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_page_header(page_name):
    st.markdown(
        f"""
        <div class="ti-page-header">
            <div class="ti-breadcrumb">TrustInflu / <span>{page_name}</span></div>
            <div class="ti-live-badge"><span class="ti-live-dot"></span>MAGHREB MARKET · LIVE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Sidebar ──────────────────────────────────────────────────────────────────
nav_items = [
    ("accueil",    "Accueil"),
    ("decouverte", "Découverte"),
    ("audit",      "Audit"),
    ("brand",      "Brand Match"),
    ("classement", "Classement"),
    ("ig",         "Scrape Instagram"),
]

nav_slugs = [n[0] for n in nav_items]
nav_labels = [n[1] for n in nav_items]

# Resolve current page purely from session_state — no <a href> links, no query params
if "page_slug" not in st.session_state:
    st.session_state["page_slug"] = "accueil"
current_slug = st.session_state["page_slug"]
if current_slug not in nav_slugs:
    current_slug = "accueil"
    st.session_state["page_slug"] = "accueil"

with st.sidebar:
    st.markdown(
        """
        <div class="ti-sidebar-logo">
            <h1><span class="ti-logo-accent">Trust</span>Influ</h1>
            <div class="ti-underline"></div>
            <p>Powered for the Maghreb</p>
        </div>
        <div class="ti-nav-section-label">Menu</div>
        """,
        unsafe_allow_html=True,
    )

    for slug, label in nav_items:
        is_active = current_slug == slug
        st.markdown(
            f'<div class="ti-nav-btn {"ti-nav-active" if is_active else "ti-nav-inactive"}">',
            unsafe_allow_html=True,
        )
        if st.button(label, key=f"nav_{slug}", use_container_width=True):
            st.session_state["page_slug"] = slug
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class=\"ti-sidebar-footer\">v1.0 · Hackathon 2025</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — ACCUEIL
# ══════════════════════════════════════════════════════════════════════════════
if current_slug == "accueil":
    render_page_header("Accueil")
    st.markdown(
        """
        <section class="ti-hero">
            <div class="ti-hero-blobs">
                <span class="ti-blob blob-gold"></span>
                <span class="ti-blob blob-blue"></span>
                <span class="ti-blob blob-cyan"></span>
            </div>
            <h1>TrustInflu</h1>
            <p>La première plateforme de confiance pour les influenceurs du Maghreb</p>
            
        </section>
        """,
        unsafe_allow_html=True,
    )


    st.markdown("#### Comment ça marche ?")
    steps = [
        ("01", "Entrez un nom d'influenceur ou importez une liste CSV"),
        ("02", "Notre pipeline LangGraph analyse le profil en 5 étapes"),
        ("03", "4 modèles ML calculent un Trust Score 0–100"),
        ("04", "Sélectionnez votre marque et obtenez les meilleurs matchs"),
    ]
    cols = st.columns(4)
    for col, (num, text) in zip(cols, steps):
        col.markdown(
            f"""
            <div class="step-card">
                <div class="step-num">{num}</div>
                <div class="muted">{text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — DÉCOUVERTE
# ══════════════════════════════════════════════════════════════════════════════
elif current_slug == "decouverte":
    render_page_header("Découverte")
    st.markdown("### 🔍 Découverte des influenceurs")

    st.markdown("<div class=\"ti-filter-bar\">", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with col1:
        niches = ["Toutes"] + sorted(df["niche"].unique().tolist())
        niche_filter = st.selectbox("Niche", niches)
    with col2:
        regions = ["Toutes"] + sorted(df["city"].unique().tolist())
        region_filter = st.selectbox("Région / Ville", regions)
    with col3:
        platforms = ["Toutes"] + sorted(df["platform"].unique().tolist())
        platform_filter = st.selectbox("Plateforme", platforms)
    with col4:
        min_score = st.slider("Trust Score minimum", 0, 100, 0, 5)
    st.markdown("</div>", unsafe_allow_html=True)

    filtered = df.copy()
    if niche_filter != "Toutes":
        filtered = filtered[filtered["niche"] == niche_filter]
    if region_filter != "Toutes":
        filtered = filtered[filtered["city"] == region_filter]
    if platform_filter != "Toutes":
        filtered = filtered[filtered["platform"] == platform_filter]
    filtered = filtered[filtered["trust_score"] >= min_score]
    filtered = filtered.sort_values("trust_score", ascending=False)

    st.markdown(
        f"<div class=\"count-pill\">{len(filtered)} influenceur(s) trouvé(s)</div>",
        unsafe_allow_html=True,
    )

    cols = st.columns(2)
    for i, (_, row) in enumerate(filtered.iterrows()):
        with cols[i % 2]:
            render_influencer_card(row)
            st.markdown('<div class="inf-audit-btn">', unsafe_allow_html=True)
            if st.button("Voir l'audit →", key=f"audit_{row['id']}", type="secondary"):
                st.session_state["audit_id"] = row["id"]
                st.session_state["page_slug"] = "audit"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — AUDIT
# ══════════════════════════════════════════════════════════════════════════════
elif current_slug == "audit":
    render_page_header("Audit")

    # ── Selector row ─────────────────────────────────────────────────────────
    sel_c1, sel_c2 = st.columns([1.5, 2])
    with sel_c1:
        names = df["name"].tolist()
        default_idx = 0
        if "audit_id" in st.session_state:
            ids = df["id"].tolist()
            if st.session_state["audit_id"] in ids:
                default_idx = ids.index(st.session_state["audit_id"])
        selected_name = st.selectbox("Influenceur", names, index=default_idx)
    with sel_c2:
        product_desc = st.text_input(
            "Contexte produit (optionnel)",
            placeholder="Ex: Lancement parfum Oriental Maghreb...",
            key="product_desc_input",
        )

    row = df[df["name"] == selected_name].iloc[0]
    inf = row.to_dict()
    result = score_influencer(inf, product_desc)
    breakdown = result["score_breakdown"]
    tier = score_tier(row.trust_score)
    color = badge_color(row.trust_score)
    flag = country_flag(row.country)
    icon = platform_icon(row.platform)

    # ── 3-COLUMN LAYOUT: Profile | Score | Activity ───────────────────────────
    left_col, center_col, right_col = st.columns([1.1, 2, 1.1])

    # ── LEFT: Influencer Profile ──────────────────────────────────────────────
    with left_col:
        st.markdown(
            f"""
            <div class="profile-card tier-{tier}" style="text-align:center">
                <div style="font-size:0.65rem;font-weight:700;color:var(--text-muted);
                    text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px">
                    Profil Influenceur
                </div>
                <img src="{row.profile_pic_url}" class="profile-avatar" style="width:80px;height:80px">
                <div class="inf-name" style="margin-top:8px">{row['name']} {flag}</div>
                <div class="inf-meta">{icon} {row.platform} · {row.city}</div>
                <span class="brand-sector-pill" style="margin-top:6px;display:inline-block">{row.niche}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="profile-stats" style="margin-top:8px">
                <div class="profile-stat-row">
                    <span>👥 Abonnés</span>
                    <strong>{row.followers:,}</strong>
                </div>
                <div class="profile-stat-row">
                    <span>❤️ Engagement</span>
                    <strong>{row.engagement_rate}%</strong>
                </div>
                <div class="profile-stat-row">
                    <span>📝 Publications</span>
                    <strong>{row.posts_count:,}</strong>
                </div>
                <div class="profile-stat-row">
                    <span>🌍 Pays</span>
                    <strong>{row.country}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if row.bio:
            st.markdown(
                f'<div class="bio-block" style="margin-top:8px;font-size:0.78rem">{row.bio}</div>',
                unsafe_allow_html=True,
            )

    # ── CENTER: Authenticity Score + Metric Cards ─────────────────────────────
    with center_col:
        # Large donut score chart (the 91%-style circle from the reference)
        donut_color = color
        remaining   = 100 - row.trust_score
        fig_donut   = go.Figure(go.Pie(
            values=[row.trust_score, remaining],
            hole=0.74,
            marker=dict(colors=[donut_color, "#0e1f35"]),
            showlegend=False,
            textinfo="none",
            hoverinfo="skip",
        ))
        fig_donut.add_annotation(
            text=f"<b>{row.trust_score}</b>",
            font=dict(size=44, color=donut_color, family="Inter"),
            x=0.5, y=0.55, showarrow=False,
        )
        fig_donut.add_annotation(
            text="Trust Score",
            font=dict(size=12, color="#8db4d8"),
            x=0.5, y=0.38, showarrow=False,
        )
        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=0, l=10, r=10), height=230,
        )

        badge_cls  = "authentic" if row.trust_score >= 80 else ("watch" if row.trust_score >= 50 else "suspect")
        badge_icon = "✓" if row.trust_score >= 80 else ("⚠" if row.trust_score >= 50 else "✗")
        badge_text = "AUTHENTIQUE" if row.trust_score >= 80 else ("À SURVEILLER" if row.trust_score >= 50 else "SUSPECT")

        st.markdown('<div class="audit-score-wrap">', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.7rem;font-weight:700;color:var(--text-muted);'
            'text-transform:uppercase;letter-spacing:0.1em;text-align:center;margin-bottom:4px">'
            'Score d\'Authenticité</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            f'<div style="text-align:center;margin-top:-18px">'
            f'<span class="audit-authentic-badge {badge_cls}">{badge_icon} {badge_text}</span>'
            f'<div style="color:var(--text-secondary);font-size:0.82rem;margin-top:6px">'
            f'{row["name"]} &nbsp;·&nbsp; {icon} {row.platform}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # 3 key metric cards (matches reference: Fake Follower, Bot Activity, Content Quality)
        ff_pct   = round((1 - breakdown["fake_detect"] / 15) * 100) if breakdown["fake_detect"] else 0
        bot_pct  = round((1 - breakdown["bot_detect"] / 10) * 100) if breakdown["bot_detect"] else 0
        cq_pct   = round(breakdown["consistency"] / 10 * 100)
        eng_pct  = round(breakdown["engagement"] / 25 * 100)

        def _bar_color(pct):
            return "#10b981" if pct >= 70 else "#f59e0b" if pct >= 40 else "#ef4444"

        metrics_html = '<div class="audit-metric-row">'
        for m_icon, m_label, m_val, m_pct in [
            ("🤖", "Faux Followers",  f"{ff_pct}%",  ff_pct),
            ("🔍", "Activité Bots",   f"{bot_pct}%", bot_pct),
            ("📝", "Qualité Contenu", f"{cq_pct}%",  cq_pct),
            ("⚡", "Engagement",      f"{eng_pct}%", eng_pct),
        ]:
            bc = _bar_color(m_pct)
            metrics_html += f"""
            <div class="audit-metric-card">
                <div class="amc-icon">{m_icon}</div>
                <div class="amc-value" style="color:{bc}">{m_val}</div>
                <div class="amc-label">{m_label}</div>
                <div class="amc-bar">
                    <div class="fill" style="width:{m_pct}%;background:{bc}"></div>
                </div>
            </div>"""
        metrics_html += '</div>'
        st.markdown(metrics_html, unsafe_allow_html=True)

        # Signal pills below cards
        st.markdown("<div style='margin-top:12px'>", unsafe_allow_html=True)
        _signal_meta = [
            ("⚡", "Engagement", breakdown["engagement"], 25),
            ("📊", "Ratio F/S",  breakdown["ratio"], 15),
            ("🤖", "Faux",       breakdown["fake_detect"], 15),
            ("🔍", "Bots",       breakdown["bot_detect"], 10),
            ("📝", "Posts",      breakdown["consistency"], 10),
            ("👤", "Profil",     breakdown["completeness"], 10),
            ("🎯", "Produit",    breakdown["product_match"], 10),
        ]
        _pills_html = ""
        for _ico, _name, _val, _max in _signal_meta:
            _r  = _val / _max
            _c  = "var(--green)" if _r >= 0.7 else "var(--amber)" if _r >= 0.4 else "var(--red)"
            _pills_html += (
                f'<span class="signal-pill" style="border-color:{_c}33">'
                f'<span>{_ico} {_name}</span>'
                f'<span class="sp-score" style="color:{_c}">{_val:.1f}/{_max}</span>'
                f'</span>'
            )
        st.markdown(f'<div class="signal-pills-row">{_pills_html}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── RIGHT: Recent Activity Feed ───────────────────────────────────────────
    with right_col:
        st.markdown(
            '<div style="font-size:0.65rem;font-weight:700;color:var(--text-muted);'
            'text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px">'
            'Activité Récente</div>',
            unsafe_allow_html=True,
        )
        activities = [
            ("🤖", "#10b981", "Détection bots",
             f"Score bots : {breakdown['bot_detect']:.1f}/10 — {'Sain' if breakdown['bot_detect'] >= 7 else 'Suspect'}"),
            ("❤️", "#e53e3e", "Taux d'engagement",
             f"{row.engagement_rate}% — {'Excellent' if row.engagement_rate >= 5 else 'Correct' if row.engagement_rate >= 2 else 'Faible'}"),
            ("👥", "#7c6ff7", "Faux followers",
             f"Estimation : ~{ff_pct}% artificiel{'s' if ff_pct != 1 else ''}"),
            ("📊", "#f59e0b", "Ratio F/Following",
             f"{row.followers:,} abonnés · {breakdown['ratio']:.1f}/15 pts"),
            ("📝", "#10b981", "Consistance posts",
             f"{row.posts_count} publications · Score {breakdown['consistency']:.1f}/10"),
            ("👤", "#e53e3e", "Complétude profil",
             f"Profil {'complet' if breakdown['completeness'] >= 8 else 'partiel'} · {breakdown['completeness']:.1f}/10"),
            ("🎯", "#f59e0b", "Fit produit",
             f"Alignement : {breakdown['product_match']:.1f}/10 pts"),
        ]
        feed_html = '<div class="activity-feed">'
        for a_ico, a_color, a_title, a_desc in activities:
            feed_html += f"""
            <div class="activity-item">
                <div class="activity-dot" style="background:{a_color}22;color:{a_color}">{a_ico}</div>
                <div class="activity-text">
                    <strong>{a_title}</strong>{a_desc}
                </div>
            </div>"""
        feed_html += '</div>'
        st.markdown(feed_html, unsafe_allow_html=True)

    # ── BOTTOM: 4-panel row (Community | Radar | Sentiment | AI Notes) ────────
    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)

    with b1:
        st.markdown('<div class="stat-panel">', unsafe_allow_html=True)
        st.markdown('<div class="stat-panel-title">Analyse Communautaire</div>', unsafe_allow_html=True)
        fig_comm = go.Figure(go.Pie(
            labels=["Engagement", "Ratio", "Consistance", "Profil"],
            values=[breakdown["engagement"], breakdown["ratio"],
                    breakdown["consistency"], breakdown["completeness"]],
            hole=0.5,
            marker=dict(colors=["#e53e3e", "#7c6ff7", "#10b981", "#f59e0b"]),
            showlegend=True,
            textinfo="none",
        ))
        fig_comm.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#8db4d8", margin=dict(t=10, b=0, l=0, r=0), height=160,
            legend=dict(font=dict(size=9), bgcolor="rgba(0,0,0,0)"),
            hoverlabel=dict(bgcolor="#0e1f35", bordercolor="#e53e3e", font_size=12),
        )
        st.plotly_chart(fig_comm, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with b2:
        st.markdown('<div class="stat-panel">', unsafe_allow_html=True)
        st.markdown('<div class="stat-panel-title">Radar des Signaux</div>', unsafe_allow_html=True)
        categories_r = ["Engage", "Ratio", "Faux", "Bots", "Posts", "Profil", "Âge", "Produit"]
        maxvals_r    = [25, 15, 15, 10, 10, 10, 10]
        vals_r       = [breakdown["engagement"], breakdown["ratio"], breakdown["fake_detect"],
                        breakdown["bot_detect"], breakdown["consistency"], breakdown["completeness"],
                        breakdown["product_match"]]
        pct_r = [round(v / m * 100) for v, m in zip(vals_r, maxvals_r)]
        fig_radar = go.Figure(go.Scatterpolar(
            r=pct_r + [pct_r[0]], theta=categories_r + [categories_r[0]],
            fill="toself", fillcolor="rgba(229,62,62,0.12)",
            line=dict(color="#e53e3e", width=2),
            marker=dict(color="#e53e3e", size=5),
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1a3050",
                                tickfont=dict(color="#3d5a7a", size=8)),
                angularaxis=dict(gridcolor="#1a3050", tickfont=dict(color="#8db4d8", size=9)),
            ),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#8db4d8", margin=dict(t=10, b=0, l=10, r=10), height=160,
            hoverlabel=dict(bgcolor="#0e1f35", bordercolor="#e53e3e", font_size=12),
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with b3:
        st.markdown('<div class="stat-panel">', unsafe_allow_html=True)
        st.markdown('<div class="stat-panel-title">Analyse Sentiments</div>', unsafe_allow_html=True)
        signal_labels_b = ["Engage", "Ratio", "Faux", "Bots", "Posts", "Profil"]
        signal_vals_b   = [breakdown["engagement"], breakdown["ratio"], breakdown["fake_detect"],
                           breakdown["bot_detect"], breakdown["consistency"], breakdown["completeness"]]
        signal_max_b    = [25, 15, 15, 10, 10, 10]
        bar_colors_b    = ["#10b981" if v/m >= 0.7 else "#f59e0b" if v/m >= 0.4 else "#ef4444"
                           for v, m in zip(signal_vals_b, signal_max_b)]
        fig_bar = go.Figure(go.Bar(
            x=signal_labels_b, y=signal_vals_b,
            marker_color=bar_colors_b,
            text=[f"{v:.0f}" for v in signal_vals_b],
            textposition="outside", textfont=dict(size=9, color="#8db4d8"),
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#8db4d8",
            xaxis=dict(gridcolor="#1a3050", tickfont=dict(size=9)),
            yaxis=dict(gridcolor="#1a3050", showticklabels=False),
            margin=dict(t=20, b=0, l=0, r=0), height=160,
            hoverlabel=dict(bgcolor="#0e1f35", bordercolor="#e53e3e", font_size=12),
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with b4:
        score_summary = "✅ Profil authentique" if row.trust_score >= 80 else ("⚠️ À surveiller" if row.trust_score >= 50 else "❌ Profil suspect")
        notes = [
            ("🎯", f"Score global : {row.trust_score}/100"),
            ("📊", f"Engagement : {row.engagement_rate}% ({breakdown['engagement']:.1f}/25)"),
            ("🤖", f"Bots : {breakdown['bot_detect']:.1f}/10 pts"),
            ("👥", f"Followers : {row.followers:,}"),
        ]
        notes_html = f'<div class="stat-panel"><div class="stat-panel-title">Notes IA Détection</div>'
        notes_html += f'<div style="color:var(--gold);font-weight:700;font-size:0.85rem;margin-bottom:8px">{score_summary}</div>'
        for n_ico, n_text in notes:
            notes_html += (
                f'<div style="display:flex;gap:6px;align-items:center;padding:4px 0;'
                f'border-bottom:1px solid var(--border);font-size:0.75rem;color:var(--text-secondary)">'
                f'<span>{n_ico}</span><span>{n_text}</span></div>'
            )
        notes_html += '</div>'
        st.markdown(notes_html, unsafe_allow_html=True)

    # ── AI Pipeline (unchanged, below the 4-panel row) ────────────────────────
    # Clear cached recommendation when influencer changes
    if st.session_state.get("_last_audit_name") != selected_name:
        st.session_state.pop("_ai_recommendation", None)
        st.session_state.pop("_ai_pipeline_done", None)
        st.session_state["_last_audit_name"] = selected_name

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🤖 Analyse IA — Pipeline LangGraph")

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        run_ai = st.button("✨ Générer l'analyse IA", type="primary", use_container_width=True)
    with col_info:
        st.caption("Exécute le pipeline LangGraph (5 nœuds) et génère une recommandation Claude AI")

    if run_ai:
        with st.spinner("Pipeline en cours d'exécution…"):
            ai_state = {**result, "product_description": product_desc}
            from nodes.report_node import report_node as _report_node
            ai_result = _report_node(ai_state)
            st.session_state["_ai_recommendation"] = ai_result.get("recommendation", "")
            st.session_state["_ai_pipeline_done"] = True

    if st.session_state.get("_ai_pipeline_done"):
        pipeline_steps = [
            ("🔍", "Analyse Profil", "igaudit_clf"),
            ("🤖", "Détection Bots", "twitterclf / tiktokclf"),
            ("📝", "Conformité Posts", "postclf"),
            ("📊", "Score composite", "8 signaux ML"),
            ("✨", "Rapport Claude", "claude-haiku-4-5"),
        ]
        cols_p = st.columns(5)
        for col_p, (icon, label, model_lbl) in zip(cols_p, pipeline_steps):
            col_p.markdown(
                f"""
                <div class="pipeline-card done">
                    <div style="font-size:1.2rem">{icon}</div>
                    <div style="color:var(--green);font-size:0.72rem;font-weight:600;margin:4px 0">{label}</div>
                    <div class="model">{model_lbl}</div>
                    <div style="color:var(--green);font-size:0.7rem;margin-top:4px">✓ OK</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        rec = st.session_state.get("_ai_recommendation", "")
        has_key = bool(os.environ.get("OPENROUTER_API_KEY"))
        badge = (
            '<span class="ai-badge">Claude Haiku 4.5</span>'
            if has_key else
            '<span class="ai-badge alt">Fallback ML</span>'
        )
        st.markdown(
            f"""
            <div class="ai-rec-card">
                <div class="ai-rec-content">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
                        <span class="pipeline-title">RECOMMANDATION</span>
                        {badge}
                    </div>
                    <div style="color:var(--text-primary);font-size:1rem;line-height:1.75">{rec}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — BRAND MATCH
# ══════════════════════════════════════════════════════════════════════════════
elif current_slug == "brand":
    render_page_header("Brand Match")
    st.markdown("### 🏢 Brand Match — Trouvez vos influenceurs idéaux")

    col1, col2 = st.columns([1, 2])
    with col1:
        brand_name = st.selectbox("Marque tunisienne", brands_df["name"].tolist())
        brand = brands_df[brands_df["name"] == brand_name].iloc[0]

        st.markdown(f"""
        <div class="brand-card">
            <div style="font-size:1.1rem;font-weight:700;color:var(--gold)">{brand['name']}</div>
            <span class="brand-sector-pill">{brand['sector']}</span>
            <div style="color:var(--text-primary);margin-top:10px;font-size:0.85rem">{brand['description']}</div>
            <div style="margin-top:8px">
                {''.join([f'<span class="brand-pill">{n.strip()}</span>'
                          for n in brand['target_niches'].split(',')])}
            </div>
        </div>""", unsafe_allow_html=True)

    with col2:
        target_niches = [n.strip() for n in brand["target_niches"].split(",")]
        matched = df[df["niche"].isin(target_niches)].copy()
        matched["final_score"] = [score_influencer(row.to_dict(), brand["description"])["trust_score"]
                                  for _, row in matched.iterrows()]
        matched = matched.sort_values("final_score", ascending=False).head(5)

        st.markdown(f"**Top influenceurs recommandés pour {brand_name}**")
        for i, (_, row) in enumerate(matched.iterrows()):
            medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
            color = badge_color(row["final_score"])
            flag = country_flag(row.country)
            icon = platform_icon(row.platform)
            match_tier = score_tier(row["final_score"])
            st.markdown(f"""
            <div class="match-card" style="border-left:4px solid {color}">
                <div style="display:flex;align-items:center;gap:12px">
                    <div style="font-size:1.4rem">{medal}</div>
                    <img src="{row.profile_pic_url}" style="width:44px;height:44px;border-radius:50%;border:2px solid {color}">
                    <div style="flex:1">
                        <div style="font-weight:700;color:var(--text-primary)">{row['name']} {flag}</div>
                        <div style="color:var(--text-muted);font-size:0.8rem">{icon} {row.platform} · {row.city} · {row.niche}</div>
                    </div>
                    <div style="text-align:right">
                        <div style="font-size:1.4rem;font-weight:800;color:{color}">{row['final_score']}</div>
                        <div style="color:var(--text-secondary);font-size:0.7rem">Final Score</div>
                    </div>
                </div>
                <div class="rank-progress" style="margin-top:10px">
                    <div class="fill {match_tier}" style="width:{int(row['final_score'])}%"></div>
                </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — CLASSEMENT
# ══════════════════════════════════════════════════════════════════════════════
elif current_slug == "classement":
    render_page_header("Classement")
    st.markdown("### 🏆 Classement — Top influenceurs Maghreb")

    niche_sel = st.selectbox("Filtrer par niche",
                             ["Toutes"] + sorted(df["niche"].unique().tolist()))

    top_df = df.copy()
    if niche_sel != "Toutes":
        top_df = top_df[top_df["niche"] == niche_sel]
    top_df = top_df.sort_values("trust_score", ascending=False).head(10)

    medals = ["🥇","🥈","🥉","4","5","6","7","8","9","10"]
    for i, (_, row) in enumerate(top_df.iterrows()):
        color = badge_color(row.trust_score)
        tier = score_tier(row.trust_score)
        flag = country_flag(row.country)
        icon = platform_icon(row.platform)
        bar_w = int(row.trust_score)
        rank_class = "top1" if i == 0 else ("silver" if i == 1 else ("bronze" if i == 2 else ""))
        st.markdown(f"""
        <div class="rank-card {rank_class}">
            <div style="display:flex;align-items:center;gap:14px">
                <div class="rank-number">{medals[i]}</div>
                <img src="{row.profile_pic_url}" style="width:46px;height:46px;border-radius:50%;border:2px solid {color}">
                <div style="flex:1">
                    <div style="font-weight:700;color:var(--text-primary)">{row['name']} {flag}</div>
                    <div style="color:var(--text-muted);font-size:0.8rem">{icon} {row.platform} · {row.city} · {row.niche}</div>
                    <div class="rank-progress">
                        <div class="fill {tier}" style="width:{bar_w}%"></div>
                    </div>
                </div>
                <div style="font-size:1.6rem;font-weight:800;color:{color};min-width:48px;text-align:right">
                    {row.trust_score}
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Score moyen par niche")
        niche_avg = df.groupby("niche")["trust_score"].mean().sort_values(ascending=True)
        fig = go.Figure(go.Bar(
            x=niche_avg.values, y=niche_avg.index, orientation="h",
            marker_color="#e53e3e", opacity=0.85,
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            margin=dict(t=10, b=10, l=10, r=10),
            height=280,
            xaxis=dict(gridcolor="#1a3050", range=[0, 100]),
            yaxis=dict(gridcolor="#1a3050"),
            hoverlabel=dict(bgcolor="#102035", bordercolor="#e53e3e", font_size=13),
        )
        st.markdown("<div class=\"chart-card\">", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("#### Score moyen par plateforme")
        plat_avg = df.groupby("platform")["trust_score"].mean()
        fig2 = go.Figure(go.Bar(
            x=plat_avg.index, y=plat_avg.values,
            marker_color=["#e53e3e", "#3b82f6", "#ef4444"],
            text=[f"{v:.0f}" for v in plat_avg.values],
            textposition="outside",
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            margin=dict(t=10, b=10),
            height=280,
            yaxis=dict(gridcolor="#1a3050", range=[0, 110]),
            xaxis=dict(gridcolor="#1a3050"),
            hoverlabel=dict(bgcolor="#102035", bordercolor="#e53e3e", font_size=13),
        )
        st.markdown("<div class=\"chart-card\">", unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — SCRAPE INSTAGRAM
# ══════════════════════════════════════════════════════════════════════════════
elif current_slug == "ig":
    from nodes.instagram_scraper import scrape_profile
    from nodes.history import record as history_record, get as history_get

    render_page_header("Scrape Instagram")
    st.markdown("### 🔎 Scrape & Score — Analyse en temps réel")
    st.markdown(
        "<div class='muted'>"
        "Entrez un username Instagram pour scraper le profil en direct, "
        "calculer son Trust Score via le pipeline ML et suivre son évolution dans le temps."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class=\"scrape-input-bar\">", unsafe_allow_html=True)
    col_in1, col_in2, col_in3 = st.columns([2, 2, 1])
    with col_in1:
        username_input = st.text_input(
            "Username Instagram", placeholder="ex: zdeffworld",
            label_visibility="visible",
        ).strip().lstrip("@")
    with col_in2:
        product_desc_scrape = st.text_input(
            "Contexte produit (optionnel)",
            placeholder="Ex: Lancement parfum Oriental...",
        )
    with col_in3:
        st.markdown("<br>", unsafe_allow_html=True)
        run_scrape = st.button("🚀 Lancer le scraping", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if run_scrape and username_input:
        with st.spinner(f"Scraping @{username_input} en cours…"):
            try:
                influencer = scrape_profile(username_input)
                st.session_state["_scraped_influencer"] = influencer
                st.session_state["_scraped_product_desc"] = product_desc_scrape
                st.session_state["_scrape_username"] = username_input
                st.session_state.pop("_scrape_error", None)
            except Exception as e:
                st.session_state["_scrape_error"] = str(e)
                st.session_state.pop("_scraped_influencer", None)

    if "._scrape_error" in st.session_state:
        st.error(f"Erreur : {st.session_state['_scrape_error']}")

    if st.session_state.get("_scrape_error"):
        st.error(f"Erreur lors du scraping : {st.session_state['_scrape_error']}")

    elif "._scraped_influencer" in st.session_state:
        pass

    if "_scraped_influencer" in st.session_state:
        inf = st.session_state["_scraped_influencer"]
        prod_desc = st.session_state.get("_scraped_product_desc", "")
        uname = st.session_state.get("_scrape_username", inf.get("_username", ""))
        posts = inf.get("_posts", [])

        # ── Run ML pipeline ────────────────────────────────────────────────
        result = score_influencer(inf, prod_desc)
        trust_score = result["trust_score"]
        breakdown = result["score_breakdown"]

        # ── Save to history ────────────────────────────────────────────────
        history_record(uname, inf, trust_score)

        color = badge_color(trust_score)
        label = badge_label(trust_score)
        flag = country_flag(inf.get("country", "TN"))

        st.divider()

        # ── Profile header ─────────────────────────────────────────────────
        col_pic, col_info, col_score = st.columns([1, 3, 1])
        with col_pic:
            pic_url = inf.get("profile_pic_url", "")
            if pic_url:
                st.image(pic_url, width=100)
            else:
                st.markdown("👤", unsafe_allow_html=True)

        with col_info:
            verified = " ✅" if inf.get("_is_verified") else ""
            st.markdown(f"""
            <div style="padding:8px 0">
                <div style="font-size:1.3rem;font-weight:700;color:var(--text-primary)">
                    {inf['name']}{verified} {flag}
                </div>
                <div style="color:var(--text-secondary);font-size:0.85rem">
                    @{uname} · 📸 Instagram · {inf['niche']}
                </div>
                <div style="color:var(--text-secondary);font-size:0.85rem;margin-top:4px">
                    {inf.get('bio','')[:120]}
                </div>
            </div>""", unsafe_allow_html=True)

        with col_score:
            st.markdown(render_score_badge(trust_score, 72), unsafe_allow_html=True)
            st.markdown(
                f"<div style='text-align:center;color:{color};font-weight:600;"
                f"font-size:0.85rem;margin-top:6px'>{label}</div>",
                unsafe_allow_html=True,
            )

        # ── Key metrics ────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)

        # Fake follower data from the pipeline result
        ff_est    = result.get("fake_follower_estimate") or 0.0
        ff_detail = result.get("fake_follower_detail") or {}
        ff_pct    = ff_detail.get("estimated_pct", round(ff_est * 100, 1))
        ff_color  = "#10b981" if ff_pct < 20 else "#ef4444" if ff_pct >= 40 else "#f59e0b"
        ff_label  = "✅ Faibles" if ff_pct < 20 else "🔴 Élevés" if ff_pct >= 40 else "⚠️ Modérés"

        m1, m2, m3, m4, m5 = st.columns(5)
        for col, title, val, metric_color in [
            (m1, "👥 Followers",       f"{inf['followers']:,}",                          "var(--gold)"),
            (m2, "❤️ Engagement",      f"{inf['engagement_rate']}%",                     "var(--gold)"),
            (m3, "🤖 Faux followers",  f"~{ff_pct}% {ff_label}",                        ff_color),
            (m4, "📸 Posts",           f"{inf['posts_count']:,}",                        "var(--gold)"),
            (m5, "📢 Pubs détectées",  f"{inf.get('_ad_count',0)}/{len(posts)}",         "var(--gold)"),
        ]:
            col.markdown(
                f'<div class="metric-card" style="border-color:{metric_color}33;--accent:{metric_color}">'
                f'<div class="label">{title}</div>'
                f'<div class="value" style="color:{metric_color}">{val}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ── Fake follower detail card ──────────────────────────────────────
        if ff_detail:
            exp_er   = ff_detail.get("expected_er", 0)
            act_er   = ff_detail.get("actual_er", 0)
            tier     = ff_detail.get("tier", "")
            sigs     = ff_detail.get("signals", {})
            er_gap   = round((1 - min(act_er / max(exp_er, 0.01), 1)) * 100)
            st.markdown(
                f'<div class="glass-card" style="margin-top:10px;border-left:4px solid {ff_color}">'
                f'<div style="color:{ff_color};font-weight:700;font-size:0.95rem">'
                f'🤖 Faux followers estimés : ~{ff_pct}%</div>'
                f'<div style="color:var(--text-secondary);font-size:0.8rem;margin-top:6px;line-height:1.7">'
                f'Tier : <b style="color:var(--text-primary)">{tier}</b> · '
                f'ER attendu : <b style="color:var(--text-primary)">{exp_er}%</b> · '
                f'ER réel : <b style="color:{ff_color}">{act_er}%</b> · '
                f'Écart d\'engagement : <b style="color:{ff_color}">{er_gap}%</b><br>'
                f'Signaux ML — Écart ER : {sigs.get("engagement_gap",0):.0%} · '
                f'IGAudit profil : {sigs.get("igaudit_profile",0):.0%} · '
                f'Anomalie ratio : {sigs.get("ratio_anomaly",0):.0%}'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)

        # ── Charts: Radar + Bar ────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        chart_col1, chart_col2 = st.columns(2)

        _has_sentiment = breakdown.get("sentiment") is not None
        if _has_sentiment:
            categories = ["Engagement","Ratio","Faux followers","Bots",
                          "Consistance","Profil","Fit produit","Sentiment"]
            maxvals = [25, 15, 15, 10, 10, 10, 10, 5]
            _sent_val = max(0.0, min(5.0, breakdown["sentiment"] + 2.5))  # shift -10..+5 → 0..5
            vals = [
                breakdown["engagement"], breakdown["ratio"], breakdown["fake_detect"],
                breakdown["bot_detect"], breakdown["consistency"], breakdown["completeness"],
                breakdown["product_match"], _sent_val,
            ]
        else:
            categories = ["Engagement","Ratio","Faux followers","Bots",
                          "Consistance","Profil","Fit produit"]
            maxvals = [25, 15, 15, 10, 10, 10, 10]
            vals = [
                breakdown["engagement"], breakdown["ratio"], breakdown["fake_detect"],
                breakdown["bot_detect"], breakdown["consistency"], breakdown["completeness"],
                breakdown["product_match"],
            ]
        pct = [round(v / m * 100) for v, m in zip(vals, maxvals)]

        with chart_col1:
            fig_radar = go.Figure(go.Scatterpolar(
                r=pct + [pct[0]],
                theta=categories + [categories[0]],
                fill="toself",
                fillcolor="rgba(229,62,62,0.15)",
                line=dict(color="#e53e3e", width=2),
                marker=dict(color="#e53e3e", size=6),
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, range=[0, 100],
                                   gridcolor="#1a3050",
                                   tickfont=dict(color="#94a3b8", size=9)),
                    angularaxis=dict(gridcolor="#1a3050",
                                    tickfont=dict(color="#94a3b8", size=10)),
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#94a3b8",
                margin=dict(t=40, b=20, l=20, r=20),
                height=320,
                title=dict(text="Radar des signaux ML", font=dict(color="#e53e3e")),
                hoverlabel=dict(bgcolor="#102035", bordercolor="#e53e3e", font_size=13),
            )
            st.markdown("<div class=\"chart-card\">", unsafe_allow_html=True)
            st.plotly_chart(fig_radar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with chart_col2:
            signal_labels = (
                ["Engagement<br>(25)", "Ratio<br>(15)", "Faux<br>(15)",
                 "Bots<br>(10)", "Posts<br>(10)", "Profil<br>(10)",
                 "Produit<br>(10)", "Sentiment<br>(±)"]
                if _has_sentiment else
                ["Engagement<br>(25)", "Ratio<br>(15)", "Faux<br>(15)",
                 "Bots<br>(10)", "Posts<br>(10)", "Profil<br>(10)",
                 "Produit<br>(10)"]
            )
            bar_colors = ["#10b981" if v >= m * 0.7 else "#f59e0b" if v >= m * 0.4 else "#ef4444"
                          for v, m in zip(vals, maxvals)]
            fig_bar = go.Figure(go.Bar(
                x=signal_labels, y=vals,
                marker_color=bar_colors,
                text=[f"{v:.1f}" for v in vals],
                textposition="outside",
            ))
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#94a3b8",
                yaxis=dict(gridcolor="#1a3050", title="Score obtenu"),
                xaxis=dict(gridcolor="#1a3050"),
                margin=dict(t=40, b=10, l=20, r=20),
                height=320,
                title=dict(text="Détail des signaux", font=dict(color="#e53e3e")),
                hoverlabel=dict(bgcolor="#102035", bordercolor="#e53e3e", font_size=13),
            )
            st.markdown("<div class=\"chart-card\">", unsafe_allow_html=True)
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── FINAL VERDICT ─────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        if trust_score >= 80:
            verdict_tier = "green"
            verdict_icon = "✅"
            verdict_title = "RECOMMANDÉ — Travaillez avec cet influenceur"
            verdict_text = (
                f"Score de confiance {trust_score}/100 · Profil authentique, "
                f"engagement solide et communauté saine. Idéal pour une campagne."
            )
        elif trust_score >= 50:
            verdict_tier = "amber"
            verdict_icon = "⚠️"
            verdict_title = "À ÉVALUER — Collaboration possible avec précautions"
            verdict_text = (
                f"Score de confiance {trust_score}/100 · Profil acceptable mais "
                f"certains signaux méritent attention. Négociez des KPIs clairs avant."
            )
        else:
            verdict_tier = "red"
            verdict_icon = "❌"
            verdict_title = "NON RECOMMANDÉ — Évitez cette collaboration"
            verdict_text = (
                f"Score de confiance {trust_score}/100 · Signaux d'alerte détectés "
                f"(faux followers, bots ou communauté toxique). Risque élevé pour votre marque."
            )

        st.markdown(
            f"""
            <div class="verdict-card tier-{verdict_tier}">
                <div class="verdict-title">{verdict_icon} {verdict_title}</div>
                <div class="verdict-text">{verdict_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Comment sentiment panel ────────────────────────────────────────────
        sent = inf.get("_comment_sentiment", {})
        st.markdown("#### 💬 Analyse des commentaires")
        if not sent or sent.get("total", 0) == 0:
            scrape_errors = sent.get("scrape_errors", 0) if sent else 0
            if scrape_errors > 0:
                st.warning("⚠️ Les commentaires n'ont pas pu être chargés depuis Instagram (limite de taux ou accès restreint). Re-scrapez dans quelques minutes.")
            else:
                st.info("ℹ️ Aucun commentaire trouvé sur les posts analysés.")
        if sent and sent.get("total", 0) > 0:
            sc      = sent.get("sentiment_score", 0.5)
            pos_r   = sent.get("positive_ratio", 0)
            neu_r   = sent.get("neutral_ratio",  0)
            neg_r   = sent.get("negative_ratio", 0)
            ins_r   = sent.get("insult_ratio",   0)
            total_c = sent.get("total", 0)
            counts  = sent.get("counts", {})

            # Label based on negative+insult presence — not on positive absence
            if ins_r >= 0.15 or neg_r >= 0.35:
                sent_tier = "red"
                sent_label = "🔴 Communauté toxique — risque image de marque"
            elif ins_r >= 0.05 or neg_r >= 0.15:
                sent_tier = "amber"
                sent_label = "🟡 Communauté mitigée — quelques commentaires négatifs"
            else:
                sent_tier = "green"
                sent_label = "🟢 Communauté saine — bon signal pour les marques"

            # Health score bar
            sc_pct = int(sc * 100)
            st.markdown(
                f"""
                <div class="sentiment-health tier-{sent_tier}">
                    <div class="sentiment-health-head">
                        <span>{sent_label}</span>
                        <strong>{sc_pct}%</strong>
                    </div>
                    <div class="sentiment-bar"><div class="fill" style="width:{sc_pct}%"></div></div>
                    <div class="muted-sm">Score de santé communautaire — analysé sur {total_c} commentaires</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # 4 cards that sum to 100%
            sc1, sc2, sc3, sc4 = st.columns(4)
            for col, val, label, tier in [
                (sc1, f"{pos_r:.0%}", "😊 Positifs", "green"),
                (sc2, f"{neu_r:.0%}", "😐 Neutres", "gold"),
                (sc3, f"{neg_r:.0%}", "😠 Négatifs", "red"),
                (sc4, f"{ins_r:.0%}", "🤬 Insultants", "red"),
            ]:
                count_key = (
                    label.split()[1]
                    .lower()
                    .rstrip("s")
                    .replace("insultant", "insult")
                    .replace("neutre", "neutral")
                    .replace("positif", "positive")
                    .replace("négatif", "negative")
                )
                col.markdown(
                    f"""
                    <div class="sentiment-card tier-{tier}">
                        <div style="font-size:1.4rem;font-weight:800;color:var(--accent)">{val}</div>
                        <div class="muted-sm">{label} · {counts.get(count_key, 0)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            col_pos, col_neg = st.columns(2)
            with col_pos:
                samples_pos = [s for s in sent.get("sample_positive", []) if len(s.strip()) > 2]
                if samples_pos:
                    st.markdown("**Exemples positifs**")
                    for s in samples_pos:
                        st.markdown(
                            f'<div class="comment-sample positive">{s}</div>',
                            unsafe_allow_html=True,
                        )
            with col_neg:
                samples_neg = sent.get("sample_negative", [])
                if samples_neg:
                    st.markdown("**Exemples négatifs / insultants**")
                    for s in samples_neg:
                        st.markdown(
                            f'<div class="comment-sample negative">{s}</div>',
                            unsafe_allow_html=True,
                        )

            st.markdown("<br>", unsafe_allow_html=True)

        # ── Posts table ────────────────────────────────────────────────────
        if posts:
            st.markdown("#### 📋 Publications scrapées")

            avg_likes = sum(p["likes"] for p in posts) / max(len(posts), 1)
            for p in posts:
                ratio      = p["likes"] / avg_likes if avg_likes > 0 else 1
                is_ad      = p.get("is_sponsored", False)
                ad_tags    = p.get("ad_tags", [])
                flag_viral = " 🔥" if ratio >= 2 else ""
                ad_label   = "🔴 PUB" if is_ad else "✅ Organique"
                ad_color   = "#ef4444" if is_ad else "#10b981"
                post_bg    = "#c9a84c" if ratio >= 2 else "#1a2e4a"
                views_val  = p.get("video_view_count") or "—"
                post_type  = "🎬 Vidéo" if p["is_video"] else "🖼️ Photo"

                tags_html = ""
                if ad_tags and ad_tags != ["[instagram_native]"]:
                    tags_str = " ".join(ad_tags[:4])
                    tags_html = f'<span class="post-pill red">{tags_str}</span>'
                elif ad_tags == ["[instagram_native]"]:
                    tags_html = '<span class="post-pill red">Instagram Branded Content</span>'

                # Single-line <a> tag avoids Streamlit markdown parser breaking the HTML
                link_html = f'<a href="{p["url"]}" target="_blank" style="color:var(--gold);font-size:0.75rem;margin-left:auto;text-decoration:none">→ Voir</a>'

                viral_class = "viral" if ratio >= 2 else ""
                ad_pill_cls = "red" if is_ad else "green"

                st.markdown(
                    f'<div class="post-card {viral_class}">'
                    f'<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">'
                    f'<span style="color:var(--text-muted);font-size:0.8rem;min-width:78px">{p["date"][:10]}</span>'
                    f'<span style="color:var(--text-primary)">{post_type}{flag_viral}</span>'
                    f'<span style="color:var(--green)">❤️ {p["likes"]:,}</span>'
                    f'<span style="color:var(--blue)">💬 {p["comments"]}</span>'
                    f'<span style="color:var(--text-muted)">👁️ {views_val}</span>'
                    f'<span style="color:{ad_color};font-weight:600;font-size:0.8rem">{ad_label}</span>'
                    f'{tags_html}'
                    f'{link_html}'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

        # ── Tracking curve ─────────────────────────────────────────────────
        st.markdown("#### 📈 Courbe de tracking — Trust Score dans le temps")
        history = history_get(uname)

        if len(history) >= 2:
            hist_df = pd.DataFrame(history)
            hist_df["timestamp"] = pd.to_datetime(hist_df["timestamp"])
            hist_df = hist_df.sort_values("timestamp")

            fig_track = go.Figure()
            fig_track.add_trace(go.Scatter(
                x=hist_df["timestamp"],
                y=hist_df["trust_score"],
                mode="lines+markers+text",
                name="Trust Score",
                line=dict(color="#e53e3e", width=3),
                marker=dict(size=10, color="#e53e3e",
                            line=dict(color="#0b1829", width=2)),
                text=hist_df["trust_score"].astype(str),
                textposition="top center",
                textfont=dict(color="#e53e3e", size=12),
            ))
            fig_track.add_hrect(y0=80, y1=100, fillcolor="#10b981", opacity=0.07,
                                annotation_text="Certifié", annotation_position="right",
                                annotation_font_color="#10b981")
            fig_track.add_hrect(y0=50, y1=80, fillcolor="#f59e0b", opacity=0.07,
                                annotation_text="À surveiller", annotation_position="right",
                                annotation_font_color="#f59e0b")
            fig_track.add_hrect(y0=0, y1=50, fillcolor="#ef4444", opacity=0.07,
                                annotation_text="Suspect", annotation_position="right",
                                annotation_font_color="#ef4444")
            fig_track.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#94a3b8",
                xaxis=dict(title="Date", gridcolor="#1a3050"),
                yaxis=dict(title="Trust Score", gridcolor="#1a3050",
                           range=[0, 105]),
                margin=dict(t=20, b=20, l=20, r=80),
                height=300,
                hovermode="x unified",
                hoverlabel=dict(bgcolor="#102035", bordercolor="#e53e3e", font_size=13),
            )
            st.markdown("<div class=\"chart-card\">", unsafe_allow_html=True)
            st.plotly_chart(fig_track, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Followers trend as secondary chart
            fig_fol = go.Figure()
            fig_fol.add_trace(go.Scatter(
                x=hist_df["timestamp"],
                y=hist_df["followers"],
                mode="lines+markers",
                name="Followers",
                line=dict(color="#3b82f6", width=2),
                marker=dict(size=7, color="#3b82f6"),
                fill="tozeroy",
                fillcolor="rgba(59,130,246,0.08)",
            ))
            fig_fol.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#94a3b8",
                xaxis=dict(title="Date", gridcolor="#1a3050"),
                yaxis=dict(title="Followers", gridcolor="#1a3050"),
                margin=dict(t=10, b=20, l=20, r=20),
                height=200,
                hoverlabel=dict(bgcolor="#102035", bordercolor="#e53e3e", font_size=13),
            )
            st.markdown("<div class=\"chart-card\">", unsafe_allow_html=True)
            st.plotly_chart(fig_fol, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info(
                f"Premier scraping de @{uname} enregistré ✓ — "
                "Relancez le scraping plus tard pour voir l'évolution du Trust Score dans le temps."
            )

        # ── Save to CSV option ─────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        col_save1, col_save2 = st.columns([1, 3])
        with col_save1:
            if st.button("💾 Sauvegarder dans influencers.csv", use_container_width=True):
                csv_path = os.path.join(os.path.dirname(__file__), "data", "influencers.csv") \
                    if os.path.isfile(os.path.join(os.path.dirname(__file__), "data", "influencers.csv")) \
                    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "influencers.csv")

                existing = pd.read_csv(csv_path)
                new_row = {k: inf.get(k, "") for k in existing.columns}
                new_row["trust_score"] = trust_score
                updated = pd.concat([existing, pd.DataFrame([new_row])], ignore_index=True)
                updated.to_csv(csv_path, index=False)
                st.success(f"@{uname} ajouté à influencers.csv ✓")
                st.cache_data.clear()
        with col_save2:
            st.caption("Ajouter ce profil à la base de données pour le voir dans Découverte, Audit et Classement.")
