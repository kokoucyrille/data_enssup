"""
pages/3_Analyse_Territoriale.py
================================
Reproduit les sections 4 (cartographie de l'offre), 10 (théorie des graphes) et
21 (carte nationale des priorités) du notebook.
"""
import streamlit as st
import plotly.express as px
from streamlit_folium import st_folium

from utils.helpers import setup_page, story_box, download_buttons
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.footer import render_footer
from config import REGION_COLORS
from utils.preprocessing import clean_etablissements
from utils.indicators import compute_cover_df, compute_impact_urgence
from utils.map_utils import build_map_etablissements, build_map_priorities
from utils.graph_utils import (
    build_graph_region_categorie, plotly_graph_region_categorie,
    build_graph_territorial, plotly_graph_territorial,
    build_graph_etab_villes, plotly_graph_etab_villes,
    build_global_pyvis_html,
)

setup_page("Analyse Territoriale", "🗺️")
render_navbar("Analyse Territoriale — Cartographie & Théorie des graphes", "4, 10 & 21", "🗺️")
df_filtered, filters = render_sidebar()

df_etab = clean_etablissements()
cover_df = compute_cover_df()

tab1, tab2, tab3, tab4 = st.tabs(["4. Cartographie de l'offre", "10. Théorie des graphes",
                                   "10.4 Graphe global interactif", "21. Carte des priorités"])

# ------------------------------------------------------------------
# 4. Cartographie de l'offre
# ------------------------------------------------------------------
with tab1:
    st.markdown("### 4.1 Répartition régionale — régions bien couvertes vs sous-dotées")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(cover_df.sort_values("nb_etablissements", ascending=False), x="region", y="nb_etablissements",
                     color="region", color_discrete_map=REGION_COLORS, text="nb_etablissements",
                     title="Nombre absolu de formations techniques par région")
        fig.update_layout(showlegend=False, height=420, margin=dict(t=60, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(cover_df, x="region", y="etab_pour_100k_hab", color="region", color_discrete_map=REGION_COLORS,
                     text="etab_pour_100k_hab", title="⚠️ Établissements pour 100 000 habitants (RGPH-5, 2022)")
        fig.update_layout(showlegend=False, height=420, margin=dict(t=60, b=10))
        st.plotly_chart(fig, use_container_width=True)

    best_abs = cover_df.sort_values("nb_etablissements", ascending=False).iloc[0]
    best_rel = cover_df.iloc[0]
    worst_rel = cover_df.iloc[-1]
    story_box(
        f"Région la mieux dotée en absolu : <b>{best_abs['region']}</b> ({int(best_abs['nb_etablissements'])} "
        f"établissements). Rapportée à la population, la région la mieux dotée est <b>{best_rel['region']}</b> "
        f"et la plus sous-dotée est <b>{worst_rel['region']}</b> — l'écart entre volume absolu et couverture "
        "relative est un premier signal de déséquilibre territorial.", "info"
    )

    st.markdown("### 4.2 Carte interactive des établissements de formation technique")
    m = build_map_etablissements(df_filtered)
    st_folium(m, use_container_width=True, height=580, key="map_etab")
    story_box(
        f"{len(df_filtered)} établissements affichés selon les filtres actifs (sur {len(df_etab)} au total). "
        "La forte concentration autour de Lomé (région Maritime) apparaît immédiatement sur la carte.", "info"
    )

    st.markdown("### 4.3 Secteurs estimés ⚠️ par région (heuristique par mots-clés)")
    st.warning("⚠️ Le champ *spécialité* n'existe pas dans l'extraction fournie. Le secteur est **déduit du "
               "nom de l'établissement** par détection de mots-clés — une large part reste « non identifiée ».")
    import pandas as pd
    sector_region = pd.crosstab(df_etab["region_nom_bdd"], df_etab["secteur_estime"])
    fig = px.imshow(sector_region.T, text_auto=True, aspect="auto", color_continuous_scale="YlGnBu",
                     labels=dict(x="Région", y="Secteur estimé ⚠️", color="Nb établissements"),
                     title="⚠️ Secteurs estimés des formations techniques par région")
    fig.update_layout(height=480, margin=dict(t=60, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 4.4 Catégories de diplôme délivré, par région (donnée réelle)")
    cat_region = pd.crosstab(df_etab["region_nom_bdd"], df_etab["etablissement_categorie"].fillna("Non renseigné")).reset_index()
    fig = px.bar(cat_region.melt(id_vars="region_nom_bdd", var_name="categorie", value_name="nb"),
                 x="region_nom_bdd", y="nb", color="categorie", barmode="stack",
                 title="Répartition des catégories de formation technique par région",
                 labels={"region_nom_bdd": "Région", "nb": "Nombre d'établissements"})
    fig.update_layout(height=470, margin=dict(t=60, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 4.5 Dynamique de création des établissements")
    creation = df_etab.dropna(subset=["annee_creation"]).copy()
    creation["decennie"] = (creation["annee_creation"] // 10 * 10).astype(int)
    decade_counts = creation.groupby(["decennie", "region_nom_bdd"]).size().reset_index(name="nb")
    fig = px.area(decade_counts, x="decennie", y="nb", color="region_nom_bdd", color_discrete_map=REGION_COLORS,
                  title="Créations d'établissements par décennie et par région")
    fig.update_layout(height=450, margin=dict(t=60, b=10))
    st.plotly_chart(fig, use_container_width=True)
    pct_recent = (creation["annee_creation"] >= 2010).mean() * 100
    story_box(f"{(creation['annee_creation'] >= 2010).sum()} établissements sur {len(creation)} ont été créés "
              f"depuis 2010 ({pct_recent:.0f}% du parc daté) — signe d'une expansion récente de l'offre.", "success")

# ------------------------------------------------------------------
# 10. Théorie des graphes
# ------------------------------------------------------------------
with tab2:
    st.info("C'est la **valeur ajoutée distinctive** de ce tableau de bord : au-delà des statistiques "
            "descriptives, la théorie des graphes révèle la structure relationnelle du système éducatif "
            "togolais — quelles régions sont des pivots, quelles catégories dominent.")

    st.markdown("### 10.1 Graphe bipartite Région ↔ Catégorie de formation")
    G1, centralities = build_graph_region_categorie()
    st.plotly_chart(plotly_graph_region_categorie(G1, centralities), use_container_width=True)
    st.dataframe(centralities.round(3), use_container_width=True)
    pivot_regions = [n for n in centralities.sort_values("betweenness", ascending=False).index if n in REGION_COLORS][:2]
    story_box(f"Régions pivots (forte intermédiarité) : <b>{', '.join(pivot_regions)}</b>. Catégorie de "
              f"formation dominante (eigenvector max) : <b>{centralities[centralities['type']=='Catégorie']['eigenvector'].idxmax()}</b>.", "info")

    st.markdown("### 10.2 Graphe hiérarchique Région → Préfecture → Établissement")
    G2, top_prefectures = build_graph_territorial()
    st.plotly_chart(plotly_graph_territorial(G2), use_container_width=True)
    st.markdown("**Top 10 préfectures les mieux dotées :**")
    st.dataframe(top_prefectures.rename("nb_etablissements"), use_container_width=True)

    st.markdown("### 10.3 Graphe Établissements ↔ Villes (2018) — PageRank et communautés de Louvain")
    G3, pagerank, partition, result3 = build_graph_etab_villes()
    st.plotly_chart(plotly_graph_etab_villes(G3, pagerank, partition), use_container_width=True)
    st.dataframe(result3.round(4), use_container_width=True)
    story_box(f"Nombre de communautés détectées (Louvain) : {result3['communaute_louvain'].nunique()}. "
              f"Nœud au PageRank le plus élevé : <b>{result3.index[0]}</b> (secteur/ville le plus « central » du réseau).", "info")

with tab3:
    st.markdown("### 10.4 Graphe global multi-niveaux interactif")
    st.caption("Région → Préfecture → Établissement de formation technique → Catégorie → Secteur estimé. "
               "Zoomez, faites glisser les nœuds, survolez un point jaune pour voir le nom de l'établissement.")
    with st.spinner("Construction du graphe global (256 établissements)..."):
        html = build_global_pyvis_html()
    st.components.v1.html(html, height=740, scrolling=True)

# ------------------------------------------------------------------
# 21. Carte des priorités
# ------------------------------------------------------------------
with tab4:
    st.markdown("### 21. Carte nationale des priorités d'investissement")
    st.caption("Chaque établissement est colorié selon le niveau de priorité de sa région "
               "(calculé page Indice IAFE, section Priorisation).")
    impact_urgence = compute_impact_urgence()
    m2 = build_map_priorities(df_filtered, impact_urgence)
    st_folium(m2, use_container_width=True, height=580, key="map_priorities")
    st.dataframe(impact_urgence[["Impact", "Urgence", "Priorité"]].sort_values("Impact", ascending=False),
                 use_container_width=True)

render_footer()
