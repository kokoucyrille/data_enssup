"""
pages/4_Formations.py
======================
Reproduit les sections 3 (KPI), 9.2 (indice de saturation proxy), 15.1
(treemap) et 15.2 (sankey) du notebook — vue centrée sur l'offre de formation
technique.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import setup_page, story_box, download_buttons
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.metrics import kpi_row
from components.footer import render_footer
from config import REGION_COLORS
from utils.preprocessing import clean_etablissements
from utils.indicators import compute_kpi, compute_saturation_risk

setup_page("Formations", "🏫")
render_navbar("Formations techniques — Offre, catégories & saturation", "3, 9.2 & 15", "🏫")
df_filtered, filters = render_sidebar()

df_etab = clean_etablissements()
kpi = compute_kpi()

st.markdown("### Indicateurs clés de l'offre de formation technique")
kpi_row([
    ("Formations techniques", str(kpi["Nombre de formations techniques recensées"]), "🏫", "#1B6B45"),
    ("Régions couvertes", f"{kpi['Nombre de régions couvertes (formation technique)']}/5", "🗺️", "#2E5EAA"),
    ("Préfectures couvertes", str(kpi["Nombre de préfectures couvertes"]), "📍", "#F2C744"),
])

st.markdown("### Treemap — Togo → Région → Préfecture → Catégorie de formation")
tm = df_etab.dropna(subset=["etablissement_categorie"]).copy()
fig = px.treemap(tm, path=[px.Constant("Togo"), "region_nom_bdd", "prefecture_nom_bdd", "etablissement_categorie"],
                  color="region_nom_bdd", color_discrete_map={**REGION_COLORS, "(?)": "#ccc"},
                  title="Répartition hiérarchique de l'offre de formation technique")
fig.update_layout(height=560, margin=dict(t=60, b=10))
st.plotly_chart(fig, use_container_width=True)

st.markdown("### ⚠️ Sankey — Flux Région → Catégorie → Secteur estimé")
st.caption("⚠️ Le dernier niveau (secteur) est une estimation heuristique par mots-clés, cf. page Données §2.2.")
sk = df_etab.dropna(subset=["etablissement_categorie"]).copy()
regions_u = sorted(sk["region_nom_bdd"].unique())
cats_u = sorted(sk["etablissement_categorie"].unique())
sects_u = sorted(sk["secteur_estime"].unique())
labels = regions_u + cats_u + sects_u
idx = {lab: i for i, lab in enumerate(labels)}
node_colors = [REGION_COLORS[r] for r in regions_u] + ["#495057"] * len(cats_u) + ["#adb5bd"] * len(sects_u)
link_src, link_tgt, link_val = [], [], []
for (r, c), v in sk.groupby(["region_nom_bdd", "etablissement_categorie"]).size().items():
    link_src.append(idx[r]); link_tgt.append(idx[c]); link_val.append(int(v))
for (c, s), v in sk.groupby(["etablissement_categorie", "secteur_estime"]).size().items():
    link_src.append(idx[c]); link_tgt.append(idx[s]); link_val.append(int(v))
fig = go.Figure(go.Sankey(node=dict(label=labels, color=node_colors, pad=14, thickness=16),
                           link=dict(source=link_src, target=link_tgt, value=link_val, color="rgba(150,150,150,0.35)")))
fig.update_layout(title="⚠️ Flux Région → Catégorie de formation → Secteur estimé", height=560, margin=dict(t=60, b=10))
st.plotly_chart(fig, use_container_width=True)

st.markdown("### 9.2 Formations « saturées » vs « porteuses » ⚠️ (indice de risque proxy)")
st.warning(
    "⚠️ **Limite majeure documentée en page Données** : aucune donnée ne relie le chômage à une filière, un "
    "diplôme ou une région précise. L'indice ci-dessous est un **proxy structurel** : "
    "`indice_saturation = (poids relatif de la catégorie dans l'offre) × (part des créations récentes depuis 2010)`. "
    "Une catégorie qui pèse déjà lourd **et** continue de s'étendre rapidement est jugée à risque de saturation."
)
risk = compute_saturation_risk()
fig = px.bar(risk.reset_index(), x="etablissement_categorie", y="indice_saturation_proxy",
             color="indice_saturation_proxy", color_continuous_scale="RdYlGn_r",
             title="⚠️ Indice de saturation proxy par catégorie de formation",
             labels={"etablissement_categorie": "Catégorie", "indice_saturation_proxy": "Indice (0-100)"})
fig.update_layout(height=430, margin=dict(t=60, b=10), coloraxis_showscale=False)
st.plotly_chart(fig, use_container_width=True)
st.dataframe(risk, use_container_width=True)
download_buttons(risk, "indice_saturation_formations", "risk")

story_box(
    f"Catégorie la plus exposée au risque de saturation (proxy) : <b>{risk.index[0]}</b>. Catégorie jugée la "
    f"plus porteuse (proxy) : <b>{risk.index[-1]}</b>. À confronter impérativement à une véritable enquête "
    "d'insertion professionnelle avant toute décision d'ouverture ou de fermeture de filière.", "warning"
)

render_footer()
