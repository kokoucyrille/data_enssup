"""
pages/7_Chômage.py
====================
Reproduit les sections 9.1 (évolution du chômage des diplômés), 16 (analyse de
corrélation entre déterminants) et 17 (matrice Offre vs Demande par région) du
notebook.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import (
    chart_insights,
    download_buttons,
    png_download_button,
    setup_page,
    story_box,
)
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.footer import render_footer
from config import PALETTE
from utils.preprocessing import build_wb_indicators
from utils.indicators import compute_correlation_analysis, compute_offre_demande_insertion
from utils.charts import correlation_heatmap

setup_page("Chômage", "📉")
render_navbar("Chômage des diplômés — Évolution, corrélations & matrice offre/demande", "9, 16 & 17", "📉")
df_filtered, filters = render_sidebar()

wb = build_wb_indicators()

tab1, tab2, tab3 = st.tabs(["9.1 Évolution nationale", "16. Analyse de corrélation", "17. Matrice Offre vs Demande"])

# ------------------------------------------------------------------
# 9.1 Évolution nationale
# ------------------------------------------------------------------
with tab1:
    s = wb["chomage"]["chomage_diplomes_pct"].dropna().sort_index()
    fig = go.Figure(go.Scatter(x=s.index, y=s.values, mode="lines+markers",
                                line=dict(color=PALETTE[2], width=3), marker=dict(size=10)))
    fig.update_layout(title="Taux de chômage des diplômés de l'enseignement supérieur — Togo (Banque mondiale)",
                       xaxis_title="Année", yaxis_title="% de la population active diplômée", height=430, margin=dict(t=60, b=10))
    st.plotly_chart(fig, use_container_width=True)
    png_download_button(fig, "evolution_chomage_diplomes", "chomage_evolution")
    st.caption(f"Années disponibles : {list(s.index)}")
    story_box(f"Le taux oscille entre {s.min():.1f}% ({s.idxmin()}) et {s.max():.1f}% ({s.idxmax()}), sans "
              "tendance linéaire nette — la série est trop courte et trop irrégulière pour conclure à une "
              "amélioration ou une dégradation structurelle.", "warning")
    chart_insights(
        f"La série observée s'étend de {s.index.min()} à {s.index.max()}.",
        "Les variations annuelles doivent être lues avec prudence vu le faible nombre d'observations.",
        "Le chômage des diplômés est un indicateur national, non attribuable à une région ou une filière.",
        "Mettre en place un suivi annuel de l'insertion par établissement et par filière.",
        "Institutionnaliser une enquête de traçabilité des diplômés.",
    )

# ------------------------------------------------------------------
# 16. Analyse de corrélation
# ------------------------------------------------------------------
with tab2:
    st.warning(
        "⚠️ **Avertissement méthodologique.** Les séries nationales annuelles mobilisées ici ne se recoupent "
        "que sur un nombre d'années très limité (parfois 2 ou 3 années communes). Une corrélation calculée sur "
        "un si petit échantillon n'a **aucune robustesse statistique** classique — elle doit être lue comme un "
        "**indice qualitatif de co-mouvement**, jamais comme une preuve de causalité. La taille d'échantillon "
        "**N** est donc systématiquement affichée à côté du coefficient."
    )
    st.markdown(
        """
| Variable demandée | Série réellement utilisée | Nature |
|---|---|---|
| Offre | Établissements techniques cumulés par année de création | Réelle, dérivée |
| Étudiants / Diplômés | Effectifs inscrits (aucune série de diplômés n'existe) | Réelle / proxy signalé |
| Budget étudiant | Dépense annuelle par étudiant (FCFA) | Réelle |
| Investissement | Budget de l'enseignement supérieur exécuté | Réelle |
| Chômage | Chômage des diplômés du supérieur (Banque mondiale) | Réelle |
| Insertion | 100 − Chômage ⚠️ (aucune série d'insertion n'existe) | Proxy signalé |
"""
    )
    corr = compute_correlation_analysis()
    st.plotly_chart(correlation_heatmap(corr["corr_mat"], corr["n_common"],
                     "Corrélation entre déterminants (chaque cellule : r puis N années communes)"), use_container_width=True)
    story_box("Lecture : une cellule 'n&lt;3' n'est pas affichée. La paire Chômage ↔ Insertion affiche r=-1.00 "
              "par construction (Insertion = 100 - Chômage) : ce n'est pas un résultat empirique.", "warning")

    chart_insights(
        "Les coefficients n'apparaissent que lorsque trois années communes au moins sont disponibles.",
        "Les corrélations sont descriptives et ne démontrent pas de causalité.",
        "La paire chômage–insertion est exclue des résultats car elle est définie mécaniquement.",
        "Compléter les séries manquantes avant toute décision fondée sur un coefficient.",
        "Prioriser la collecte conjointe des données de budget, d'effectifs et d'insertion.",
    )

    st.markdown("#### Corrélations dominantes et variables les plus influentes")
    st.dataframe(corr["pairs_df"].style.background_gradient(subset=["r"], cmap="RdBu", vmin=-1, vmax=1).format({"r": "{:.2f}"}),
                 use_container_width=True, hide_index=True)
    if corr["pairs_df"].empty:
        st.info("Aucune paire de séries ne possède trois années communes : aucun coefficient n'est interprété.")
    else:
        top_pos, top_neg = corr["pairs_df"].iloc[0], corr["pairs_df"].iloc[-1]
        story_box(
            f"Corrélation la plus forte (positive) : <b>{top_pos['Variable 1']} ↔ {top_pos['Variable 2']}</b> "
            f"(r={top_pos['r']:.2f}, n={top_pos['n']:.0f}). Corrélation la plus forte (négative, hors paire "
            f"circulaire) : <b>{top_neg['Variable 1']} ↔ {top_neg['Variable 2']}</b> (r={top_neg['r']:.2f}, "
            f"n={top_neg['n']:.0f}).", "info"
        )
    st.dataframe(corr["influence"].round(2), use_container_width=True)

# ------------------------------------------------------------------
# 17. Matrice Offre vs Demande
# ------------------------------------------------------------------
with tab3:
    st.caption("Cette section répond à la question : existe-t-il un déséquilibre entre l'offre de formation "
               "et la demande potentielle, région par région ?")
    od = compute_offre_demande_insertion(df_filtered)
    offre_demande = od["offre_demande"]
    st.dataframe(
        offre_demande.style.background_gradient(subset=["Offre de formation", "Demande potentielle", "Insertion (proxy)"], cmap="RdYlGn").format(precision=1),
        use_container_width=True,
    )

    fig = px.imshow(offre_demande[["Offre de formation", "Demande potentielle", "Insertion (proxy)"]].T,
                     text_auto=True, aspect="auto", color_continuous_scale="RdYlGn", range_color=[0, 100],
                     labels=dict(x="Région", y="", color="Score /100"),
                     title="Heatmap Offre / Demande potentielle / Insertion (proxy) par région")
    fig.update_layout(height=380, margin=dict(t=60, b=10))
    st.plotly_chart(fig, use_container_width=True)
    png_download_button(fig, "matrice_offre_demande", "offre_demande_heatmap")
    chart_insights(
        "Les scores d'offre et d'insertion reflètent le périmètre sélectionné.",
        "La demande potentielle est estimée à partir de la population régionale.",
        "Le chômage présenté reste une référence nationale, faute de mesure régionale.",
        "Cibler l'extension de l'offre dans les régions sous-dotées et à forte demande.",
        "Valider les priorités avec les collectivités et les employeurs locaux.",
    )

    st.markdown("#### Diagnostic automatique, région par région")
    for r in offre_demande.index:
        row = offre_demande.loc[r]
        signe_o = "≥" if row["Offre de formation"] >= od["med_offre"] else "<"
        signe_d = "≥" if row["Demande potentielle"] >= od["med_demande"] else "<"
        st.markdown(
            f"**{r}** : offre {row['Offre de formation']:.1f}/100 ({signe_o} médiane {od['med_offre']:.0f}), "
            f"demande potentielle {row['Demande potentielle']:.1f}/100 ({signe_d} médiane {od['med_demande']:.0f}) "
            f"→ **{row['Diagnostic']}**"
        )
    download_buttons(offre_demande, "matrice_offre_demande", "od")

render_footer()
