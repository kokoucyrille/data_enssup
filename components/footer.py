"""
components/footer.py
=====================
Pied de page commun, affiché en fin de chaque page.
"""
import streamlit as st

from config import ASSETS_DIR, AUTHOR, INSTITUTION, LOGO_FILES, MINISTERE


def render_footer():
    st.divider()
    logos = [ASSETS_DIR / filename for filename in LOGO_FILES]
    available_logos = [str(logo) for logo in logos if logo.exists()]
    if available_logos:
        columns = st.columns(len(available_logos))
        for column, logo in zip(columns, available_logos):
            with column:
                st.image(logo, use_container_width=True)
    st.markdown(
        f"""<div style="text-align:center;color:#9aa1a9;font-size:12.5px;padding:8px 0 20px 0;">
        🇹🇬 Tableau de bord — Adéquation Formation-Emploi au Togo · Data Challenge Éducation, Défi 2 — 2026<br>
        Auteur : {AUTHOR} · {INSTITUTION} · à destination du {MINISTERE}
        </div>""",
        unsafe_allow_html=True,
    )
