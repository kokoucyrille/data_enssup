"""
components/navbar.py
=====================
Fil d'ariane / en-tête de page affiché en haut de chaque page du tableau de bord.
"""
import streamlit as st


def render_navbar(title: str, section_number: str = "", icon: str = "📄"):
    """Affiche un en-tête de page cohérent : icône + titre + numéro de section
    (référence au notebook source, pour la traçabilité méthodologique)."""
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f"# {icon} {title}")
    with col2:
        if section_number:
            st.markdown(
                f"<div style='text-align:right;padding-top:18px;color:#6c757d;font-size:13px'>"
                f"§ {section_number}</div>", unsafe_allow_html=True,
            )
    st.markdown("<hr style='margin-top:0;margin-bottom:1.2rem;border-color:#e9ecef'>", unsafe_allow_html=True)
