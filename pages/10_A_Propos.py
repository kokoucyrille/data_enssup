"""
pages/10_A_Propos.py
======================
Reproduit la section 24 du notebook (conclusion et pistes d'amélioration) et
récapitule les sources de données et l'équipe du projet.
"""
import streamlit as st

from utils.helpers import setup_page
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.footer import render_footer
from config import AUTHOR, INSTITUTION, MINISTERE

setup_page("À Propos", "ℹ️")
render_navbar("À Propos — Sources, méthodologie & conclusion", "24", "ℹ️")
_, filters = render_sidebar()

st.markdown("### Ce que cette analyse a établi (sur données réelles)")
st.markdown(
    """
- Une **cartographie fine et géolocalisée** de 256 établissements de formation technique, avec une forte
  concentration régionale et des disparités marquées de couverture par habitant.
- Une **lecture structurelle par la théorie des graphes** (centralités, PageRank, communautés de Louvain) qui
  va au-delà du simple décompte et révèle les régions et catégories réellement pivots du système.
- Un **suivi complet des indicateurs nationaux** (effectifs, féminisation, encadrement, budgets, chômage) sur
  la période disponible, avec une chaîne Budget → Encadrement → Insertion documentée.
- Une **démarche Machine Learning et clustering reproductible**, honnêtement bornée par la taille des
  échantillons disponibles.
- Des **scores composites originaux** (FEAS, Opportunity Index, Territorial Equity Score, Employment Potential
  Score) combinant systématiquement le réel et l'estimé, chaque composante étant traçable à sa source.
"""
)

st.markdown("### Ce que la synthèse décisionnelle ajoute")
st.markdown(
    """
- Un **indice unique d'adéquation Formation-Emploi (IAFE)**, qui remplace le FEAS comme indice de référence,
  avec des poids **statistiquement discutés** (méthode CRITIC) et un **test de robustesse explicite**.
- Un **classement national complet** (régions et établissements) et une **matrice de priorisation Impact ×
  Urgence** qui traduit le diagnostic en priorités d'investissement chiffrées et justifiées région par région.
- Une **carte des priorités**, des **scénarios prospectifs transparents** et un **Policy Dashboard** rassemblant
  des décisions calculées automatiquement à partir des données — sans aucun texte générique.
- Une découverte transversale : le Togo semble moins souffrir d'un déficit de **volume** de formation que d'un
  déséquilibre de **composition** de son offre (la Maritime, mieux dotée que quiconque en établissements,
  affiche pourtant le score d'insertion proxy le plus faible du pays).
"""
)

st.markdown("### Ce qu'il manque pour aller plus loin (priorités de collecte pour le Ministère)")
st.markdown(
    """
1. **Une nomenclature de filières/spécialités** systématiquement renseignée dans le recensement des
   établissements techniques.
2. **Une exécution budgétaire régionalisée**, pour vérifier si les régions les moins couvertes reçoivent un
   effort d'investissement compensatoire, et remplacer une composante nationale uniforme de l'IAFE par une
   vraie composante régionale.
3. **Une enquête de traçabilité des diplômés (tracer study)** par filière, diplôme et région — condition
   *sine qua non* d'un véritable indicateur d'insertion.
4. **Une mise à jour régulière** des séries nationales (plusieurs indicateurs s'arrêtent en 2018-2019), pour
   que le pilotage stratégique du Ministère s'appuie sur une photographie récente.
"""
)

st.divider()
st.markdown("### Sources de données")
st.markdown(
    """
- Fichiers du Data Challenge Éducation (Défi 2, 2026) : établissements de formation technique géolocalisés,
  répartition des établissements d'enseignement supérieur (2018), indicateurs socio-éducatifs nationaux,
  budgets, indicateurs Banque mondiale (chômage des diplômés, dépense/étudiant, taux d'inscription tertiaire).
- Population régionale : **RGPH-5** (INSEED Togo, résultats définitifs, novembre 2022), reprise par l'Agence
  Togolaise de Presse (ATOP), avril 2023 — seule donnée externe injectée dans ce projet.
"""
)

st.markdown("### Équipe & contexte")
c1, c2, c3 = st.columns(3)
c1.metric("Auteur", AUTHOR)
c2.metric("Institution", INSTITUTION)
c3.metric("Concours", "Data Challenge Éducation — Défi 2 — 2026")
st.caption(f"Tableau de bord produit à destination du {MINISTERE}.")

st.info(
    "🧭 Toutes les sources de données et hypothèses méthodologiques sont documentées dans la page **Données**, "
    "et rappelées par le symbole ⚠️ à chaque usage d'une estimation ou d'un proxy."
)

render_footer()
