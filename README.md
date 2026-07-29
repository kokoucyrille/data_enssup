# 🎓 🇹🇬 Adéquation Formation-Emploi au Togo

Tableau de bord Streamlit — Data Challenge Éducation, Défi 2 (2026).
Analyse des formations techniques, de l'enseignement supérieur, des budgets et
du chômage des diplômés au Togo, à destination du Ministère de l'Éducation
Nationale et du Ministère de l'Enseignement Supérieur.

Application entièrement dérivée du notebook `notebooks/Analyse_Adequation_Formation_Emploi_Togo_presentation_v2.ipynb`
(24 sections), restructurée en application professionnelle modulaire.

## Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Architecture

```
Formation_Emploi_Togo/
├── app.py                     # Point d'entrée (redirige vers Accueil)
├── config.py                  # Constantes centrales (chemins, palette, poids)
├── requirements.txt
├── .streamlit/config.toml     # Thème Streamlit
├── assets/style.css           # CSS personnalisé
│   ├── ministere_education_nationale.jpg        # République / MEN
│   ├── ministere_enseignement_superieur.jpg     # République / MESR
│   └── togo_ai_lab.jpg                          # Partenaire Togo AI Lab
├── data/                      # 8 CSV du Data Challenge
├── utils/
│   ├── loader.py              # Chargement brut (cache)
│   ├── preprocessing.py       # Nettoyage, structuration, jointures
│   ├── indicators.py          # KPI, FEAS, IAFE, CRITIC, ML, clustering, scénarios
│   ├── graph_utils.py         # Théorie des graphes (NetworkX + pyvis)
│   ├── map_utils.py           # Cartes Folium
│   ├── charts.py              # Constructeurs de graphiques Plotly génériques
│   └── helpers.py             # Storytelling, exports, setup de page
├── components/
│   ├── sidebar.py, navbar.py, metrics.py, filters.py, cards.py, footer.py
├── pages/
│   ├── 1_Accueil.py
│   ├── 2_Données.py                     # §1-2 : chargement, audit, méthodologie
│   ├── 3_Analyse_Territoriale.py        # §4, 10, 21 : cartes, graphes
│   ├── 4_Formations.py                  # §3, 9.2, 15 : offre, saturation
│   ├── 5_Enseignement_Supérieur.py      # §5, 6, 11, 12 : effectifs, ML, clustering
│   ├── 6_Budgets.py                     # §8
│   ├── 7_Chômage.py                     # §9, 16, 17
│   ├── 8_Indice_Formation_Emploi.py     # §13, 18-22 : FEAS, IAFE, priorisation
│   ├── 9_Recommandations.py             # §14, 23 : recommandations, Policy Dashboard
│   ├── 10_A_Propos.py                   # §24 : conclusion, sources
│   └── 11_Actions_prioritaires.py        # Portefeuille d'actions ministérielles
└── notebooks/                 # Notebook source (traçabilité)
```

## Note méthodologique

Chaque estimation, proxy ou valeur nationale appliquée uniformément aux régions
est signalée par le symbole **⚠️** dans l'application — cf. la page **Données**
pour le détail complet des limites de chaque source.

## Nouveautés décisionnelles

- Charte graphique institutionnelle bleue, responsive et cartes KPI modernisées.
- Filtres territoriaux et de l'offre placés en haut de chaque page ; les analyses
  fondées sur les établissements sont recalculées sur le périmètre sélectionné.
- Pages **Chômage** et **Indice Formation-Emploi** sécurisées face aux séries
  incomplètes et aux corrélations non interprétables.
- Exports CSV et Excel pour les tableaux, export PNG/PDF pour les graphiques
  enrichis, lorsque Kaleido est disponible.
- Page **Actions prioritaires** : régions, formations, secteurs, populations
  vulnérables, recommandations et impact attendu.

### Logos institutionnels

Les logos institutionnels fournis sont déjà intégrés à `assets/`. Ils sont
affichés automatiquement dans la barre latérale et le pied de page.
