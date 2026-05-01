import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys, os
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

st.set_page_config(
    page_title="TrustInflu",
    page_icon="🇹🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS ──────────────────────────────────────────────────────────────
with open(os.path.join(os.path.dirname(__file__), "static", "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_influencers():
    return pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "influencers.csv"))

@st.cache_data
def load_brands():
    return pd.read_csv(os.path.join(os.path.dirname(__file__), "data", "brands.csv"))

df = load_influencers()
brands_df = load_brands()

# ── Helpers ──────────────────────────────────────────────────────────────────
def badge_color(score):
    if score >= 80: return "#22c55e"
    if score >= 50: return "#eab308"
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
    color = badge_color(score)
    return f"""<div style="width:{size}px;height:{size}px;border-radius:50%;
        background:rgba(0,0,0,0.2);border:3px solid {color};
        display:flex;align-items:center;justify-content:center;
        font-size:{size//3}px;font-weight:bold;color:{color};margin:auto">
        {score}</div>"""

def render_influencer_card(row):
    color = badge_color(row.trust_score)
    flag = country_flag(row.country)
    icon = platform_icon(row.platform)
    st.markdown(f"""
    <div style="background:#1a2e4a;border:1px solid {color}33;border-radius:12px;
                padding:16px;margin-bottom:8px;border-left:4px solid {color}">
        <div style="display:flex;align-items:center;gap:12px">
            <img src="{row.profile_pic_url}" style="width:52px;height:52px;border-radius:50%;border:2px solid {color}">
            <div style="flex:1">
                <div style="font-weight:700;color:#e2e8f0;font-size:1rem">{row['name']} {flag}</div>
                <div style="color:#94a3b8;font-size:0.8rem">{icon} {row.platform} · {row.city} · {row.niche}</div>
                <div style="color:#94a3b8;font-size:0.8rem">👥 {row.followers:,} · ❤️ {row.engagement_rate}%</div>
            </div>
            <div style="text-align:center">
                {render_score_badge(row.trust_score, 52)}
                <div style="color:{color};font-size:0.7rem;margin-top:4px">{badge_label(row.trust_score)}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style="text-align:center;padding:12px 0">
        <div style="font-size:1.6rem;font-weight:800;color:#c9a84c">🇹🇳 TrustInflu</div>
        <div style="color:#64748b;font-size:0.75rem;margin-top:4px">Powered for the Maghreb market</div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    page = st.radio("Navigation", [
        "🏠 Accueil",
        "🔍 Découverte",
        "📊 Audit",
        "🏢 Brand Match",
        "🏆 Classement",
    ], label_visibility="collapsed")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — ACCUEIL
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Accueil":
    st.markdown("""
    <div style="text-align:center;padding:40px 0 20px">
        <div style="font-size:2.8rem;font-weight:800;color:#c9a84c">🇹🇳 TrustInflu</div>
        <div style="font-size:1.1rem;color:#94a3b8;margin-top:8px">
            La première plateforme de confiance pour les influenceurs du Maghreb
        </div>
        <div style="font-size:0.85rem;color:#475569;margin-top:4px">
            منصة التحقق من المؤثرين للسوق التونسي والمغاربي
        </div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    total = len(df)
    certified = len(df[df.trust_score >= 80])
    suspect = len(df[df.trust_score < 50])
    avg_score = int(df.trust_score.mean())

    for col, val, label, color in [
        (c1, total, "Influenceurs", "#c9a84c"),
        (c2, certified, "🟢 Certifiés", "#22c55e"),
        (c3, suspect, "🔴 Suspects", "#ef4444"),
        (c4, avg_score, "Score moyen", "#c9a84c"),
    ]:
        col.markdown(f"""<div style="background:#1a2e4a;border-radius:12px;padding:20px;
            text-align:center;border:1px solid {color}33">
            <div style="font-size:2rem;font-weight:800;color:{color}">{val}</div>
            <div style="color:#94a3b8;font-size:0.85rem">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Distribution des Trust Scores")
        fig = go.Figure(go.Histogram(
            x=df["trust_score"], nbinsx=15,
            marker_color="#c9a84c", opacity=0.85,
        ))
        fig.update_layout(
            paper_bgcolor="#112240", plot_bgcolor="#112240",
            font_color="#e2e8f0", margin=dict(t=20, b=20, l=20, r=20),
            xaxis=dict(title="Trust Score", gridcolor="#1e3a5f"),
            yaxis=dict(title="Nombre", gridcolor="#1e3a5f"),
            height=280,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Répartition par niche")
        niche_counts = df["niche"].value_counts()
        fig2 = go.Figure(go.Pie(
            labels=niche_counts.index, values=niche_counts.values,
            hole=0.5,
            marker=dict(colors=["#c9a84c","#1e88e5","#22c55e","#ef4444",
                                 "#a855f7","#f97316","#06b6d4","#e2e8f0"]),
        ))
        fig2.update_layout(
            paper_bgcolor="#112240", font_color="#e2e8f0",
            margin=dict(t=20, b=20, l=20, r=20), height=280,
            showlegend=True, legend=dict(font=dict(size=10)),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Comment ça marche ?")
    steps = [
        ("1️⃣", "Entrez un nom d'influenceur ou importez une liste CSV"),
        ("2️⃣", "Notre pipeline LangGraph analyse le profil en 5 étapes"),
        ("3️⃣", "4 modèles ML calculent un Trust Score 0–100"),
        ("4️⃣", "Sélectionnez votre marque et obtenez les meilleurs matchs"),
    ]
    cols = st.columns(4)
    for col, (num, text) in zip(cols, steps):
        col.markdown(f"""<div style="background:#1a2e4a;border-radius:10px;padding:16px;
            text-align:center;border:1px solid #c9a84c33;height:100px">
            <div style="font-size:1.5rem">{num}</div>
            <div style="color:#94a3b8;font-size:0.8rem;margin-top:8px">{text}</div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — DÉCOUVERTE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Découverte":
    st.markdown("### 🔍 Découverte des influenceurs")

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

    filtered = df.copy()
    if niche_filter != "Toutes":
        filtered = filtered[filtered["niche"] == niche_filter]
    if region_filter != "Toutes":
        filtered = filtered[filtered["city"] == region_filter]
    if platform_filter != "Toutes":
        filtered = filtered[filtered["platform"] == platform_filter]
    filtered = filtered[filtered["trust_score"] >= min_score]
    filtered = filtered.sort_values("trust_score", ascending=False)

    st.markdown(f"<div style='color:#94a3b8;margin-bottom:12px'>{len(filtered)} influenceur(s) trouvé(s)</div>",
                unsafe_allow_html=True)

    cols = st.columns(2)
    for i, (_, row) in enumerate(filtered.iterrows()):
        with cols[i % 2]:
            render_influencer_card(row)
            if st.button("Voir l'audit complet →", key=f"audit_{row['id']}"):
                st.session_state["audit_id"] = row["id"]
                st.session_state["page_override"] = "📊 Audit"
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — AUDIT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Audit":
    st.markdown("### 📊 Audit détaillé")

    names = df["name"].tolist()
    default_idx = 0
    if "audit_id" in st.session_state:
        ids = df["id"].tolist()
        if st.session_state["audit_id"] in ids:
            default_idx = ids.index(st.session_state["audit_id"])

    selected_name = st.selectbox("Choisir un influenceur", names, index=default_idx)
    row = df[df["name"] == selected_name].iloc[0]

    col1, col2 = st.columns([1, 2])

    with col1:
        color = badge_color(row.trust_score)
        flag = country_flag(row.country)
        icon = platform_icon(row.platform)
        st.markdown(f"""
        <div style="background:#1a2e4a;border-radius:12px;padding:24px;text-align:center;
                    border:2px solid {color}">
            <img src="{row.profile_pic_url}" style="width:80px;height:80px;border-radius:50%;
                 border:3px solid {color};margin-bottom:12px">
            <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0">{row['name']} {flag}</div>
            <div style="color:#94a3b8;margin:4px 0">{icon} {row.platform} · {row.city}</div>
            <div style="color:#c9a84c;font-size:0.85rem">{row.niche}</div>
            <br>
            {render_score_badge(row.trust_score, 72)}
            <div style="color:{color};font-weight:600;margin-top:8px">{badge_label(row.trust_score)}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#1a2e4a;border-radius:10px;padding:16px">
            <div style="color:#94a3b8;font-size:0.8rem">ABONNÉS</div>
            <div style="color:#c9a84c;font-size:1.4rem;font-weight:700">{row.followers:,}</div>
            <div style="color:#94a3b8;font-size:0.8rem;margin-top:8px">ENGAGEMENT</div>
            <div style="color:#c9a84c;font-size:1.4rem;font-weight:700">{row.engagement_rate}%</div>
            <div style="color:#94a3b8;font-size:0.8rem;margin-top:8px">PUBLICATIONS</div>
            <div style="color:#c9a84c;font-size:1.4rem;font-weight:700">{row.posts_count:,}</div>
            <div style="color:#94a3b8;font-size:0.8rem;margin-top:8px">ANCIENNETÉ</div>
            <div style="color:#c9a84c;font-size:1.4rem;font-weight:700">{row.account_age_months} mois</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        from nodes.trust_score_node import trust_score_node, get_tier, engagement_score
        from nodes.state import InfluencerState

        inf = row.to_dict()
        fake_prob = max(0.0, min(1.0, 1.0 - row.trust_score / 100 * 1.3))

        state: InfluencerState = {
            "influencer": inf,
            "fake_probability": fake_prob,
            "bot_score": None,
            "product_match_score": None,
            "trust_score": None,
            "trust_label": None,
            "score_breakdown": None,
            "recommendation": None,
            "product_description": "",
        }
        result = trust_score_node(state)
        breakdown = result["score_breakdown"]

        # Radar chart
        categories = ["Engagement", "Ratio", "Faux followers", "Consistance", "Profil", "Ancienneté"]
        maxvals = [30, 20, 25, 10, 10, 5]
        vals = [breakdown["engagement"], breakdown["ratio"], breakdown["fake_detect"],
                breakdown["consistency"], breakdown["completeness"], breakdown["age"]]
        pct = [round(v/m*100) for v, m in zip(vals, maxvals)]

        fig = go.Figure(go.Scatterpolar(
            r=pct + [pct[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(201,168,76,0.15)",
            line=dict(color="#c9a84c", width=2),
            marker=dict(color="#c9a84c", size=6),
        ))
        fig.update_layout(
            polar=dict(
                bgcolor="#112240",
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1e3a5f",
                                tickfont=dict(color="#94a3b8", size=9)),
                angularaxis=dict(gridcolor="#1e3a5f", tickfont=dict(color="#e2e8f0", size=10)),
            ),
            paper_bgcolor="#1a2e4a", font_color="#e2e8f0",
            margin=dict(t=30, b=30), height=320,
            title=dict(text="Analyse radar des signaux", font=dict(color="#c9a84c")),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Bar chart per signal
        signal_labels = ["Engagement<br>(30pts)", "Ratio F/S<br>(20pts)",
                         "Faux<br>(25pts)", "Posts<br>(10pts)",
                         "Profil<br>(10pts)", "Âge<br>(5pts)"]
        colors = ["#22c55e" if v >= m*0.7 else "#eab308" if v >= m*0.4 else "#ef4444"
                  for v, m in zip(vals, maxvals)]

        fig2 = go.Figure(go.Bar(
            x=signal_labels, y=vals,
            marker_color=colors, text=[f"{v:.1f}" for v in vals],
            textposition="outside",
        ))
        fig2.update_layout(
            paper_bgcolor="#1a2e4a", plot_bgcolor="#1a2e4a",
            font_color="#e2e8f0",
            yaxis=dict(gridcolor="#1e3a5f", title="Score obtenu"),
            xaxis=dict(gridcolor="#1e3a5f"),
            margin=dict(t=20, b=10), height=240,
            title=dict(text="Détail des signaux", font=dict(color="#c9a84c")),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Bio
    st.markdown(f"""
    <div style="background:#1a2e4a;border-radius:10px;padding:16px;margin-top:8px;
                border-left:4px solid #c9a84c">
        <div style="color:#94a3b8;font-size:0.8rem;margin-bottom:4px">BIO</div>
        <div style="color:#e2e8f0">{row.bio}</div>
    </div>""", unsafe_allow_html=True)

    # Clear cached recommendation when influencer changes
    if st.session_state.get("_last_audit_name") != selected_name:
        st.session_state.pop("_ai_recommendation", None)
        st.session_state.pop("_ai_pipeline_done", None)
        st.session_state["_last_audit_name"] = selected_name

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🤖 Analyse IA — Pipeline LangGraph")

    product_desc = st.text_input(
        "🏷️ Contexte produit / campagne (optionnel)",
        placeholder="Ex: Lancement d'un nouveau yaourt Délice Maghreb...",
        key="product_desc_input",
    )

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
            ("📊", "Trust Score", "6 signaux ML"),
            ("✨", "Rapport Claude", "claude-haiku-4-5"),
        ]
        cols_p = st.columns(5)
        for col_p, (icon, label, model_lbl) in zip(cols_p, pipeline_steps):
            col_p.markdown(f"""
            <div style="text-align:center;background:#0d2137;border-radius:8px;padding:10px 6px;
                        border:1px solid #22c55e55">
                <div style="font-size:1.2rem">{icon}</div>
                <div style="color:#22c55e;font-size:0.72rem;font-weight:600;margin:4px 0">{label}</div>
                <div style="color:#475569;font-size:0.6rem">{model_lbl}</div>
                <div style="color:#22c55e;font-size:0.7rem;margin-top:4px">✓ OK</div>
            </div>""", unsafe_allow_html=True)

        rec = st.session_state.get("_ai_recommendation", "")
        has_key = bool(os.environ.get("OPENROUTER_API_KEY"))
        badge = ('<span style="background:#c9a84c22;color:#c9a84c;padding:2px 8px;border-radius:10px;'
                 'font-size:0.7rem;margin-left:8px">Claude Haiku 4.5</span>' if has_key else
                 '<span style="background:#47556922;color:#94a3b8;padding:2px 8px;border-radius:10px;'
                 'font-size:0.7rem;margin-left:8px">Fallback ML</span>')
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a2e4a,#112240);border-radius:12px;
                    padding:20px;margin-top:14px;border:1px solid #c9a84c55;
                    border-left:4px solid #c9a84c">
            <div style="display:flex;align-items:center;margin-bottom:12px">
                <span style="color:#c9a84c;font-weight:700;font-size:0.9rem">RECOMMANDATION</span>
                {badge}
            </div>
            <div style="color:#e2e8f0;font-size:1rem;line-height:1.75">{rec}</div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — BRAND MATCH
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏢 Brand Match":
    st.markdown("### 🏢 Brand Match — Trouvez vos influenceurs idéaux")

    col1, col2 = st.columns([1, 2])
    with col1:
        brand_name = st.selectbox("Marque tunisienne", brands_df["name"].tolist())
        brand = brands_df[brands_df["name"] == brand_name].iloc[0]

        st.markdown(f"""
        <div style="background:#1a2e4a;border-radius:10px;padding:16px;margin-top:8px;
                    border:1px solid #c9a84c44">
            <div style="font-weight:700;color:#c9a84c">{brand['name']}</div>
            <div style="color:#94a3b8;font-size:0.8rem">{brand['sector']}</div>
            <div style="color:#e2e8f0;margin-top:8px;font-size:0.85rem">{brand['description']}</div>
            <div style="margin-top:8px">
                {''.join([f'<span style="background:#c9a84c22;color:#c9a84c;padding:2px 8px;border-radius:10px;font-size:0.75rem;margin-right:4px">{n.strip()}</span>'
                          for n in brand['target_niches'].split(',')])}
            </div>
        </div>""", unsafe_allow_html=True)

    with col2:
        target_niches = [n.strip() for n in brand["target_niches"].split(",")]
        matched = df[df["niche"].isin(target_niches)].copy()
        matched = matched.sort_values("trust_score", ascending=False).head(5)

        st.markdown(f"**Top influenceurs recommandés pour {brand_name}**")
        for i, (_, row) in enumerate(matched.iterrows()):
            medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
            color = badge_color(row.trust_score)
            flag = country_flag(row.country)
            icon = platform_icon(row.platform)
            st.markdown(f"""
            <div style="background:#1a2e4a;border-radius:10px;padding:14px;margin-bottom:8px;
                        border:1px solid {color}44;border-left:4px solid {color}">
                <div style="display:flex;align-items:center;gap:12px">
                    <div style="font-size:1.4rem">{medal}</div>
                    <img src="{row.profile_pic_url}" style="width:44px;height:44px;border-radius:50%;border:2px solid {color}">
                    <div style="flex:1">
                        <div style="font-weight:700;color:#e2e8f0">{row['name']} {flag}</div>
                        <div style="color:#94a3b8;font-size:0.8rem">{icon} {row.platform} · {row.city} · {row.niche}</div>
                    </div>
                    <div style="text-align:right">
                        <div style="font-size:1.4rem;font-weight:800;color:{color}">{row.trust_score}</div>
                        <div style="color:#94a3b8;font-size:0.7rem">Trust Score</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — CLASSEMENT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏆 Classement":
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
        flag = country_flag(row.country)
        icon = platform_icon(row.platform)
        bar_w = int(row.trust_score)
        st.markdown(f"""
        <div style="background:#1a2e4a;border-radius:10px;padding:14px;margin-bottom:8px;
                    border:1px solid {color}33">
            <div style="display:flex;align-items:center;gap:14px">
                <div style="font-size:1.5rem;width:32px;text-align:center">{medals[i]}</div>
                <img src="{row.profile_pic_url}" style="width:46px;height:46px;border-radius:50%;border:2px solid {color}">
                <div style="flex:1">
                    <div style="font-weight:700;color:#e2e8f0">{row['name']} {flag}</div>
                    <div style="color:#94a3b8;font-size:0.8rem">{icon} {row.platform} · {row.city} · {row.niche}</div>
                    <div style="background:#0a1628;border-radius:4px;height:6px;margin-top:6px">
                        <div style="background:{color};width:{bar_w}%;height:6px;border-radius:4px"></div>
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
            marker_color="#c9a84c", opacity=0.85,
        ))
        fig.update_layout(
            paper_bgcolor="#1a2e4a", plot_bgcolor="#1a2e4a",
            font_color="#e2e8f0", margin=dict(t=10, b=10, l=10, r=10), height=280,
            xaxis=dict(gridcolor="#1e3a5f", range=[0, 100]),
            yaxis=dict(gridcolor="#1e3a5f"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Score moyen par plateforme")
        plat_avg = df.groupby("platform")["trust_score"].mean()
        fig2 = go.Figure(go.Bar(
            x=plat_avg.index, y=plat_avg.values,
            marker_color=["#c9a84c", "#1e88e5", "#ef4444"],
            text=[f"{v:.0f}" for v in plat_avg.values],
            textposition="outside",
        ))
        fig2.update_layout(
            paper_bgcolor="#1a2e4a", plot_bgcolor="#1a2e4a",
            font_color="#e2e8f0", margin=dict(t=10, b=10), height=280,
            yaxis=dict(gridcolor="#1e3a5f", range=[0, 110]),
        )
        st.plotly_chart(fig2, use_container_width=True)
