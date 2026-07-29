"""
app.py
======
Point d'entrée de l'application. Configure la page (titre, icône, layout, CSS
personnalisé) puis redirige immédiatement vers la page d'accueil du tableau de
bord (pages/1_Accueil.py), qui porte tout le contenu de la page de garde.
"""
import streamlit as st

from config import APP_TITLE, APP_ICON, CSS_PATH

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide", initial_sidebar_state="expanded")

if CSS_PATH.exists():
    st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

st.switch_page("pages/1_Accueil.py")
