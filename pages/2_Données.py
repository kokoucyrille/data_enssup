"""
pages/2_Données.py
===================
Reproduit les sections 1 et 2 du notebook : chargement des données, nettoyage,
audit quantitatif des valeurs manquantes, et note méthodologique (portée et
limites des données).
"""
import streamlit as st
import plotly.express as px

from utils.helpers import setup_page, story_box, download_buttons
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.footer import render_footer
from utils.preprocessing import (
    clean_etablissements, clean_repartition_sup, build_indicateurs_sup, build_budget_wide,
    build_wb_indicators, audit_missing_values, completeness_table, get_population_df,
)

setup_page("Données", "📊")
render_navbar("Données — Chargement, nettoyage et note méthodologique", "1 & 2", "📊")
_, filters = render_sidebar()

df_etab = clean_etablissements()
df_repart = clean_repartition_sup()
ind_wide = build_indicateurs_sup()
budget_wide = build_budget_wide()
wb = build_wb_indicators()

tab1, tab2, tab3, tab4 = st.tabs(["1.2 Jeux de données", "1.4 Audit des manquants",
                                   "1.5 Règles de traitement", "2. Note méthodologique"])

with tab1:
    st.markdown("### Huit fichiers CSV, trois familles de granularité")
    st.markdown(
        """
| Famille | Granularité |
|---|---|
| 🏫 Établissements de formation technique (géolocalisés) | Établissement individuel, région/préfecture/commune, coordonnées GPS |
| 🏛️ Établissements d'enseignement supérieur | Ville, type (Université/Établissement), statut (Public/Privé), année 2018 |
| 📈 Indicateurs socio-éducatifs nationaux | Nationale, séries temporelles annuelles |
"""
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Établissements formation technique", df_etab.shape[0], help=f"{df_etab.shape[1]} colonnes")
    c2.metric("Répartition établ. sup. 2018", df_repart.shape[0], help=f"{df_repart.shape[1]} colonnes")
    c3.metric("Années d'indicateurs nationaux", ind_wide.shape[0])

    st.markdown("#### Aperçu — Établissements de formation technique")
    st.dataframe(df_etab.head(20), use_container_width=True)
    download_buttons(df_etab, "etablissements_formation_technique", "etab")

    st.markdown("#### Aperçu — Répartition établissements sup. 2018 (Région → Ville → Type → Statut)")
    st.dataframe(df_repart.groupby(["villes", "type", "statut"])["Value"].sum().unstack(fill_value=0), use_container_width=True)

    st.markdown("#### Population régionale (RGPH-5, INSEED Togo, novembre 2022)")
    pop_df = get_population_df()
    st.dataframe(pop_df, use_container_width=True, hide_index=True)
    st.caption(f"Population totale du Togo (RGPH-5, 2022) : {int(pop_df['population_2022'].sum()):,} habitants".replace(",", " "))

with tab2:
    st.markdown("### Audit quantitatif des valeurs manquantes")
    st.caption("Deux natures de manquant : la non-réponse d'enquête (codes 'Nsp'/'N/a' convertis en NaN) et "
               "l'absence structurelle dans une série nationale (indicateur non mesuré certaines années).")
    audit_df = audit_missing_values()
    fig = px.bar(audit_df, x="% manquant", y="colonne", color="jeu_de_données", orientation="h",
                 title="Audit des valeurs manquantes par colonne")
    fig.update_layout(height=max(400, 28 * len(audit_df)), margin=dict(t=60, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(audit_df, use_container_width=True, hide_index=True)
    story_box(
        f"{len(audit_df)} colonnes sont concernées par de la donnée manquante. Les champs géographiques "
        "(région, préfecture, commune, coordonnées GPS) sont intégralement renseignés (0% manquant), ce qui "
        "conditionne la fiabilité de toute la cartographie du tableau de bord.", "info"
    )

    st.markdown("### Complétude des séries temporelles nationales")
    comp_df = completeness_table()
    st.dataframe(comp_df, use_container_width=True, hide_index=True)
    story_box(
        "Le chômage des diplômés est, de loin, l'indicateur le plus lacunaire — c'est précisément la raison "
        "pour laquelle la page Machine Learning traite ce point comme une limite structurelle et non comme un "
        "simple 'trou à combler'.", "warning"
    )

with tab3:
    st.markdown("### Règles de traitement retenues")
    st.markdown(
        """
- **Champs géographiques** (région, GPS) : 0% manquant → aucun traitement.
- **Champs qualitatifs déclaratifs** (toilettes, terrain, catégorie...) : **jamais imputés** — exclus au cas
  par cas via `dropna`, uniquement dans les analyses qui utilisent le champ concerné.
- **Filière/spécialité absente** : remplacée par une estimation par mots-clés (`secteur_estime`), toujours
  signalée ⚠️.
- **Séries nationales annuelles** : jamais imputées dans les analyses descriptives — seules les années
  réellement observées sont tracées.
- **Prédicteurs du modèle ML uniquement** : interpolation linéaire entre années observées, avec un marqueur
  `__observe` explicite ; la cible (chômage) n'est **jamais** interpolée.
- **Budget régionalisé absent** : aucune ventilation fabriquée — valeur nationale appliquée uniformément aux
  régions, signalée ⚠️.
"""
    )
    st.info("🧭 Une valeur manquante est donc **exclue avec traçabilité**, **interpolée avec marqueur**, ou "
            "**remplacée par une estimation signalée** — jamais comblée silencieusement.")

with tab4:
    st.markdown("### 2.1 Ce que les données permettent de faire directement")
    st.markdown(
        """
| Analyse | Granularité réelle |
|---|---|
| Cartographie des formations techniques | Établissement géolocalisé, 256 structures, 5 régions |
| Public/privé, université/établissement | Ville, année 2018 |
| Effectifs, féminisation, ratio étudiant/enseignant | National, annuel, 2014-2019 |
| Budgets (voté/exécuté), PIB | National, annuel, 2013-2018 |
| Chômage des diplômés, dépense/étudiant, inscription | Banque mondiale, national, très lacunaire |
"""
    )
    st.markdown("### 2.2 Ce que les données ne permettent pas — et comment ce tableau de bord compense")
    st.markdown(
        """
- ❌ **Pas de filière détaillée** → estimée par mots-clés (`secteur_estime` ⚠️).
- ❌ **Pas de budget régionalisé** → valeur nationale appliquée uniformément aux régions (⚠️, page Indice IAFE).
- ❌ **Pas de chômage par filière/région** → modèle ML (page Enseignement Supérieur) traité comme exploratoire.
- ❌ **Pas de table formation ↔ emploi** → graphe construit sur Formation/Catégorie ↔ Secteur estimé ↔ Région.
- ⚠️ **Chevauchement temporel limité** entre budgets, indicateurs et chômage → corrélations indicatives, non causales.
"""
    )
    st.markdown("### 2.3 Enrichissement externe")
    st.write("Populations régionales du **RGPH-5 (INSEED, novembre 2022)** — seule donnée externe injectée, "
             "pour normaliser la couverture territoriale.")
    st.success("🧭 **Principe directeur** : tout graphique ou score construit à partir d'une estimation, d'une "
               "valeur nationale appliquée uniformément, ou d'une heuristique porte le symbole **⚠️**. Son "
               "absence signifie une donnée directement observée.")

render_footer()
