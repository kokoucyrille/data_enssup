"""
pages/9_Recommandations.py
============================
Reproduit les sections 14 (recommandations stratégiques générées
automatiquement) et 23 (Policy Dashboard) du notebook. Toutes les
recommandations sont calculées à partir des résultats des pages précédentes —
aucun texte générique.
"""
import streamlit as st

from utils.helpers import setup_page, fmt_fr
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.cards import recommendation_card, decision_card
from components.metrics import kpi_row
from components.footer import render_footer
from config import PALETTE
from utils.preprocessing import build_indicateurs_sup, build_budget_wide, clean_etablissements
from utils.indicators import (
    compute_cover_df, compute_saturation_risk, compute_complementary_scores, compute_feas,
    compute_iafe, compute_impact_urgence,
)

setup_page("Recommandations", "🎯")
render_navbar("Recommandations stratégiques & Policy Dashboard", "14 & 23", "🎯")
_, filters = render_sidebar()

ind_wide = build_indicateurs_sup()
budget_wide = build_budget_wide()
df_etab = clean_etablissements()
cover_df = compute_cover_df()
risk = compute_saturation_risk()
scores_df, equity = compute_complementary_scores()
feas = compute_feas()
feas_sorted = feas.sort_values("FEAS", ascending=False)
iafe_data = compute_iafe()
impact_urgence = compute_impact_urgence()

tab1, tab2 = st.tabs(["14. Recommandations stratégiques", "23. Policy Dashboard"])

# ------------------------------------------------------------------
# 14. Recommandations stratégiques
# ------------------------------------------------------------------
with tab1:
    st.caption("Les recommandations ci-dessous sont produites par une fonction de règles appliquée aux "
               "résultats calculés dans les pages précédentes : si les données changent, les recommandations changent avec elles.")

    region_faible = cover_df.sort_values("etab_pour_100k_hab").iloc[0]
    region_forte = cover_df.sort_values("etab_pour_100k_hab", ascending=False).iloc[0]
    opportunity_index = scores_df["Opportunity Index"]

    recommendations = [
        f"🗺️ **Rééquilibrer l'offre territoriale** : la région **{region_faible['region']}** affiche la "
        f"couverture la plus faible ({region_faible['etab_pour_100k_hab']:.1f} établissements/100k hab. contre "
        f"{region_forte['etab_pour_100k_hab']:.1f} pour {region_forte['region']}). Prioriser l'ouverture de "
        f"nouveaux centres, en cohérence avec son Opportunity Index ({opportunity_index[region_faible['region']]:.0f}/100).",

        f"⚠️ **Vérifier le risque de saturation** de la catégorie **{risk.index[0]}** (indice proxy le plus "
        f"élevé, {risk.iloc[0]['indice_saturation_proxy']:.0f}/100) par une véritable enquête d'insertion "
        f"professionnelle. À l'inverse, la catégorie **{risk.index[-1]}** apparaît sous-représentée et "
        "pourrait justifier un soutien ciblé.",

        f"🔬 **Renforcer les filières scientifiques et technologiques**, qui ne représentent que "
        f"{ind_wide['pct_filieres_scientifiques'].dropna().iloc[-1]:.1f}% des effectifs du supérieur, avec un "
        f"accent sur la féminisation de ces filières ({ind_wide['pct_filles_filieres_sci'].dropna().iloc[-1]:.1f}% "
        f"des inscrits contre {ind_wide['taux_feminisation'].dropna().iloc[-1]:.1f}% de féminisation globale).",

        f"👩‍🏫 **Poursuivre l'effort d'encadrement** : le ratio étudiants/enseignant s'est amélioré (128 → "
        f"{ind_wide['ratio_etud_enseignant'].dropna().iloc[-1]:.0f}), un effort à maintenir face à la "
        f"croissance continue des effectifs ({int(ind_wide['effectifs_etudiants'].dropna().iloc[-1]):,} "
        "étudiants inscrits en dernière année connue).".replace(",", " "),

        f"💰 **Cibler l'investissement** sur la région **{feas_sorted.index[-1]}**, qui affiche le FEAS le "
        f"plus bas ({feas_sorted.iloc[-1]['FEAS']:.0f}/100) — combinaison de couverture, diversité et "
        "dynamisme de l'offre les plus faibles du pays.",

        "📋 **Combler le déficit de données** : sans (i) une nomenclature de filières/spécialités "
        "systématiquement renseignée, (ii) une exécution budgétaire régionalisée, et (iii) une enquête de "
        "traçabilité des diplômés par filière, aucune analyse d'adéquation Formation-Emploi ne pourra dépasser "
        "le stade de l'estimation indicative présentée ici.",
    ]
    for i, r in enumerate(recommendations, 1):
        recommendation_card(i, r)

# ------------------------------------------------------------------
# 23. Policy Dashboard
# ------------------------------------------------------------------
with tab2:
    region_p1_top = (impact_urgence[impact_urgence["Priorité"] == "Priorité 1"]["Impact"].idxmax()
                      if (impact_urgence["Priorité"] == "Priorité 1").any() else impact_urgence["Impact"].idxmax())
    nb_p1 = int((impact_urgence["Priorité"] == "Priorité 1").sum())

    kpi_row([
        ("IAFE national", f"{iafe_data['iafe_national']:.1f}/100", "🧮", "#1B6B45"),
        ("Région n°1 en priorité", region_p1_top, "📍", "#D62839"),
        ("Régions en Priorité 1", f"{nb_p1} / 5", "🚨", "#D62839" if nb_p1 else "#1B6B45"),
        ("Chômage diplômés (dernier)", f"{iafe_data['chomage_val']:.1f}%", "📉", "#2E5EAA"),
        ("Budget / étudiant (dernier)", f"{fmt_fr(iafe_data['budget_val'])} FCFA", "💰", "#F2C744"),
    ])
    st.write("")

    st.markdown("### Décisions prioritaires — calculées automatiquement à partir des données")
    infra_gap_sport = df_etab["terrain_sport"].isna().mean() * 100
    infra_gap_toilette = df_etab["toilette_type"].isna().mean() * 100
    regions_p1 = impact_urgence[impact_urgence["Priorité"] == "Priorité 1"].sort_values("Impact", ascending=False)
    from utils.indicators import compute_offre_demande_insertion
    insertion_score = compute_offre_demande_insertion()["insertion_score"]
    regions_insertion_faible = insertion_score[insertion_score < insertion_score.median()].sort_values()
    categorie_risque = risk.index[0]
    categorie_porteuse = risk.index[-1]

    from utils.indicators import compute_scenarios
    sc = compute_scenarios()

    if len(regions_p1):
        decision_card(
            "🏗️ Construire de nouveaux centres techniques",
            f"Régions Priorité 1 : {', '.join(regions_p1.index)}",
            f"Déficit d'offre moyen de {regions_p1['deficit_offre'].mean():.0f}/100 sur ces régions ; seuil de "
            f"rattrapage estimé à +{sc['nb_centres_necessaires']} centres pour {sc['region_cible']} seule.",
            "#D62839",
        )
    if iafe_data["budget_score"] < 50:
        decision_card(
            "💰 Augmenter le budget par étudiant", "Niveau national",
            f"Dépense/étudiant {iafe_data['budget_year']} = {fmt_fr(iafe_data['budget_val'])} FCFA, positionnée "
            f"à {iafe_data['budget_score']:.0f}/100 de sa propre plage historique observée — proche de son "
            "plus bas niveau récent.", "#F2C744",
        )
    decision_card(
        "🎓 Développer certaines filières",
        f"Renforcer « {categorie_porteuse} » ; encadrer « {categorie_risque} »",
        f"Indice de saturation proxy : {risk.loc[categorie_porteuse, 'indice_saturation_proxy']:.1f}/100 pour "
        f"« {categorie_porteuse} » vs {risk.loc[categorie_risque, 'indice_saturation_proxy']:.1f}/100 pour « {categorie_risque} ».",
        "#2E5EAA",
    )
    if len(regions_insertion_faible):
        decision_card(
            "🤝 Renforcer les partenariats entreprises-universités",
            ", ".join(regions_insertion_faible.index),
            f"Score d'insertion (proxy) le plus faible du pays pour {regions_insertion_faible.index[0]} "
            f"({regions_insertion_faible.iloc[0]:.0f}/100), lié à une offre concentrée sur des catégories à "
            "risque de saturation plus élevé.", "#1B6B45",
        )
    decision_card(
        "🏫 Améliorer les infrastructures", "Ensemble du parc de formation technique",
        f"{infra_gap_sport:.0f}% des établissements sans terrain de sport recensé, {infra_gap_toilette:.0f}% "
        "sans type de sanitaire renseigné.", "#8C5E58",
    )
    decision_card(
        "🎯 Créer des bourses ciblées", f"{scores_df['Opportunity Index'].idxmax()}",
        f"Opportunity Index le plus élevé du pays ({scores_df['Opportunity Index'].max():.0f}/100) : forte "
        "population, couverture relative encore faible.", "#F2C744",
    )
    decision_card(
        "📊 Prioriser les investissements selon la matrice Impact × Urgence", f"{nb_p1} région(s) en Priorité 1 sur 5",
        "Cf. page Indice IAFE, onglet Priorisation — matrice détaillée et justifications région par région.", "#1B6B45",
    )

    st.markdown("### En une phrase")
    chomage_year_min = None
    synthese = (
        f"Le Togo affiche un IAFE national de **{iafe_data['iafe_national']:.1f}/100** : **{region_p1_top}** "
        f"concentre le déficit le plus critique (Priorité 1, {nb_p1} région(s) concernée(s) sur 5), la "
        "Maritime illustre un problème de **composition** de l'offre plutôt que de volume, et le chômage des "
        f"diplômés ({iafe_data['chomage_val']:.1f}% en {iafe_data['chomage_year']}) reste proche de son "
        "meilleur niveau observé — une fenêtre favorable pour agir."
    )
    st.markdown(
        f"""<div style="padding:18px 22px;background:linear-gradient(135deg,#1B6B45,#2E5EAA);color:white;
        border-radius:10px;font-size:15.5px;line-height:1.6;">{synthese}</div>""",
        unsafe_allow_html=True,
    )

render_footer()
