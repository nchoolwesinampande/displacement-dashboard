"""
Displacement Solutions Dashboard
Main Streamlit application for visualizing beneficiary progress along durable solutions pathways.

Author: Nchoolwe Progress Sinampande
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
import os

# Import custom components
from components.sankey_diagram import create_sankey, create_simple_sankey
from components.map_visualization import create_cluster_map, create_heatmap
from components.indicator_cards import render_kpi_card, render_kpi_row, render_progress_indicator
from components.filters import render_sidebar_filters, apply_filters, render_active_filters

# Import utilities
from utils.data_processing import (
    load_and_process_data,
    calculate_kpis,
    get_monthly_trends,
    get_regional_summary,
    get_pathway_progress
)


# Page configuration
st.set_page_config(
    page_title="Displacement Solutions Dashboard",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css_file = os.path.join(os.path.dirname(__file__), 'assets', 'custom.css')
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()


# Cache data loading
@st.cache_data
def load_data():
    """Load and cache the dataset."""
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'sample_data.csv')
    return load_and_process_data(data_path)


def main():
    """Main application function."""
    
    # Load data
    df = load_data()
    
    # Render sidebar filters
    filters = render_sidebar_filters(df)
    
    # Apply filters
    filtered_df = apply_filters(df, filters)
    
    # Calculate KPIs
    kpis = calculate_kpis(filtered_df)
    
    # Main content area
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 style="color: #2C3E50; margin-bottom: 5px; font-weight: 600;">
            Displacement Solutions Dashboard
        </h1>
        <p style="color: #7F8C8D; font-size: 16px;">
            Monitoring progress along durable solutions pathways for displaced populations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show active filters
    render_active_filters(filters)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview",
        "Geographic View", 
        "Progress Analysis",
        "Indicators"
    ])
    
    # ==================== TAB 1: OVERVIEW ====================
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # KPI Row
        kpi_data = [
            {
                'title': 'Total Beneficiaries',
                'value': kpis['total_beneficiaries'],
                'delta': None,
                'icon': '',
                'color': '#3498DB'
            },
            {
                'title': 'Individuals Reached',
                'value': kpis['total_individuals'],
                'delta': None,
                'icon': '',
                'color': '#9B59B6'
            },
            {
                'title': 'Solutions Achieved',
                'value': kpis['solutions_achieved'],
                'delta': None,
                'icon': '',
                'color': '#27AE60'
            },
            {
                'title': 'Female-Headed HH',
                'value': kpis['female_hoh_percentage'],
                'delta': None,
                'icon': '',
                'color': '#E74C3C'
            }
        ]
        
        render_kpi_row(kpi_data)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Sankey Diagram
        st.markdown("""
        <h3 style="color: #2C3E50; margin-bottom: 15px; font-weight: 600;">
            Beneficiary Flow Through Solutions Pathways
        </h3>
        """, unsafe_allow_html=True)
        
        sankey_fig = create_sankey(
            filtered_df,
            source_col='displacement_status',
            middle_col='solutions_pathway',
            target_col='pathway_stage',
            title=''
        )
        st.plotly_chart(sankey_fig, width='stretch')
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Two column layout for additional charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <h4 style="color: #2C3E50;">Distribution by Solutions Pathway</h4>
            """, unsafe_allow_html=True)
            
            pathway_counts = filtered_df['solutions_pathway'].value_counts()
            fig_pathway = px.pie(
                values=pathway_counts.values,
                names=pathway_counts.index,
                hole=0.4,
                color_discrete_sequence=['#9B59B6', '#F39C12', '#1ABC9C']
            )
            fig_pathway.update_layout(
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2),
                margin=dict(t=20, b=20, l=20, r=20),
                height=350
            )
            st.plotly_chart(fig_pathway, width='stretch')
        
        with col2:
            st.markdown("""
            <h4 style="color: #2C3E50;">Distribution by Displacement Status</h4>
            """, unsafe_allow_html=True)
            
            status_counts = filtered_df['displacement_status'].value_counts()
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                hole=0.4,
                color_discrete_sequence=['#E74C3C', '#3498DB', '#2ECC71']
            )
            fig_status.update_layout(
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2),
                margin=dict(t=20, b=20, l=20, r=20),
                height=350
            )
            st.plotly_chart(fig_status, width='stretch')
    
    # ==================== TAB 2: GEOGRAPHIC VIEW ====================
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <h3 style="color: #2C3E50; margin-bottom: 15px; font-weight: 600;">
            Geographic Distribution of Beneficiaries
        </h3>
        """, unsafe_allow_html=True)
        
        # Map controls
        map_col1, map_col2 = st.columns([3, 1])
        
        with map_col2:
            color_by = st.selectbox(
                'Color markers by:',
                ['solutions_pathway', 'displacement_status', 'pathway_stage'],
                format_func=lambda x: x.replace('_', ' ').title()
            )
            
            map_type = st.radio(
                'Map type:',
                ['Cluster Map', 'Heat Map'],
                horizontal=True
            )
        
        with map_col1:
            if map_type == 'Cluster Map':
                m = create_cluster_map(
                    filtered_df,
                    lat_col='latitude',
                    lon_col='longitude',
                    color_by=color_by,
                    zoom_start=6
                )
            else:
                m = create_heatmap(
                    filtered_df,
                    lat_col='latitude',
                    lon_col='longitude',
                    weight_col='household_size',
                    zoom_start=6
                )
            
            st_folium(m, height=500, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Regional summary table
        st.markdown("""
        <h4 style="color: #2C3E50; margin-bottom: 15px; font-weight: 600;">
            Regional Summary
        </h4>
        """, unsafe_allow_html=True)
        
        regional_summary = get_regional_summary(filtered_df)
        
        # Style the dataframe
        st.dataframe(
            regional_summary.style.format({
                'beneficiaries': '{:,.0f}',
                'individuals': '{:,.0f}',
                'female_hoh': '{:,.0f}',
                'achieved': '{:,.0f}',
                'livelihood_support': '{:,.0f}',
                'achievement_rate': '{:.1f}%',
                'female_hoh_rate': '{:.1f}%'
            }).background_gradient(subset=['achievement_rate'], cmap='Greens'),
            width='stretch',
            hide_index=True
        )
    
    # ==================== TAB 3: PROGRESS ANALYSIS ====================
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Monthly trends
        st.markdown("""
        <h3 style="color: #2C3E50; margin-bottom: 15px; font-weight: 600;">
            Registration Trends Over Time
        </h3>
        """, unsafe_allow_html=True)
        
        monthly_data = get_monthly_trends(filtered_df)
        
        fig_trends = go.Figure()
        
        fig_trends.add_trace(go.Bar(
            x=monthly_data['month'],
            y=monthly_data['value'],
            name='Monthly Registrations',
            marker_color='#3498DB'
        ))
        
        fig_trends.add_trace(go.Scatter(
            x=monthly_data['month'],
            y=monthly_data['cumulative'],
            name='Cumulative',
            line=dict(color='#E74C3C', width=3),
            yaxis='y2'
        ))
        
        fig_trends.update_layout(
            xaxis=dict(title='Month', tickangle=-45),
            yaxis=dict(title='Monthly Count', side='left'),
            yaxis2=dict(title='Cumulative', side='right', overlaying='y'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
            margin=dict(t=50, b=100),
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_trends, width='stretch')
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Progress by pathway and region
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <h4 style="color: #2C3E50;">Progress by Region</h4>
            """, unsafe_allow_html=True)
            
            region_stage = filtered_df.groupby(['region', 'pathway_stage']).size().unstack(fill_value=0)
            stage_order = ['Assessment', 'Planning', 'Implementation', 'Achieved']
            region_stage = region_stage.reindex(columns=[c for c in stage_order if c in region_stage.columns])
            
            fig_region = px.bar(
                region_stage.reset_index().melt(id_vars='region'),
                x='region',
                y='value',
                color='pathway_stage',
                color_discrete_map={
                    'Assessment': '#BDC3C7',
                    'Planning': '#F39C12',
                    'Implementation': '#3498DB',
                    'Achieved': '#27AE60'
                },
                barmode='stack'
            )
            fig_region.update_layout(
                xaxis_title='',
                yaxis_title='Beneficiaries',
                legend_title='Stage',
                margin=dict(t=20),
                height=400
            )
            st.plotly_chart(fig_region, width='stretch')
        
        with col2:
            st.markdown("""
            <h4 style="color: #2C3E50;">Progress by Solutions Pathway</h4>
            """, unsafe_allow_html=True)
            
            pathway_stage = filtered_df.groupby(['solutions_pathway', 'pathway_stage']).size().unstack(fill_value=0)
            pathway_stage = pathway_stage.reindex(columns=[c for c in stage_order if c in pathway_stage.columns])
            
            fig_pathway = px.bar(
                pathway_stage.reset_index().melt(id_vars='solutions_pathway'),
                x='solutions_pathway',
                y='value',
                color='pathway_stage',
                color_discrete_map={
                    'Assessment': '#BDC3C7',
                    'Planning': '#F39C12',
                    'Implementation': '#3498DB',
                    'Achieved': '#27AE60'
                },
                barmode='group'
            )
            fig_pathway.update_layout(
                xaxis_title='',
                yaxis_title='Beneficiaries',
                legend_title='Stage',
                margin=dict(t=20),
                height=400
            )
            st.plotly_chart(fig_pathway, width='stretch')
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Shelter and support analysis
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("""
            <h4 style="color: #2C3E50;">Shelter Status Distribution</h4>
            """, unsafe_allow_html=True)
            
            shelter_counts = filtered_df['shelter_status'].value_counts()
            fig_shelter = px.bar(
                x=shelter_counts.index,
                y=shelter_counts.values,
                color=shelter_counts.index,
                color_discrete_map={
                    'Emergency': '#E74C3C',
                    'Transitional': '#F39C12',
                    'Permanent': '#27AE60'
                }
            )
            fig_shelter.update_layout(
                xaxis_title='',
                yaxis_title='Beneficiaries',
                showlegend=False,
                margin=dict(t=20),
                height=300
            )
            st.plotly_chart(fig_shelter, width='stretch')
        
        with col4:
            st.markdown("""
            <h4 style="color: #2C3E50;">Documentation Status</h4>
            """, unsafe_allow_html=True)
            
            doc_counts = filtered_df['documentation_status'].value_counts()
            fig_doc = px.bar(
                x=doc_counts.index,
                y=doc_counts.values,
                color=doc_counts.index,
                color_discrete_map={
                    'None': '#E74C3C',
                    'Partial': '#F39C12',
                    'Complete': '#27AE60'
                }
            )
            fig_doc.update_layout(
                xaxis_title='',
                yaxis_title='Beneficiaries',
                showlegend=False,
                margin=dict(t=20),
                height=300
            )
            st.plotly_chart(fig_doc, width='stretch')
    
    # ==================== TAB 4: INDICATORS ====================
    with tab4:
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <h3 style="color: #2C3E50; margin-bottom: 15px; font-weight: 600;">
            Programme Indicators (OECD-DAC Aligned)
        </h3>
        <p style="color: #7F8C8D; margin-bottom: 25px;">
            Progress tracking against key durable solutions indicators
        </p>
        """, unsafe_allow_html=True)
        
        # Define indicators with targets
        total_target = 500  # Adjust based on your programme targets
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Effectiveness Indicators")
            
            render_progress_indicator(
                title="Solutions Achieved (Target: 100)",
                current=kpis['solutions_achieved'],
                target=100,
                color="#27AE60"
            )
            
            render_progress_indicator(
                title="Livelihood Support Provided (Target: 300)",
                current=kpis['livelihood_support_count'],
                target=300,
                color="#3498DB"
            )
            
            render_progress_indicator(
                title="Complete Documentation (Target: 250)",
                current=kpis['complete_documentation'],
                target=250,
                color="#9B59B6"
            )
            
            render_progress_indicator(
                title="Permanent Shelter (Target: 80)",
                current=kpis['permanent_shelter'],
                target=80,
                color="#1ABC9C"
            )
        
        with col2:
            st.markdown("#### Coverage Indicators")
            
            render_progress_indicator(
                title=f"Total Beneficiaries Reached (Target: {total_target})",
                current=kpis['total_beneficiaries'],
                target=total_target,
                color="#3498DB"
            )
            
            render_progress_indicator(
                title="Female-Headed Households (Target: 40%)",
                current=kpis['female_hoh_percentage'] * 100,
                target=40,
                color="#E74C3C"
            )
            
            render_progress_indicator(
                title="Regions Covered (Target: 5)",
                current=kpis['regions_covered'],
                target=5,
                color="#F39C12"
            )
            
            render_progress_indicator(
                title="Districts Covered (Target: 10)",
                current=kpis['districts_covered'],
                target=10,
                color="#2ECC71"
            )
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Pathway progress table
        st.markdown("""
        <h4 style="color: #2C3E50; margin-bottom: 15px; font-weight: 600;">
            Detailed Pathway Progress Matrix
        </h4>
        """, unsafe_allow_html=True)
        
        pathway_progress = get_pathway_progress(filtered_df)
        
        st.dataframe(
            pathway_progress.style.format({
                'Achievement Rate': '{:.1f}%'
            }).background_gradient(subset=['Achievement Rate'], cmap='Greens'),
            width='stretch'
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Summary statistics
        st.markdown("""
        <h4 style="color: #2C3E50; margin-bottom: 15px; font-weight: 600;">
            Key Statistics Summary
        </h4>
        """, unsafe_allow_html=True)
        
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        
        with stats_col1:
            st.metric(
                label="Average Household Size",
                value=f"{kpis['avg_household_size']:.1f}"
            )
        
        with stats_col2:
            st.metric(
                label="Achievement Rate",
                value=f"{kpis['achievement_rate']*100:.1f}%"
            )
        
        with stats_col3:
            st.metric(
                label="Livelihood Coverage",
                value=f"{kpis['livelihood_support_percentage']*100:.1f}%"
            )
        
        with stats_col4:
            st.metric(
                label="Documentation Rate",
                value=f"{kpis['documentation_rate']*100:.1f}%"
            )
    
    # Footer
    st.markdown("""
    <div class="dashboard-footer">
        <p>
            Displacement Solutions Dashboard | Built with Streamlit<br>
            Data updated: Sample Data | Developed by Nchoolwe Progress Sinampande
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
