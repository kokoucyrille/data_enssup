"""
pages/1_Accueil.py
===================
Page de garde du tableau de bord : titre, contexte, objectifs, statistiques
globales et navigation vers les autres pages.
"""
import streamlit as st

from utils.helpers import setup_page
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.cards import objective_grid
from components.metrics import kpi_row
from components.footer import render_footer
from utils.indicators import compute_kpi
from config import AUTHOR, INSTITUTION, MINISTERE

setup_page("Accueil", "🎓")
render_navbar("Adéquation Formation-Emploi au Togo", "Pilotage ministériel", "🎓")
df_filtered, filters = render_sidebar()

# ------------------------------------------------------------------
# Bandeau principal
# ------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-banner">
        <div style="font-size:38px;font-weight:800;">🎓 🇹🇬 Adéquation Formation-Emploi au Togo</div>
        <div style="font-size:17px;margin-top:6px;opacity:0.95;">
            Data Challenge Éducation — Défi 2 — 2026 · Tableau de bord stratégique à destination du Ministère
        </div>
        <div style="font-size:14px;margin-top:14px;opacity:0.85;">
            Analyse des formations techniques, de l'enseignement supérieur, des budgets et du chômage des diplômés
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col_a, col_b = st.columns([2, 1])
with col_a:
    st.markdown("### 🎯 Objectif général")
    st.markdown(
        "Évaluer, à partir des données ouvertes disponibles, l'**adéquation entre l'offre de formation** "
        "(technique et supérieure) **et les besoins du marché de l'emploi** au Togo, afin de proposer des "
        "**recommandations stratégiques** concrètes au Ministère en charge de l'Enseignement supérieur et de "
        "la Formation technique et professionnelle."
    )
    st.markdown(
        "Ce tableau de bord combine cartographie territoriale, analyse statistique, théorie des graphes, "
        "Machine Learning exploratoire, indicateurs composites inédits (**IAFE**, successeur du FEAS) et un "
        "**Policy Dashboard** de priorisation des investissements."
    )
with col_b:
    st.markdown("### 📍 Portée")
    st.info("**5 régions administratives**\n\nMaritime · Plateaux · Centrale · Kara · Savanes")
    st.caption(f"Auteur : {AUTHOR} — {INSTITUTION}")
    st.caption(f"À destination du {MINISTERE}")

st.warning(
    "⚠️ **Avertissement méthodologique** — Une page dédiée (Note méthodologique, dans le menu **Données**) "
    "documente précisément la granularité réelle de chaque source et les limites qu'elle impose sur la portée "
    "des analyses. Chaque résultat construit sur une estimation est signalé explicitement par le symbole ⚠️."
)

st.markdown("### 🧭 Explorer le tableau de bord")
objective_grid([
    ("🗺️", "Cartographie territoriale", "Localisation des 256 établissements de formation technique et carte des priorités d'investissement."),
    ("📊", "Diagnostic statistique", "Effectifs, budgets, chômage des diplômés, indicateurs socio-éducatifs nationaux 2013-2020."),
    ("🕸️", "Théorie des graphes", "Centralités, PageRank, communautés de Louvain — structure relationnelle du système éducatif."),
])
st.write("")
objective_grid([
    ("🤖", "Machine Learning", "Modélisation exploratoire du chômage des diplômés et clustering des profils régionaux."),
    ("🧮", "Indice IAFE", "Indice d'Adéquation Formation-Emploi, pondération justifiée statistiquement (méthode CRITIC)."),
    ("🎯", "Policy Dashboard", "Priorisation Impact × Urgence, scénarios prospectifs et recommandations chiffrées."),
])

st.markdown("### 📈 Statistiques globales")
kpi = compute_kpi()
kpi_row([
    ("Formations techniques", str(kpi["Nombre de formations techniques recensées"]), "🏫", "#1B6B45"),
    ("Régions couvertes", f"{kpi['Nombre de régions couvertes (formation technique)']}/5", "🗺️", "#2E5EAA"),
    ("Préfectures couvertes", str(kpi["Nombre de préfectures couvertes"]), "📍", "#F2C744"),
    ("Universités (2018)", str(kpi["Nombre d'universités recensées (2018)"]), "🎓", "#D62839"),
])
st.write("")
kpi_row([
    ("Féminisation étudiants", f"{kpi['Taux de féminisation le plus récent (%)']}%", "👩‍🎓", "#1B6B45"),
    ("Ratio étud./enseignant", f"{kpi['Ratio étudiants/enseignants le plus récent']}:1", "👩‍🏫", "#2E5EAA"),
    ("Filières scientifiques", f"{kpi['Part des filières scientifiques la plus récente (%)']}%", "🔬", "#F2C744"),
    ("Chômage diplômés", kpi["Chômage diplômés le plus récent connu (%, année)"], "📉", "#D62839"),
])

st.markdown("### 🧩 Sommaire du tableau de bord")
st.markdown(
    """
| Page | Contenu |
|---|---|
| 📊 Données | Chargement, nettoyage, audit des valeurs manquantes, note méthodologique |
| 🗺️ Analyse Territoriale | Cartographie, couverture régionale, théorie des graphes |
| 🏫 Formations | Offre de formation technique, catégories, secteurs estimés, saturation |
| 🎓 Enseignement Supérieur | Effectifs, féminisation, ML, clustering, public/privé |
| 💰 Budgets | Budgets votés/exécutés, dépense par étudiant, chaîne Budget→Insertion |
| 📉 Chômage | Chômage des diplômés, corrélations, matrice Offre/Demande |
| 🧮 Indice IAFE | Formule, CRITIC, robustesse, classements, priorisation, scénarios |
| 🎯 Recommandations | Recommandations stratégiques et Policy Dashboard |
| ℹ️ À Propos | Sources, méthodologie, limites, pistes d'amélioration |
"""
)

render_footer()
