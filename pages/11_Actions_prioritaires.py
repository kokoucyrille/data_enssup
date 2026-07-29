"""Page de synthèse décisionnelle pour les ministères de l'Éducation au Togo."""
import streamlit as st

from components.cards import decision_card
from components.footer import render_footer
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from utils.helpers import download_buttons, setup_page
from utils.indicators import (
    compute_impact_urgence,
    compute_offre_demande_insertion,
    compute_saturation_risk,
)


setup_page("Actions prioritaires", "🎯")
render_navbar("Actions prioritaires", "Décision ministérielle", "🎯")
df_filtered, _ = render_sidebar()

priorites = compute_impact_urgence(df_filtered)
offre_demande = compute_offre_demande_insertion(df_filtered)
risque = compute_saturation_risk(df_filtered)

st.markdown(
    "Cette page transforme les indicateurs disponibles en un portefeuille "
    "d'actions traçables. Les données de chômage et de budget restent nationales."
)

prioritaires = priorites.sort_values(["Impact", "Urgence"], ascending=False)
regions = ", ".join(prioritaires[prioritaires["Priorité"] == "Priorité 1"].index)
if not regions:
    regions = prioritaires.index[0]

formation_a_developper = risque.index[-1]
formation_a_surveiller = risque.index[0]
secteurs = (
    df_filtered["secteur_estime"].value_counts().drop(labels="Non identifié", errors="ignore")
    .head(3).index.tolist()
)
secteurs_txt = ", ".join(secteurs) if secteurs else "À documenter"
vulnerables = prioritaires.head(2).index.tolist()

col1, col2 = st.columns(2)
with col1:
    decision_card(
        "Régions prioritaires", regions,
        "Priorités établies par le croisement du déficit structurel et de "
        "l'urgence démographique.", "#D64545",
    )
    decision_card(
        "Formations à développer", formation_a_developper,
        "Catégorie présentant le risque structurel proxy le plus faible dans "
        "le périmètre retenu.", "#005BAC",
    )
    decision_card(
        "Secteurs porteurs", secteurs_txt,
        "Secteurs les plus représentés dans l'offre filtrée ; validation avec "
        "les besoins employeurs recommandée.", "#2C7BE5",
    )
with col2:
    decision_card(
        "Populations vulnérables", ", ".join(vulnerables),
        "Territoires cumulant une couverture relative faible et une pression "
        "de demande élevée.", "#F4B942",
    )
    decision_card(
        "Formation à surveiller", formation_a_surveiller,
        "Risque de saturation structurel le plus élevé : ne pas étendre sans "
        "enquête d'insertion par filière.", "#D64545",
    )
    decision_card(
        "Impact attendu", "Accès, équité et employabilité",
        "Une meilleure allocation territoriale doit augmenter la couverture et "
        "réduire les déséquilibres de l'offre.", "#0B6E4F",
    )

st.markdown("### Recommandations stratégiques")
st.markdown(
    "1. Programmer l'extension des centres dans les régions Priorité 1.\n"
    "2. Co-construire les nouveaux curricula avec les entreprises et collectivités.\n"
    "3. Lancer une enquête annuelle d'insertion par filière, sexe et région.\n"
    "4. Publier un suivi trimestriel des actions et des indicateurs d'impact."
)

st.markdown("### Base de décision exportable")
export_df = prioritaires.join(offre_demande, how="left")
st.dataframe(export_df.round(1), use_container_width=True)
download_buttons(export_df, "actions_prioritaires", "actions_prioritaires")

render_footer()
