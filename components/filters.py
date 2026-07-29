"""
components/filters.py
======================
Filtres globaux de la sidebar, appliqués au jeu de données des établissements de
formation technique (seul jeu à la granularité individuelle). Les filtres proposés
sont adaptés aux champs réellement disponibles dans les données fournies : Région,
Préfecture, Commune, Catégorie d'établissement, Année de création et Secteur estimé
⚠️ (proxy du "domaine de formation", cf. note méthodologique §2 — aucun champ
"spécialité" ni "sexe" n'existe au niveau établissement dans l'extraction fournie).
"""
from typing import Dict

import pandas as pd
import streamlit as st

from config import REGIONS


def render_page_filters(df_etab: pd.DataFrame) -> Dict:
    """Affiche les filtres synchronisés sous le titre de la page."""
    st.markdown("### Filtres d'analyse")
    col1, col2, col3 = st.columns(3)
    with col1:
        regions_sel = st.multiselect(
            "Région", options=REGIONS, default=REGIONS, key="filt_region"
        )

    prefectures_options = sorted(df_etab[df_etab["region_nom_bdd"].isin(regions_sel)]["prefecture_nom_bdd"].dropna().unique())
    with col2:
        prefectures_sel = st.multiselect(
            "Préfecture", options=prefectures_options, default=[],
            key="filt_prefecture",
            help="Aucune sélection = toutes les préfectures des régions choisies",
        )

    communes_options = sorted(df_etab[df_etab["region_nom_bdd"].isin(regions_sel)]["commune_nom_bdd"].dropna().unique())
    with col3:
        communes_sel = st.multiselect(
            "Commune", options=communes_options, default=[], key="filt_commune",
            help="Aucune sélection = toutes les communes",
        )

    categories_options = sorted(df_etab["etablissement_categorie"].dropna().unique())
    col4, col5, col6 = st.columns(3)
    with col4:
        categories_sel = st.multiselect(
            "Type d'établissement", options=categories_options,
            default=[], key="filt_categorie",
        )

    secteurs_options = sorted(df_etab["secteur_estime"].dropna().unique())
    with col5:
        secteurs_sel = st.multiselect(
            "Domaine de formation (estimé)", options=secteurs_options,
            default=[], key="filt_secteur",
            help="Champ estimé par mots-clés : la spécialité n'est pas fournie.",
        )

    annees_valides = df_etab["annee_creation"].dropna()
    if len(annees_valides):
        y_min, y_max = int(annees_valides.min()), int(annees_valides.max())
        with col6:
            annee_range = st.slider(
                "Année de création", min_value=y_min, max_value=y_max,
                value=(y_min, y_max), key="filt_annee",
            )
    else:
        annee_range = None

    st.caption(
        "Les filtres s'appliquent aux analyses fondées sur les établissements. "
        "Les indicateurs nationaux (budget, chômage) conservent leur périmètre national."
    )

    return {
        "regions": regions_sel, "prefectures": prefectures_sel, "communes": communes_sel,
        "categories": categories_sel, "secteurs": secteurs_sel, "annee_range": annee_range,
    }


def apply_filters(df_etab: pd.DataFrame, filters: Dict) -> pd.DataFrame:
    """Applique le dictionnaire de sélections à une copie du DataFrame établissements."""
    d = df_etab.copy()
    if filters["regions"]:
        d = d[d["region_nom_bdd"].isin(filters["regions"])]
    if filters["prefectures"]:
        d = d[d["prefecture_nom_bdd"].isin(filters["prefectures"])]
    if filters["communes"]:
        d = d[d["commune_nom_bdd"].isin(filters["communes"])]
    if filters["categories"]:
        d = d[d["etablissement_categorie"].isin(filters["categories"])]
    if filters["secteurs"]:
        d = d[d["secteur_estime"].isin(filters["secteurs"])]
    if filters["annee_range"]:
        lo, hi = filters["annee_range"]
        d = d[d["annee_creation"].isna() | d["annee_creation"].between(lo, hi)]
    return d
