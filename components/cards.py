"""
components/cards.py
====================
Cartes de contenu réutilisables (recommandations stratégiques, décisions
priorisées, objectifs du projet) — rendu HTML/CSS cohérent avec assets/style.css.
"""
from typing import List

import streamlit as st

from config import PALETTE


def recommendation_card(index: int, text: str):
    color = PALETTE[index % len(PALETTE)]
    st.markdown(
        f"""<div style="padding:12px 16px;margin:8px 0;border-left:4px solid {color};
        background:#f8f9fa;border-radius:6px;font-size:14.5px;line-height:1.55;">
        <b>{index}.</b> {text}</div>""",
        unsafe_allow_html=True,
    )


def decision_card(titre: str, ou: str, justification: str, color: str = PALETTE[0]):
    st.markdown(
        f"""<div style="padding:14px 18px;margin:10px 0;border-left:5px solid {color};
        background:#f8f9fa;border-radius:6px;">
        <b style="font-size:15.5px;">{titre}</b><br>
        <span style="color:#495057;">📍 {ou}</span><br>
        <span style="color:#6c757d;font-size:13px;">📈 {justification}</span>
        </div>""",
        unsafe_allow_html=True,
    )


def objective_card(icon: str, title: str, description: str):
    st.markdown(
        f"""<div style="background:white;border-radius:10px;padding:20px;height:100%;
        box-shadow:0 1px 4px rgba(0,0,0,0.08);">
        <div style="font-size:30px;">{icon}</div>
        <div style="font-weight:700;font-size:16px;margin-top:8px;">{title}</div>
        <div style="color:#6c757d;font-size:13.5px;margin-top:6px;">{description}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def objective_grid(items: List[tuple]):
    cols = st.columns(len(items))
    for col, (icon, title, desc) in zip(cols, items):
        with col:
            objective_card(icon, title, desc)
