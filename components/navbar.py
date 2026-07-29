"""
components/navbar.py
=====================
Fil d'ariane / en-tête de page affiché en haut de chaque page du tableau de bord.
"""
import streamlit as st

from config import ASSETS_DIR, LOGO_FILES


def _header_logo(filename: str) -> None:
    """Affiche un logo sans en modifier le ratio."""
    logo_path = ASSETS_DIR / filename
    if logo_path.exists():
        st.image(str(logo_path), width=88)


def render_navbar(title: str, section_number: str = "", icon: str = "📄"):
    """Affiche un en-tête institutionnel cohérent sur toutes les pages."""
    logos = list(LOGO_FILES)
    col_rep, col_title, col_men, col_mes = st.columns([1, 5, 1.2, 1.2])
    with col_rep:
        st.markdown("<div class='republic-mark'>🇹🇬<span>République<br>togolaise</span></div>", unsafe_allow_html=True)
    with col_title:
        st.markdown(f"# {icon} {title}")
        if section_number:
            st.caption(f"Tableau de bord stratégique · § {section_number}")
    with col_men:
        if logos:
            _header_logo(logos[0])
    with col_mes:
        if len(logos) > 1:
            _header_logo(logos[1])
    st.markdown("<hr style='margin-top:0;margin-bottom:1.2rem;border-color:#e9ecef'>", unsafe_allow_html=True)
