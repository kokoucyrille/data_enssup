"""
components/sidebar.py
======================
Rendu de la barre laterale : logo/titre du projet, rappel du contexte, puis
filtres globaux (delegues a components.filters). Les filtres ne sont affiches
que sur les pages qui en tirent une reelle valeur (show_filters=True) ; les
autres pages (Accueil, A propos, sections uniquement nationales) appellent
render_sidebar(show_filters=False) pour une interface plus sobre.
"""
import streamlit as st

from config import APP_ICON, MINISTERE, ASSETS_DIR, LOGO_FILES, NAV_SECTIONS
from components.filters import render_page_filters, apply_filters
from utils.preprocessing import clean_etablissements


def render_page_nav(current: str):
    """Petit menu de navigation textuel (5 sections) dans la sidebar, en plus du
    menu natif Streamlit, pour une lecture immediate de la structure du site."""
    st.markdown("**Navigation**")
    for slug, icon, label in NAV_SECTIONS:
        marker = "▸ " if slug == current else "&nbsp;&nbsp;"
        weight = "700" if slug == current else "400"
        opacity = "1" if slug == current else "0.72"
        st.markdown(
            f"<div style='font-size:13.5px;padding:2px 0;font-weight:{weight};opacity:{opacity};'>"
            f"{marker}{icon} {label}</div>",
            unsafe_allow_html=True,
        )
    st.markdown("<hr>", unsafe_allow_html=True)


def render_sidebar(show_filters: bool = True, current: str = ""):
    """Affiche la sidebar complete et retourne (df_etab_filtre_ou_complet, filters_dict)."""
    with st.sidebar:
        logos = [ASSETS_DIR / filename for filename in LOGO_FILES]
        available_logos = [logo for logo in logos if logo.exists()]
        if available_logos:
            st.image(str(available_logos[0]), width='stretch')
        else:
            st.markdown(f"# {APP_ICON} Togo")
        st.markdown("**Adéquation Formation-Emploi**")
        st.caption(MINISTERE)
        st.caption("Data Challenge Éducation — Défi 2 — 2026")
        st.markdown("<hr>", unsafe_allow_html=True)

        if current:
            render_page_nav(current)

        df_etab = clean_etablissements()
        if show_filters:
            filters = render_page_filters(df_etab)
            df_filtered = apply_filters(df_etab, filters)
            st.caption(f"{len(df_filtered)} / {len(df_etab)} établissements pris en compte.")
        else:
            filters = {"regions": [], "annee_range": None}
            df_filtered = df_etab

    return df_filtered, filters
