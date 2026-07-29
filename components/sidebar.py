"""
components/sidebar.py
======================
Rendu de la sidebar : logo/titre du projet, rappel du contexte, puis filtres
globaux (délégués à components.filters).
"""
import streamlit as st

from config import APP_ICON, MINISTERE, ASSETS_DIR, LOGO_FILES
from components.filters import render_page_filters, apply_filters
from utils.preprocessing import clean_etablissements


def render_sidebar():
    """Affiche la sidebar complète et retourne (df_etab_filtre, filters_dict)."""
    logo_path = ASSETS_DIR / "logo.png"
    with st.sidebar:
        logos = [ASSETS_DIR / filename for filename in LOGO_FILES]
        available_logos = [logo for logo in logos if logo.exists()]
        if available_logos:
            st.image(str(available_logos[0]), use_container_width=True)
        elif logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        else:
            st.markdown(f"# {APP_ICON} Togo")
        st.markdown("**Adéquation Formation-Emploi**")
        st.caption(MINISTERE)
        st.caption("Data Challenge Éducation — Défi 2 — 2026")

    df_etab = clean_etablissements()
    filters = render_page_filters(df_etab)
    df_filtered = apply_filters(df_etab, filters)
    st.caption(f"{len(df_filtered)} / {len(df_etab)} établissements pris en compte.")
    return df_filtered, filters
