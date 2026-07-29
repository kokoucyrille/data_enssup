"""
components/metrics.py
======================
Rendu de cartes de métriques (KPI) en grille, au-dessus des st.metric natifs de
Streamlit, pour un rendu homogène façon Power BI sur l'ensemble des pages.
"""
from typing import List, Tuple

import streamlit as st


def metric_row(metrics: List[Tuple[str, str, str]]):
    """Affiche une rangée de st.metric. `metrics` = liste de tuples
    (label, valeur, delta_ou_aide)."""
    cols = st.columns(len(metrics))
    for col, (label, value, helptext) in zip(cols, metrics):
        with col:
            st.metric(label, value, help=helptext or None)


def kpi_card(label: str, value: str, icon: str = "📌", color: str = "#005BAC",
             delta: str = "", helptext: str = ""):
    """Carte KPI stylée en HTML/CSS (utilisée pour les mises en avant fortes,
    ex. page d'accueil, Policy Dashboard)."""
    st.markdown(
        f"""
        <div style="background:white;border-radius:10px;padding:18px 16px;
                    border-top:4px solid {color};box-shadow:0 1px 4px rgba(0,0,0,0.08);text-align:center;">
            <div style="font-size:26px;">{icon}</div>
            <div style="font-size:24px;font-weight:700;color:{color};margin-top:4px;">{value}</div>
            <div style="font-size:12.5px;color:#6c757d;margin-top:2px;" title="{helptext}">{label}</div>
            <div style="font-size:12px;color:{color};font-weight:650;margin-top:5px;">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_row(items: List[Tuple[str, str, str, str]]):
    """Rangée de kpi_card. `items` = liste de tuples (label, value, icon, color)."""
    cols = st.columns(len(items))
    for col, (label, value, icon, color) in zip(cols, items):
        with col:
            kpi_card(label, value, icon, color)
