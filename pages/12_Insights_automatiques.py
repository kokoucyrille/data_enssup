"""Synthèse automatique des constats pour la décision ministérielle."""
import plotly.express as px
import streamlit as st

from components.footer import render_footer
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from utils.helpers import chart_insights, download_buttons, png_download_button, setup_page
from utils.indicators import (
    compute_impact_urgence,
    compute_offre_demande_insertion,
    compute_saturation_risk,
)


setup_page("Insights automatiques", "💡")
render_navbar("Insights automatiques", "Synthèse décisionnelle", "💡")
df_filtered, _ = render_sidebar()

priorites = compute_impact_urgence(df_filtered)
offre_demande = compute_offre_demande_insertion(df_filtered)
risques = compute_saturation_risk(df_filtered)

top_region = priorites.sort_values(["Impact", "Urgence"], ascending=False).index[0]
top_opportunite = offre_demande["Demande potentielle"].idxmax()
top_probleme = offre_demande["Offre de formation"].idxmin()
top_formation = risques.index[-1]

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Région prioritaire", top_region, help="Impact et urgence cumulés.")
kpi2.metric("Opportunité majeure", top_opportunite, help="Demande potentielle la plus élevée.")
kpi3.metric("Déficit d'offre", top_probleme, help="Score d'offre le plus faible.")
kpi4.metric("Formation à développer", top_formation, help="Risque proxy le plus faible.")

st.markdown("### Priorités territoriales")
treemap_df = priorites.reset_index().rename(columns={"index": "Région"})
fig = px.treemap(
    treemap_df,
    path=["Priorité", "Région"],
    values="Population_2022",
    color="Impact",
    color_continuous_scale="Blues",
    hover_data={"Urgence": ":.1f", "Population_2022": ":,.0f"},
    title="Portefeuille territorial : poids démographique et déficit structurel",
)
fig.update_layout(margin=dict(t=55, b=10, l=10, r=10), height=460)
st.plotly_chart(fig, use_container_width=True)
png_download_button(fig, "insights_priorites_territoriales", "insights_treemap")
chart_insights(
    f"{top_region} se situe en tête du portefeuille de priorités.",
    "La couleur reflète le déficit structurel et la surface représente la population.",
    "Les territoires les plus peuplés et sous-dotés nécessitent un arbitrage prioritaire.",
    "Cibler les investissements avec une validation locale des besoins en compétences.",
    "Établir une feuille de route régionale assortie d'indicateurs de réalisation.",
)

st.markdown("### Top constats et recommandations")
constats = [
    ("Opportunité", top_opportunite,
     "Consolider l'offre de formation au regard de la demande potentielle."),
    ("Problème", top_probleme,
     "Réduire le déficit d'offre par une implantation ciblée de centres."),
    ("Formation", top_formation,
     "Valider l'extension avec les entreprises avant tout investissement."),
    ("Données", "Niveau national",
     "Collecter l'insertion par filière, sexe et région pour fiabiliser la décision."),
]
insights_df = st.data_editor(
    {"Type": [row[0] for row in constats],
     "Cible": [row[1] for row in constats],
     "Recommandation": [row[2] for row in constats]},
    disabled=True,
    hide_index=True,
    use_container_width=True,
)
download_buttons(insights_df, "insights_automatiques", "insights")

render_footer()
