"""
Beneficiary Solutions Dashboard
Monitoring beneficiary progress along durable solutions pathways.

Clean, minimal Streamlit interface.
Author: Nchoolwe Progress Sinampande
"""

import os
import streamlit as st

from components.sankey_diagram import create_sankey
from components.map_visualization import create_cluster_map, create_heatmap
from components.indicator_cards import render_metric_row, render_target_bar
from components.filters import render_sidebar_filters, apply_filters, render_active_filters
from components.charts import (
    funnel_chart, pathway_distribution, status_distribution,
    shelter_distribution, documentation_distribution, trend_chart,
    stage_composition,
)
from utils.data_processing import (
    load_and_process_data, calculate_kpis, get_monthly_trends,
    get_regional_summary,
)
from utils.theme import PRIMARY, STATUS_COLORS, STAGE_COLORS, PATHWAY_COLORS

from streamlit_folium import st_folium

st.set_page_config(
    page_title="Beneficiary Solutions Dashboard",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}


def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "assets", "custom.css")
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), "data", "sample_data.csv")
    return load_and_process_data(path)


def section(title: str, sub: str = "") -> None:
    """Render a quiet section heading."""
    sub_html = f'<div class="section-sub">{sub}</div>' if sub else '<div style="height:12px"></div>'
    st.markdown(f'<div class="section-title">{title}</div>{sub_html}', unsafe_allow_html=True)


def main():
    load_css()
    df = load_data()

    filters = render_sidebar_filters(df)
    fdf = apply_filters(df, filters)
    kpis = calculate_kpis(fdf) if len(fdf) else None

    # ---- Header ----
    st.markdown(
        """
        <div style="margin-bottom:14px;">
            <h1 style="font-size:30px;margin:0;">Beneficiary Solutions Dashboard</h1>
            <p style="font-size:15px;color:#94A3B8;margin:6px 0 0 0;">
                Progress along durable solutions pathways for displaced populations
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_active_filters(filters)

    if not len(fdf):
        st.info("No records match the current filters. Adjust or reset the filters in the sidebar.")
        return

    # ---- KPI strip ----
    achieved_pct = kpis["achievement_rate"] * 100
    render_metric_row([
        {"label": "Households reached", "value": kpis["total_beneficiaries"], "accent": PRIMARY},
        {"label": "Individuals reached", "value": kpis["total_individuals"],
         "accent": "#3B82F6", "caption": f"Avg household {kpis['avg_household_size']:.1f}"},
        {"label": "Solutions achieved", "value": kpis["solutions_achieved"],
         "accent": "#059669", "caption": f"{achieved_pct:.1f}% of caseload"},
        {"label": "Female-headed HH", "value": f"{kpis['female_hoh_percentage'] * 100:.0f}",
         "value_suffix": "%", "accent": "#8B5CF6",
         "caption": f"{kpis['female_hoh_count']:,} households"},
    ])

    st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)

    tab_overview, tab_geo, tab_progress = st.tabs(["Overview", "Geography", "Progress"])

    # ==================== OVERVIEW ====================
    with tab_overview:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        left, right = st.columns([1.05, 1], gap="large")
        with left:
            section("Beneficiaries by stage", "Progress funnel across the caseload")
            st.plotly_chart(funnel_chart(fdf), width="stretch", config=PLOTLY_CONFIG)
        with right:
            section("By solutions pathway", "Return · Local Integration · Relocation")
            st.plotly_chart(pathway_distribution(fdf), width="stretch", config=PLOTLY_CONFIG)
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            section("By displacement status", "")
            st.plotly_chart(status_distribution(fdf), width="stretch", config=PLOTLY_CONFIG)

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        section("Flow to durable solutions",
                "Displacement status → solutions pathway → pathway stage")
        st.plotly_chart(
            create_sankey(fdf, "displacement_status", "solutions_pathway", "pathway_stage"),
            width="stretch", config=PLOTLY_CONFIG,
        )

    # ==================== GEOGRAPHY ====================
    with tab_geo:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        section("Geographic distribution", "Each point is a registered household")

        ctrl1, ctrl2, _ = st.columns([1.4, 1.4, 3])
        with ctrl1:
            color_by = st.selectbox(
                "Colour by",
                ["solutions_pathway", "displacement_status", "pathway_stage"],
                format_func=lambda x: x.replace("_", " ").title(),
            )
        with ctrl2:
            map_type = st.selectbox("Map type", ["Clusters", "Heatmap"])

        if map_type == "Clusters":
            m = create_cluster_map(fdf, color_by=color_by, zoom_start=6)
        else:
            m = create_heatmap(fdf, weight_col="household_size", zoom_start=6)
        st_folium(m, height=500, use_container_width=True, returned_objects=[])

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        section("Regional summary", "")
        summary = get_regional_summary(fdf).rename(columns={
            "region": "Region", "beneficiaries": "Beneficiaries", "individuals": "Individuals",
            "achieved": "Achieved", "livelihood_support": "Livelihood",
            "achievement_rate": "Achievement %", "female_hoh_rate": "Female HoH %",
        })[["Region", "Beneficiaries", "Individuals", "Achieved",
            "Livelihood", "Achievement %", "Female HoH %"]]
        st.dataframe(
            summary.style
            .format({"Beneficiaries": "{:,.0f}", "Individuals": "{:,.0f}",
                     "Achieved": "{:,.0f}", "Livelihood": "{:,.0f}",
                     "Achievement %": "{:.1f}%", "Female HoH %": "{:.1f}%"})
            .background_gradient(subset=["Achievement %"], cmap="Greens"),
            width="stretch", hide_index=True,
        )

    # ==================== PROGRESS ====================
    with tab_progress:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        section("Registrations over time", "Monthly intake and cumulative reach")
        st.plotly_chart(trend_chart(get_monthly_trends(fdf)), width="stretch", config=PLOTLY_CONFIG)

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2, gap="large")
        with c1:
            section("Stage by region", "")
            st.plotly_chart(stage_composition(fdf, "region"), width="stretch", config=PLOTLY_CONFIG)
        with c2:
            section("Stage by pathway", "")
            st.plotly_chart(stage_composition(fdf, "solutions_pathway"), width="stretch", config=PLOTLY_CONFIG)

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        c3, c4 = st.columns(2, gap="large")
        with c3:
            section("Shelter status", "")
            st.plotly_chart(shelter_distribution(fdf), width="stretch", config=PLOTLY_CONFIG)
        with c4:
            section("Documentation status", "")
            st.plotly_chart(documentation_distribution(fdf), width="stretch", config=PLOTLY_CONFIG)

        st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
        section("Progress against targets", "Programme planning goals, not derived from actuals")

        total = kpis["total_beneficiaries"]
        tcol1, tcol2 = st.columns(2, gap="large")
        with tcol1:
            st.markdown("**Effectiveness**")
            render_target_bar("Solutions achieved (35%)", kpis["solutions_achieved"],
                              round(total * 0.35), accent="#059669")
            render_target_bar("Livelihood support (60%)", kpis["livelihood_support_count"],
                              round(total * 0.60), accent="#3B82F6")
            render_target_bar("Complete documentation (75%)", kpis["complete_documentation"],
                              round(total * 0.75), accent="#8B5CF6")
            render_target_bar("Permanent shelter (45%)", kpis["permanent_shelter"],
                              round(total * 0.45), accent="#14B8A6")
        with tcol2:
            st.markdown("**Coverage**")
            render_target_bar("Total beneficiaries reached", kpis["total_beneficiaries"],
                              600, accent=PRIMARY)
            render_target_bar("Female-headed households (40%)",
                              kpis["female_hoh_percentage"] * 100, 40, accent="#8B5CF6", unit="%")
            render_target_bar("Regions covered", kpis["regions_covered"],
                              df["region"].nunique(), accent="#F59E0B")
            render_target_bar("Districts covered", kpis["districts_covered"],
                              df["district"].nunique(), accent="#3B82F6")

    st.markdown(
        """
        <div class="dashboard-footer">
            Beneficiary Solutions Dashboard · Built with Streamlit ·
            Developed by Nchoolwe Progress Sinampande
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
