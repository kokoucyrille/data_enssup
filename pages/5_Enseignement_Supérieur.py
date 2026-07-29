"""
pages/5_Enseignement_Supérieur.py
==================================
Reproduit les sections 5 (effectifs/féminisation), 6 (public vs privé), 11
(Machine Learning exploratoire) et 12 (clustering régional) du notebook.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.helpers import setup_page, story_box
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.footer import render_footer
from config import PALETTE, REGION_COLORS
from utils.preprocessing import clean_repartition_sup, build_indicateurs_sup
from utils.indicators import compute_ml_comparison, compute_clustering

setup_page("Enseignement Supérieur", "🎓")
render_navbar("Enseignement Supérieur — Effectifs, ML & Clustering", "5, 6, 11 & 12", "🎓")
_, filters = render_sidebar()

ind_wide = build_indicateurs_sup()
df_repart = clean_repartition_sup()

tab1, tab2, tab3, tab4 = st.tabs(["5. Effectifs & féminisation", "6. Public vs privé",
                                   "11. Machine Learning", "12. Clustering régional"])

# ------------------------------------------------------------------
# 5. Effectifs, féminisation, filières scientifiques
# ------------------------------------------------------------------
with tab1:
    fig = make_subplots(rows=2, cols=2, subplot_titles=(
        "Évolution des effectifs d'étudiants inscrits", "Taux de féminisation des étudiants (%)",
        "Ratio étudiants / enseignants (universités publiques)", "Filières scientifiques et technologiques"))

    s = ind_wide["effectifs_etudiants"].dropna()
    fig.add_trace(go.Scatter(x=s.index, y=s.values, mode="lines+markers", line=dict(color=PALETTE[0], width=3), fill="tozeroy"), row=1, col=1)

    s = ind_wide["taux_feminisation"].dropna()
    fig.add_trace(go.Scatter(x=s.index, y=s.values, mode="lines+markers", line=dict(color=PALETTE[2], width=3)), row=1, col=2)
    fig.add_hline(y=50, line_dash="dash", line_color="gray", row=1, col=2)

    s = ind_wide["ratio_etud_enseignant"].dropna()
    fig.add_trace(go.Bar(x=s.index.astype(str), y=s.values, marker_color=PALETTE[3]), row=2, col=1)

    s1 = ind_wide["pct_filieres_scientifiques"].dropna()
    s2 = ind_wide["pct_filles_filieres_sci"].dropna()
    fig.add_trace(go.Scatter(x=s1.index, y=s1.values, mode="lines+markers", name="% étudiants en filières sci.", line=dict(color=PALETTE[1], width=3)), row=2, col=2)
    fig.add_trace(go.Scatter(x=s2.index, y=s2.values, mode="lines+markers", name="% filles en filières sci.", line=dict(color=PALETTE[4], width=3)), row=2, col=2)

    fig.update_layout(height=760, margin=dict(t=60, b=10), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

    story_box(
        "Les effectifs et la féminisation progressent de façon continue sur la période observée, tandis que "
        "le ratio étudiants/enseignants se détend (128 → 91 entre 2016 et 2019), signe d'un effort "
        "d'encadrement. La part des filières scientifiques progresse (18,1% → 23,6%) mais reste minoritaire, "
        "et la féminisation de ces filières spécifiquement (14,7% → 15,6%) demeure très inférieure à la "
        "féminisation globale — un point d'attention pour les politiques d'orientation.", "info"
    )

# ------------------------------------------------------------------
# 6. Public vs privé
# ------------------------------------------------------------------
with tab2:
    pub_priv = df_repart.groupby(["type", "statut"])["Value"].sum().unstack(fill_value=0)
    st.dataframe(pub_priv, use_container_width=True)

    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "domain"}, {"type": "xy"}]],
                         subplot_titles=("Répartition Public / Privé", "Établissements par ville, statut et type"))
    totals_statut = df_repart.groupby("statut")["Value"].sum()
    fig.add_trace(go.Pie(labels=totals_statut.index, values=totals_statut.values,
                         marker_colors=[PALETTE[0], PALETTE[2]], hole=0.45, textinfo="label+percent"), row=1, col=1)
    city_type_statut = df_repart.groupby(["villes", "type", "statut"])["Value"].sum().reset_index()
    city_type_statut["label"] = city_type_statut["type"] + " " + city_type_statut["statut"]
    for i, lab in enumerate(city_type_statut["label"].unique()):
        d = city_type_statut[city_type_statut["label"] == lab]
        fig.add_trace(go.Bar(x=d["villes"], y=d["Value"], name=lab, marker_color=px.colors.qualitative.Set2[i % 8]), row=1, col=2)
    fig.update_layout(barmode="stack", height=470, margin=dict(t=60, b=10), title_text="Établissements d'enseignement supérieur ayant fonctionné (2018)")
    st.plotly_chart(fig, use_container_width=True)

    pct_prive = totals_statut.get("Prive", 0) / totals_statut.sum() * 100
    lome_count = int(city_type_statut[city_type_statut["villes"] == "LOMÉ"]["Value"].sum())
    story_box(f"Sur {int(df_repart['Value'].sum())} structures recensées en 2018, {pct_prive:.0f}% relèvent du "
              f"secteur privé — Lomé concentre à elle seule {lome_count} structures.", "info")

    st.markdown("### 6.1 Sunburst — hiérarchie Région → Ville → Type → Statut")
    sb = df_repart.copy()
    sb["region"] = sb["region"].fillna("Autre")
    fig = px.sunburst(sb, path=["region", "villes", "type", "statut"], values="Value",
                       color="region", color_discrete_map=REGION_COLORS,
                       title="Établissements d'enseignement supérieur — Région → Ville → Type → Statut (2018)")
    fig.update_layout(height=560, margin=dict(t=60, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------
# 11. Machine Learning
# ------------------------------------------------------------------
with tab3:
    st.warning(
        "⚠️ **Avertissement à lire avant cette section.** Le chômage des diplômés n'est connu qu'à l'échelle "
        "**nationale** et sur **6 années seulement**. Il n'existe **aucune donnée réelle** de chômage par "
        "filière, diplôme ou région. Ce qui suit est un **exercice pédagogique de bout en bout** appliqué à un "
        "échantillon de **6 observations** : les performances n'ont **aucune valeur prédictive opérationnelle**."
    )
    ml = compute_ml_comparison()
    st.markdown("#### 11.1 Jeu de données (interpolation transparente)")
    st.dataframe(ml["dataset"], use_container_width=True)

    st.markdown("#### 11.2 Comparaison de modèles (validation croisée Leave-One-Out)")
    st.dataframe(ml["results_df"], use_container_width=True, hide_index=True)
    story_box("⚠️ Avec n=6, le R² peut être négatif ou instable : ce n'est PAS un signe d'échec, mais la "
              "conséquence arithmétique attendue d'un échantillon aussi réduit. À interpréter uniquement de "
              "façon relative (quel modèle se trompe le moins), jamais en valeur absolue.", "warning")

    st.markdown("#### 11.3 Importance des variables (Random Forest)")
    fig = px.bar(ml["importance"].reset_index(), x="index", y=0, color=0, color_continuous_scale="Teal",
                 labels={"index": "Variable", "0": "Importance"},
                 title="Importance des variables — Random Forest (n=6, résultat indicatif ⚠️)")
    fig.update_layout(height=400, margin=dict(t=60, b=10), showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Conclusion : la démarche complète est fonctionnelle et reproductible, mais la donnée manquante "
               "est le facteur limitant, pas la méthode. Une vraie estimation nécessiterait une enquête de "
               "traçabilité des diplômés (tracer study) ventilée par filière, diplôme et région.")

# ------------------------------------------------------------------
# 12. Clustering régional
# ------------------------------------------------------------------
with tab4:
    st.warning("⚠️ Le Togo compte **5 régions** : ce n'est pas un échantillon statistique mais la population "
               "complète. Le clustering est un outil de regroupement visuel, pas une découverte généralisable.")
    cl = compute_clustering()
    st.dataframe(cl["clusters"].round(2), use_container_width=True)

    fig = make_subplots(rows=1, cols=3, subplot_titles=("KMeans", "DBSCAN", "Agglomerative"))
    coords = cl["coords_pca"]
    for i, method in enumerate(["KMeans", "DBSCAN", "Agglomerative"]):
        labels = cl["clusters"][method].values
        for lbl in sorted(set(labels)):
            mask = labels == lbl
            fig.add_trace(go.Scatter(x=coords[mask, 0], y=coords[mask, 1], mode="markers+text",
                                      text=[r for r, m in zip(cl["clusters"].index, mask) if m],
                                      textposition="top center", marker=dict(size=14),
                                      name=f"{method}: Cluster {lbl}" if lbl != -1 else f"{method}: Bruit",
                                      showlegend=False), row=1, col=i + 1)
    fig.update_layout(height=440, margin=dict(t=60, b=10), title_text="Segmentation des 5 régions (projection PCA)")
    st.plotly_chart(fig, use_container_width=True)
    story_box("Lecture qualitative — la Maritime se distingue nettement (volume et diversité les plus élevés, "
              "portés par Lomé), tandis que les autres régions se regroupent selon leur niveau de couverture "
              "relative et la fraîcheur de leur offre.", "info")

render_footer()
