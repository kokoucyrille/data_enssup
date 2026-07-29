"""
pages/8_Indice_Formation_Emploi.py
===================================
Cœur analytique du tableau de bord : FEAS (§13), Indice d'Adéquation
Formation-Emploi IAFE (§18), méthode CRITIC et test de robustesse (§18.2),
classement national (§19), matrice de priorisation Impact × Urgence (§20) et
scénarios prospectifs (§22).
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.helpers import (
    chart_insights,
    download_buttons,
    png_download_button,
    setup_page,
    story_box,
)
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.footer import render_footer
from config import REGIONS, REGION_COLORS, PALETTE
from utils.indicators import (
    compute_feas, compute_complementary_scores, compute_iafe, compute_iafe_etablissement,
    critic_weights, compute_impact_urgence, compute_scenarios, compute_region_features, fmt_fr,
)
from config import IAFE_WEIGHTS
from utils.charts import radar_chart, gauge_chart

setup_page("Indice Formation-Emploi", "🧮")
render_navbar("Indice d'Adéquation Formation-Emploi (IAFE)", "13 & 18-22", "🧮")
df_filtered, filters = render_sidebar()

if df_filtered.empty:
    st.warning(
        "Aucun établissement ne correspond aux filtres sélectionnés. "
        "Élargissez le périmètre pour calculer l'indice Formation-Emploi."
    )
    render_footer()
    st.stop()

tabs = st.tabs(["13. FEAS", "18. Formule IAFE", "18.2 CRITIC & robustesse", "19. Classement",
                "20-21. Priorisation", "22. Scénarios"])

# ------------------------------------------------------------------
# 13. FEAS
# ------------------------------------------------------------------
with tabs[0]:
    feas = compute_feas(df_filtered)
    feas_sorted = feas.sort_values("FEAS", ascending=False)
    st.markdown("### 13.1 Formation-Employment Alignment Score (FEAS) — 0 à 100")
    st.caption("Combine variables régionales réelles (couverture, diversité, dynamisme, volume sup.) et "
               "indicateurs nationaux appliqués uniformément ⚠️ (encadrement, orientation scientifique, exécution budgétaire).")
    fig = px.bar(feas_sorted.reset_index(), x="region", y="FEAS", color="FEAS", color_continuous_scale="RdYlGn",
                 range_color=[0, 100], text=feas_sorted["FEAS"].round(1), title="FEAS par région — 0 à 100")
    fig.update_traces(textposition="outside")
    fig.update_layout(height=430, margin=dict(t=60, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    png_download_button(fig, "feas_regions", "feas_regions")
    chart_insights(
        "Le FEAS compare la couverture, la diversité et le dynamisme de l'offre entre régions.",
        "Les composantes nationales sont constantes ; les écarts proviennent principalement de l'offre locale.",
        "Le score ne mesure pas la qualité pédagogique ni l'insertion réellement observée.",
        "Affecter les investissements en combinant ce score avec la matrice Impact × Urgence.",
        "Vérifier les résultats après chaque changement de périmètre de filtre.",
    )
    st.dataframe(feas_sorted.round(1), use_container_width=True)

    st.markdown("### 13.2 Trois scores complémentaires")
    st.markdown(
        "- **Opportunity Index** : régions à forte population mais faible couverture actuelle → potentiel "
        "d'investissement prioritaire (100% régional, réel).\n"
        "- **Territorial Equity Score** : équité de répartition de l'offre rapportée à la population (100% régional, réel).\n"
        "- **Employment Potential Score ⚠️** : potentiel théorique d'absorption en emploi (proxy)."
    )
    scores_df, equity = compute_complementary_scores(df_filtered)
    st.dataframe(scores_df.round(1), use_container_width=True)
    story_box(f"Score d'équité territoriale du système : <b>{equity}/100</b>. Région avec le plus fort potentiel "
              f"d'opportunité : <b>{scores_df['Opportunity Index'].idxmax()}</b>.", "info")

    st.plotly_chart(radar_chart(scores_df, ["FEAS", "Opportunity Index", "Employment Potential Score ⚠️"],
                     REGION_COLORS, "Comparatif régional — scores composites"), use_container_width=True)

    st.markdown("### Profils régionaux — vue multidimensionnelle")
    rf = compute_region_features(df_filtered)
    c1, c2 = st.columns(2)
    with c1:
        bubble = rf.copy()
        bubble["FEAS"] = feas["FEAS"]
        fig = px.scatter(bubble.reset_index(), x="population_2022", y="nb_etablissements", size="FEAS", color="region",
                          color_discrete_map=REGION_COLORS, size_max=55, text=bubble.index,
                          title="Population régionale vs offre (taille = FEAS)",
                          labels={"population_2022": "Population 2022", "nb_etablissements": "Nb établissements"})
        fig.update_traces(textposition="top center")
        fig.update_layout(height=460, margin=dict(t=60, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        pc = rf.copy()
        pc["FEAS"] = feas["FEAS"]
        fig = px.parallel_coordinates(
            pc.reset_index(), color="FEAS", color_continuous_scale="RdYlGn",
            dimensions=["nb_etablissements", "etab_pour_100k_hab", "diversite_categories",
                        "part_creations_recentes_pct", "nb_etab_sup_2018", "FEAS"],
            title="Profils régionaux multidimensionnels")
        fig.update_layout(height=460, margin=dict(t=60, b=10))
        st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------
# 18.1 Formule IAFE
# ------------------------------------------------------------------
with tabs[1]:
    st.markdown("### 18.1 Formule")
    st.latex(r"""\text{IAFE} = 40\%\times\text{Offre} + 25\%\times\text{Budget/étudiant} + 20\%\times\text{Insertion} + 15\%\times\text{Chômage (inversé)}""")
    st.markdown(
        """
| Pilier | Poids | Granularité | Construction |
|---|---|---|---|
| **Offre de formation** | 40% | Régionale, réelle | Couverture + diversité + dynamisme + volume sup. |
| **Budget par étudiant** | 25% | Nationale ⚠️ | Positionné dans sa propre plage historique observée |
| **Insertion professionnelle** | 20% | Régionale, proxy | Employabilité moyenne des catégories offertes par région |
| **Chômage des diplômés** | 15% | Nationale ⚠️ | Positionné (inversé) dans sa propre plage historique |
"""
    )
    st.info("⚠️ Aucune donnée réelle de budget, chômage ou insertion n'existe à l'échelle régionale au Togo — "
            "c'est une limite documentée, pas un choix arbitraire.")

    iafe_data = compute_iafe(df_filtered)
    iafe = iafe_data["iafe"]
    iafe_sorted = iafe.sort_values("IAFE", ascending=False)
    st.dataframe(iafe_sorted.style.background_gradient(subset=["IAFE"], cmap="RdYlGn").format(precision=1), use_container_width=True)
    st.caption(f"Budget/étudiant {iafe_data['budget_year']} = {fmt_fr(iafe_data['budget_val'])} FCFA → score {iafe_data['budget_score']:.1f}/100. "
               f"Chômage {iafe_data['chomage_year']} = {iafe_data['chomage_val']:.1f}% → score {iafe_data['chomage_score']:.1f}/100.")

    fig = go.Figure()
    for col in IAFE_WEIGHTS:
        fig.add_trace(go.Bar(x=iafe_sorted.index, y=iafe_sorted[col] * IAFE_WEIGHTS[col], name=col))
    fig.add_trace(go.Scatter(x=iafe_sorted.index, y=iafe_sorted["IAFE"], mode="text",
                              text=iafe_sorted["IAFE"].round(1), textposition="top center", showlegend=False))
    fig.update_layout(barmode="stack", title="IAFE par région — décomposition par pilier", yaxis_title="Score IAFE (0-100)",
                       height=480, margin=dict(t=60, b=10), legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig, use_container_width=True)
    png_download_button(fig, "iafe_piliers", "iafe_piliers")
    chart_insights(
        "Les régions sont comparées sur les quatre piliers explicites de l'IAFE.",
        "Budget et chômage sont des références nationales et ne créent donc pas d'écart régional.",
        "Les différences observées proviennent de l'offre et du proxy d'insertion.",
        "Compléter l'IAFE par des données régionales d'emploi et de dépenses.",
        "Suivre en priorité les régions à faible score et à forte urgence.",
    )
    story_box("La Maritime concentre l'essentiel de l'offre nationale de formation technique et obtient le "
              "meilleur score d'Offre — mais affiche le score d'Insertion (proxy) le plus faible du pays. Le "
              "Togo n'a donc pas seulement un problème de <b>volume</b> d'offre, mais aussi de "
              "<b>composition</b> de cette offre.", "warning")

    st.markdown("### 18.3 Score par établissement")
    etab_iafe = compute_iafe_etablissement(df_filtered)
    moyenne_nat = etab_iafe["IAFE_etablissement"].mean()
    fig = px.histogram(etab_iafe.dropna(subset=["IAFE_etablissement"]), x="IAFE_etablissement", color="region_nom_bdd",
                        color_discrete_map=REGION_COLORS, nbins=25,
                        title="Distribution de l'IAFE au niveau établissement (256 établissements)")
    fig.add_vline(x=moyenne_nat, line_dash="dash", line_color="black", annotation_text=f"Moyenne ({moyenne_nat:.1f})")
    fig.update_layout(height=430, margin=dict(t=60, b=10), bargap=0.05)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Deux établissements de même région et même catégorie obtiennent un score identique : limite "
               "honnête des données disponibles (aucune performance individuelle par établissement), pas un artefact de calcul.")

    st.markdown("### 18.4 Score national")
    st.plotly_chart(gauge_chart(iafe_data["iafe_national"], "IAFE national (pondéré par la population régionale)"), use_container_width=True)
    st.caption(f"IAFE national pondéré : {iafe_data['iafe_national']:.1f}/100 · moyenne simple des 5 régions : {iafe_data['iafe_national_simple']:.1f}/100")

# ------------------------------------------------------------------
# 18.2 CRITIC & robustesse
# ------------------------------------------------------------------
with tabs[2]:
    st.markdown("### 18.2 Pondération : justification statistique (méthode CRITIC)")
    st.caption("CRITIC (Diakoulaki, Mavrotas & Papayannakis, 1995) pondère chaque critère selon sa variabilité "
               "et son originalité par rapport aux autres critères.")
    iafe = compute_iafe(df_filtered)["iafe"]
    w_critic = critic_weights(iafe[list(IAFE_WEIGHTS)])
    w_expert = pd.Series(IAFE_WEIGHTS)
    w_equal = pd.Series(0.25, index=list(IAFE_WEIGHTS))
    comparaison_poids = pd.DataFrame({"Experts (cahier des charges)": w_expert, "CRITIC (statistique)": w_critic, "Égalitaire (référence)": w_equal})
    st.dataframe(comparaison_poids.style.format("{:.1%}").background_gradient(cmap="Blues", axis=1), use_container_width=True)

    fig = go.Figure()
    for scheme in comparaison_poids.columns:
        fig.add_trace(go.Bar(x=comparaison_poids.index, y=comparaison_poids[scheme], name=scheme))
    fig.update_layout(barmode="group", title="Comparaison des schémas de pondération de l'IAFE", yaxis_tickformat=".0%",
                       height=420, margin=dict(t=60, b=10), legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)
    story_box("CRITIC attribue un poids quasi-nul à Budget et Chômage : non pas parce qu'ils seraient sans "
              "importance, mais parce que ce sont des valeurs NATIONALES appliquées uniformément aux 5 régions "
              "et ne contiennent, par construction, aucune information discriminante à l'échelle régionale. "
              "C'est une limite des données, pas une faiblesse de la méthode.", "warning")

    from scipy.stats import spearmanr
    iafe_critic = (iafe[list(IAFE_WEIGHTS)] * w_critic).sum(axis=1).round(1)
    rang_expert = iafe["IAFE"].rank(ascending=False).astype(int)
    rang_critic = iafe_critic.rank(ascending=False).astype(int)
    rho, _ = spearmanr(rang_expert, rang_critic)
    robustesse = pd.DataFrame({"Rang (poids experts)": rang_expert, "Rang (poids CRITIC)": rang_critic})
    st.dataframe(robustesse.sort_values("Rang (poids experts)"), use_container_width=True)
    st.caption(f"Corrélation de rang (Spearman) experts vs CRITIC : {rho:.2f} — accord {'fort' if rho > 0.7 else 'faible à modéré'}.")
    st.info(">>> Décision retenue : les poids du cahier des charges (40/25/20/15) sont conservés comme IAFE "
            "officiel — ils reflètent une hiérarchie politique assumée. La tension avec CRITIC est un résultat "
            "à porter à la connaissance des décideurs, pas un bug.")

# ------------------------------------------------------------------
# 19. Classement
# ------------------------------------------------------------------
with tabs[3]:
    iafe_data = compute_iafe(df_filtered)
    iafe = iafe_data["iafe"]
    feas = compute_feas(df_filtered)
    classement_regions = iafe[["IAFE"]].copy()
    classement_regions["Rang IAFE"] = classement_regions["IAFE"].rank(ascending=False).astype(int)
    classement_regions["FEAS (§13.1)"] = feas["FEAS"]
    classement_regions["Rang FEAS"] = feas["FEAS"].rank(ascending=False).astype(int)
    classement_regions["Δ rang (FEAS→IAFE)"] = classement_regions["Rang FEAS"] - classement_regions["Rang IAFE"]
    classement_regions["Δ score (IAFE-FEAS)"] = (classement_regions["IAFE"] - feas["FEAS"]).round(1)
    classement_regions = classement_regions.sort_values("IAFE", ascending=False)

    def arrow(x):
        return "▲" if x > 0 else ("▼" if x < 0 else "▬")
    classement_regions["Évolution"] = classement_regions["Δ rang (FEAS→IAFE)"].apply(arrow)
    st.markdown("### 19.1 Régions — classement complet")
    st.dataframe(
        classement_regions.style.background_gradient(subset=["IAFE"], cmap="RdYlGn")
        .background_gradient(subset=["Δ rang (FEAS→IAFE)"], cmap="RdYlGn", vmin=-2, vmax=2)
        .format({"IAFE": "{:.1f}", "FEAS (§13.1)": "{:.1f}", "Δ score (IAFE-FEAS)": "{:+.1f}"}),
        use_container_width=True,
    )
    fig = go.Figure(go.Bar(y=classement_regions.index, x=classement_regions["IAFE"], orientation="h",
                            marker=dict(color=classement_regions["IAFE"], colorscale="RdYlGn", cmin=0, cmax=100),
                            text=[f"#{r}  {v:.1f}" for r, v in zip(classement_regions["Rang IAFE"], classement_regions["IAFE"])],
                            textposition="outside"))
    fig.update_layout(title="Classement national des régions — IAFE", xaxis_title="Score IAFE (0-100)",
                       xaxis_range=[0, 115], height=420, margin=dict(t=60, b=10), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 19.2 Établissements — Top 10 et Bottom 10")
    etab_iafe = compute_iafe_etablissement(df_filtered)
    cols_show = ["etab_nom", "region_nom_bdd", "etablissement_categorie", "IAFE_etablissement", "ecart_moyenne_nationale"]
    rename_show = {"etab_nom": "Établissement", "region_nom_bdd": "Région", "etablissement_categorie": "Catégorie",
                   "IAFE_etablissement": "IAFE", "ecart_moyenne_nationale": "Écart / moyenne nat."}
    top10 = etab_iafe.dropna(subset=["IAFE_etablissement"]).sort_values(["IAFE_etablissement", "annee_creation"], ascending=[False, False]).head(10)[cols_show].rename(columns=rename_show)
    bottom10 = etab_iafe.dropna(subset=["IAFE_etablissement"]).sort_values(["IAFE_etablissement", "annee_creation"], ascending=[True, False]).head(10)[cols_show].rename(columns=rename_show)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**TOP 10**")
        st.dataframe(top10.style.background_gradient(subset=["IAFE"], cmap="RdYlGn"), use_container_width=True, hide_index=True)
    with c2:
        st.markdown("**BOTTOM 10**")
        st.dataframe(bottom10.style.background_gradient(subset=["IAFE"], cmap="RdYlGn"), use_container_width=True, hide_index=True)

    combo = pd.concat([top10.assign(Groupe="Top 10"), bottom10.assign(Groupe="Bottom 10")])
    fig = px.bar(combo, x="IAFE", y="Établissement", color="Groupe", orientation="h",
                 color_discrete_map={"Top 10": PALETTE[0], "Bottom 10": PALETTE[2]}, hover_data=["Région", "Catégorie"],
                 title="Top 10 et Bottom 10 établissements — IAFE")
    fig.update_layout(height=620, margin=dict(t=60, b=10), yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------
# 20-21. Priorisation
# ------------------------------------------------------------------
with tabs[4]:
    st.markdown("### 20. Matrice de priorisation Impact × Urgence")
    st.caption("Impact : déficit d'offre (45%) + déficit d'insertion (30%) + déficit d'infrastructures sup. "
               "(25%). Urgence : pression démographique (65%) + stagnation de l'offre (35%).")
    impact_urgence = compute_impact_urgence(df_filtered)
    med_impact, med_urgence = impact_urgence.attrs["med_impact"], impact_urgence.attrs["med_urgence"]
    st.dataframe(
        impact_urgence.drop(columns="Couleur")[["Impact", "Urgence", "Population_2022", "Priorité"]].sort_values("Impact", ascending=False)
        .style.background_gradient(subset=["Impact", "Urgence"], cmap="RdYlGn_r").format({"Impact": "{:.1f}", "Urgence": "{:.1f}", "Population_2022": "{:,.0f}"}),
        use_container_width=True,
    )
    st.caption(f"Répartition : {impact_urgence['Priorité'].value_counts().to_dict()}")

    fig = go.Figure()
    fig.add_shape(type="rect", x0=med_impact, x1=105, y0=med_urgence, y1=105, fillcolor="#D62839", opacity=0.07, line_width=0)
    fig.add_shape(type="rect", x0=-5, x1=med_impact, y0=-5, y1=med_urgence, fillcolor="#1B6B45", opacity=0.07, line_width=0)
    fig.add_vline(x=med_impact, line_dash="dot", line_color="gray")
    fig.add_hline(y=med_urgence, line_dash="dot", line_color="gray")
    fig.add_trace(go.Scatter(x=impact_urgence["Impact"], y=impact_urgence["Urgence"], mode="markers+text",
                              text=impact_urgence.index, textposition="top center",
                              marker=dict(size=impact_urgence["Population_2022"] / 25000, color=impact_urgence["Couleur"],
                                          line=dict(width=1.5, color="white"), sizemin=18)))
    fig.update_layout(title="Matrice de priorisation Impact × Urgence (taille = population 2022)",
                       xaxis_title="Impact (déficit structurel)", yaxis_title="Urgence (pression démographique + stagnation)",
                       xaxis_range=[-5, 105], yaxis_range=[-5, 105], height=560, margin=dict(t=60, b=10))
    st.plotly_chart(fig, use_container_width=True)
    png_download_button(fig, "priorisation_impact_urgence", "impact_urgence")
    chart_insights(
        "Les régions du quadrant haut-droite cumulent déficit structurel et urgence démographique.",
        "Les seuils sont des médianes du périmètre filtré, pas des normes absolues.",
        "La priorisation est un outil transparent d'arbitrage, à compléter par une instruction de terrain.",
        "Programmer les investissements par niveau de priorité et suivre les indicateurs associés.",
        "Lancer un plan d'action régional pour les priorités 1.",
    )

    st.markdown("#### Justification automatique, région par région")
    for r in impact_urgence.sort_values("Impact", ascending=False).index:
        row = impact_urgence.loc[r]
        st.markdown(
            f"**{r}** — Impact {row['Impact']:.0f}/100 (déficit offre {row['deficit_offre']:.0f}, déficit "
            f"insertion {row['deficit_insertion']:.0f}, déficit infra sup. {row['deficit_infra_sup']:.0f}) × "
            f"Urgence {row['Urgence']:.0f}/100 (poids démographique, stagnation {row['dynamisme_inv']:.0f}) "
            f"→ **{row['Priorité']}**"
        )
    download_buttons(impact_urgence.drop(columns="Couleur"), "matrice_impact_urgence", "iu")

# ------------------------------------------------------------------
# 22. Scénarios
# ------------------------------------------------------------------
with tabs[5]:
    st.info("Aucun modèle causal n'est disponible : les effets ci-dessous sont des **simulations mécaniques "
            "et transparentes** de la formule de l'IAFE, pas des prédictions économétriques.")
    sc = compute_scenarios()
    st.dataframe(
        sc["scenarios_df"].style.background_gradient(subset=["Δ IAFE national"], cmap="RdYlGn", vmin=-10, vmax=10)
        .format({"IAFE national": "{:.1f}", "Δ IAFE national": "{:+.1f}"}, na_rep="n/a"),
        use_container_width=True, hide_index=True,
    )
    st.caption(f"Référence : IAFE national de base = {sc['iafe_base_nat']:.1f}/100. Seuil de rattrapage : "
               f"il faudrait +{sc['nb_centres_necessaires']} centres pour que {sc['region_cible']} quitte la "
               "dernière place en couverture/habitant.")

    regions_qui_bougent = list(sc["changed_expansion"][sc["changed_expansion"]].index)
    txt_bouge = (f"le classement de {' et '.join(regions_qui_bougent)} bouge, alors qu'elles ne reçoivent aucun nouvel établissement"
                 if regions_qui_bougent else "aucune autre région ne change de rang")
    story_box(
        f"⚠️ Sur la lecture du scénario « +5 centres » : le score d'Offre de {sc['region_cible']} reste "
        f"mathématiquement inchangé, alors que {txt_bouge}. Ce n'est <b>pas</b> un effet réel du scénario sur "
        f"ces régions : c'est un <b>artefact numérique de la normalisation min-max</b>. Le vrai signal : "
        f"{sc['region_cible']} reste, même après +{sc['croissance_pct']:.0f}% de son parc actuel, la région la "
        "moins bien dotée du pays.", "warning"
    )

    plot_df = sc["scenarios_df"].dropna(subset=["Δ IAFE national"])
    fig = go.Figure(go.Bar(x=plot_df["Δ IAFE national"], y=plot_df["Scénario"], orientation="h",
                            marker=dict(color=plot_df["Δ IAFE national"], colorscale="RdYlGn", cmid=0),
                            text=plot_df["Δ IAFE national"].apply(lambda x: f"{x:+.1f}"), textposition="outside"))
    fig.add_vline(x=0, line_color="black", line_width=1)
    fig.update_layout(title="Effet simulé de chaque scénario sur l'IAFE national", xaxis_title="Δ IAFE national (points)",
                       height=380, margin=dict(t=60, b=10, l=10))
    st.plotly_chart(fig, use_container_width=True)

render_footer()
