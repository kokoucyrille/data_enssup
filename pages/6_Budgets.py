"""
pages/6_Budgets.py
===================
Reproduit la section 8 du notebook : budgets de l'enseignement supérieur.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.helpers import setup_page, story_box
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.footer import render_footer
from config import PALETTE
from utils.preprocessing import build_budget_wide, build_indicateurs_sup, build_wb_indicators, build_national_table

setup_page("Budgets", "💰")
render_navbar("Budgets de l'enseignement supérieur", "8", "💰")
_, filters = render_sidebar()

budget_wide = build_budget_wide()
ind_wide = build_indicateurs_sup()
wb = build_wb_indicators()
national = build_national_table()

st.markdown("### 8.1 Budget voté vs exécuté, et poids dans le budget national")
fig = make_subplots(rows=1, cols=2, subplot_titles=("Budget votés vs exécuté (millions FCFA)", "Taux d'exécution budgétaire (%)"))
fig.add_trace(go.Bar(x=budget_wide.index.astype(str), y=budget_wide["budget_sup_vote"], name="Voté", marker_color=PALETTE[3]), row=1, col=1)
fig.add_trace(go.Bar(x=budget_wide.index.astype(str), y=budget_wide["budget_sup_execute"], name="Exécuté", marker_color=PALETTE[0]), row=1, col=1)
fig.add_trace(go.Scatter(x=budget_wide.index.astype(str), y=budget_wide["taux_execution_sup"], mode="lines+markers",
                          name="Taux d'exécution", line=dict(color=PALETTE[2], width=3)), row=1, col=2)
fig.add_hline(y=100, line_dash="dash", line_color="gray", row=1, col=2)
fig.update_layout(barmode="group", height=430, margin=dict(t=60, b=10), title_text="Exécution budgétaire de l'enseignement supérieur")
st.plotly_chart(fig, use_container_width=True)

taux_moy = budget_wide["taux_execution_sup"].mean()
story_box(f"Taux d'exécution moyen : {taux_moy:.1f}% — "
          + ("l'exécution est globalement proche ou supérieure au budget voté, signe d'un financement additionnel en cours d'année."
             if taux_moy > 95 else "une part du budget voté n'est pas consommée."), "info")

share_df = None
import pandas as pd
share_df = pd.DataFrame({
    "Budget enseign. sup.": budget_wide["budget_sup_execute"],
    "Budget éducation (hors sup.)": (budget_wide["budget_education_execute"] - budget_wide["budget_sup_execute"]).clip(lower=0),
    "Reste du budget national": (budget_wide["budget_national_execute"] - budget_wide["budget_education_execute"]).clip(lower=0),
})
fig = px.area(share_df.reset_index().melt(id_vars="Date", var_name="Poste", value_name="Montant"),
              x="Date", y="Montant", color="Poste", color_discrete_sequence=[PALETTE[0], PALETTE[1], PALETTE[4]],
              title="Décomposition du budget national exécuté (millions FCFA)")
fig.update_layout(height=440, margin=dict(t=60, b=10))
st.plotly_chart(fig, use_container_width=True)
pct_sup = (budget_wide["budget_sup_execute"] / budget_wide["budget_national_execute"] * 100).mean()
st.caption(f"L'enseignement supérieur représente en moyenne {pct_sup:.2f}% du budget national exécuté.")

st.markdown("### 8.2 Dépense publique par étudiant")
c1, c2 = st.columns(2)
with c1:
    s = ind_wide["depense_annuelle_par_etudiant_fcfa"].dropna()
    fig = px.line(x=s.index, y=s.values, markers=True, title="Dépense annuelle par étudiant (FCFA)",
                  labels={"x": "Année", "y": "FCFA"})
    fig.update_traces(line_color=PALETTE[0])
    st.plotly_chart(fig, use_container_width=True)
with c2:
    s2 = wb["depense"]["depense_etud_pct_pib_hab"].dropna().sort_index()
    fig = px.line(x=s2.index, y=s2.values, markers=True, title="Dépense publique/étudiant (% PIB/hab.) — Banque mondiale",
                  labels={"x": "Année", "y": "%"})
    fig.update_traces(line_color=PALETTE[3])
    st.plotly_chart(fig, use_container_width=True)
story_box("La dépense par étudiant en % du PIB/habitant a fortement décru depuis 1998, ce qui traduit une "
          "croissance des effectifs plus rapide que celle du financement par tête.", "info")

st.markdown("### 8.3 Chaîne Budget → Qualité de l'encadrement → Insertion / Chômage")
st.warning("⚠️ Les années disponibles pour le budget, l'encadrement et le chômage se recoupent sur très peu "
           "de points communs. Le graphique visualise la **chaîne conceptuelle** demandée ; la lecture doit "
           "rester qualitative, pas statistique.")
chain = national[["depense_annuelle_par_etudiant_fcfa", "ratio_etud_enseignant",
                   "taux_inscription_immediat_bac", "chomage_diplomes_pct"]].dropna(how="all")
fig = go.Figure()
for i, col in enumerate(chain.columns):
    s = chain[col].dropna()
    fig.add_trace(go.Scatter(x=s.index, y=(s - s.min()) / (s.max() - s.min()) * 100, mode="lines+markers",
                              name=col, line=dict(color=PALETTE[i % len(PALETTE)])))
fig.update_layout(title="⚠️ Chaîne Budget → Encadrement → Insertion → Chômage (indices normalisés 0-100)",
                   xaxis_title="Année", yaxis_title="Indice normalisé", height=460, margin=dict(t=60, b=10))
st.plotly_chart(fig, use_container_width=True)

render_footer()
