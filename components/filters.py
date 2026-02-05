"""
Filters Component
Renders sidebar filter controls for dashboard interactivity.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


def render_sidebar_filters(
    df: pd.DataFrame,
    date_col: str = 'registration_date'
) -> Dict:
    """
    Render sidebar filter controls and return selected filter values.
    
    Args:
        df: DataFrame with beneficiary data
        date_col: Column name for date filtering
        
    Returns:
        Dictionary of selected filter values
    """
    
    filters = {}
    
    # Dashboard header
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 10px 0 20px 0;">
        <h2 style="color: #2C3E50; margin: 0; font-weight: 600;">Solutions Dashboard</h2>
        <p style="color: #7F8C8D; font-size: 12px; margin: 5px 0 0 0;">
            Displacement Solutions Monitoring
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Filter section header
    st.sidebar.markdown("""
    <p style="color: #2C3E50; font-weight: 600; font-size: 14px; margin-bottom: 15px;">
        Filter Data
    </p>
    """, unsafe_allow_html=True)
    
    # Region filter
    regions = ['All'] + sorted(df['region'].unique().tolist())
    filters['region'] = st.sidebar.selectbox(
        'Region',
        options=regions,
        index=0,
        help="Filter by geographic region"
    )
    
    # District filter (dependent on region)
    if filters['region'] != 'All':
        districts = ['All'] + sorted(df[df['region'] == filters['region']]['district'].unique().tolist())
    else:
        districts = ['All'] + sorted(df['district'].unique().tolist())
    
    filters['district'] = st.sidebar.selectbox(
        'District',
        options=districts,
        index=0,
        help="Filter by district"
    )
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    
    # Solutions pathway filter
    pathways = ['All'] + sorted(df['solutions_pathway'].unique().tolist())
    filters['solutions_pathway'] = st.sidebar.selectbox(
        'Solutions Pathway',
        options=pathways,
        index=0,
        help="Filter by durable solutions pathway"
    )
    
    # Pathway stage filter
    stages = ['All'] + ['Assessment', 'Planning', 'Implementation', 'Achieved']
    filters['pathway_stage'] = st.sidebar.selectbox(
        'Pathway Stage',
        options=stages,
        index=0,
        help="Filter by progress stage"
    )
    
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    
    # Displacement status filter
    statuses = ['All'] + sorted(df['displacement_status'].unique().tolist())
    filters['displacement_status'] = st.sidebar.selectbox(
        'Displacement Status',
        options=statuses,
        index=0,
        help="Filter by displacement status"
    )
    
    st.sidebar.markdown("---")
    
    # Date range filter
    st.sidebar.markdown("""
    <p style="color: #2C3E50; font-weight: 600; font-size: 14px; margin-bottom: 15px;">
        Date Range
    </p>
    """, unsafe_allow_html=True)
    
    # Convert date column to datetime if needed
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col])
        min_date = df[date_col].min().date()
        max_date = df[date_col].max().date()
        
        date_range = st.sidebar.date_input(
            'Registration Period',
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            help="Filter by registration date range"
        )
        
        # Handle single date selection
        if isinstance(date_range, tuple) and len(date_range) == 2:
            filters['date_start'] = date_range[0]
            filters['date_end'] = date_range[1]
        else:
            filters['date_start'] = min_date
            filters['date_end'] = max_date
    
    st.sidebar.markdown("---")
    
    # Additional filters (collapsible)
    with st.sidebar.expander("Additional Filters", expanded=False):
        # Gender of HoH filter
        genders = ['All'] + sorted(df['gender_hoh'].unique().tolist())
        filters['gender_hoh'] = st.selectbox(
            'Gender of Head of Household',
            options=genders,
            index=0
        )
        
        # Shelter status filter
        shelter_statuses = ['All'] + sorted(df['shelter_status'].unique().tolist())
        filters['shelter_status'] = st.selectbox(
            'Shelter Status',
            options=shelter_statuses,
            index=0
        )
        
        # Livelihood support filter
        livelihood_options = ['All', 'Yes', 'No']
        filters['livelihood_support'] = st.selectbox(
            'Livelihood Support',
            options=livelihood_options,
            index=0
        )
        
        # Documentation status filter
        doc_statuses = ['All'] + sorted([x for x in df['documentation_status'].unique().tolist() if pd.notna(x)])
        filters['documentation_status'] = st.selectbox(
            'Documentation Status',
            options=doc_statuses,
            index=0
        )
        
        # Household size filter
        min_hh = int(df['household_size'].min())
        max_hh = int(df['household_size'].max())
        filters['household_size_range'] = st.slider(
            'Household Size',
            min_value=min_hh,
            max_value=max_hh,
            value=(min_hh, max_hh)
        )
    
    st.sidebar.markdown("---")
    
    # Reset filters button
    if st.sidebar.button('Reset All Filters', width='stretch'):
        st.rerun()
    
    # Data summary
    st.sidebar.markdown("""
    <div style="
        background-color: #f0f2f5;
        border-radius: 8px;
        padding: 12px;
        margin-top: 15px;
    ">
        <p style="color: #7F8C8D; font-size: 11px; margin: 0 0 5px 0;">
            Data loaded from sample_data.csv
        </p>
        <p style="color: #2C3E50; font-size: 12px; margin: 0;">
            Total records: <strong>{:,}</strong>
        </p>
    </div>
    """.format(len(df)), unsafe_allow_html=True)
    
    return filters


def apply_filters(df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
    """
    Apply filter selections to the DataFrame.
    
    Args:
        df: Original DataFrame
        filters: Dictionary of filter values from render_sidebar_filters
        
    Returns:
        Filtered DataFrame
    """
    
    filtered_df = df.copy()
    
    # Apply categorical filters
    categorical_filters = [
        'region', 'district', 'solutions_pathway', 'pathway_stage',
        'displacement_status', 'gender_hoh', 'shelter_status',
        'livelihood_support', 'documentation_status'
    ]
    
    for col in categorical_filters:
        if col in filters and filters[col] != 'All':
            filtered_df = filtered_df[filtered_df[col] == filters[col]]
    
    # Apply date filter
    if 'date_start' in filters and 'date_end' in filters:
        filtered_df['registration_date'] = pd.to_datetime(filtered_df['registration_date'])
        filtered_df = filtered_df[
            (filtered_df['registration_date'].dt.date >= filters['date_start']) &
            (filtered_df['registration_date'].dt.date <= filters['date_end'])
        ]
    
    # Apply household size range filter
    if 'household_size_range' in filters:
        min_size, max_size = filters['household_size_range']
        filtered_df = filtered_df[
            (filtered_df['household_size'] >= min_size) &
            (filtered_df['household_size'] <= max_size)
        ]
    
    return filtered_df


def get_quick_filter_buttons(df: pd.DataFrame) -> Optional[str]:
    """
    Render quick filter buttons for common selections.
    
    Args:
        df: DataFrame for context
        
    Returns:
        Selected quick filter or None
    """
    
    st.markdown("""
    <p style="color: #7F8C8D; font-size: 12px; margin-bottom: 10px;">
        Quick Filters
    </p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    quick_filter = None
    
    with col1:
        if st.button("Achieved", width='stretch'):
            quick_filter = "achieved"
    
    with col2:
        if st.button("IDPs Only", width='stretch'):
            quick_filter = "idp"
    
    with col3:
        if st.button("Female HoH", width='stretch'):
            quick_filter = "female_hoh"
    
    with col4:
        if st.button("Emergency", width='stretch'):
            quick_filter = "emergency"
    
    return quick_filter


def render_active_filters(filters: Dict) -> None:
    """
    Display currently active filters as tags.
    
    Args:
        filters: Dictionary of current filter values
    """
    
    active_filters = []
    
    for key, value in filters.items():
        if value != 'All' and value is not None and not key.startswith('date'):
            if key == 'household_size_range':
                continue
            display_key = key.replace('_', ' ').title()
            active_filters.append(f"{display_key}: {value}")
    
    if active_filters:
        tags_html = " ".join([
            f'<span style="background-color: #E8F4FD; color: #2980B9; padding: 4px 10px; '
            f'border-radius: 15px; font-size: 12px; margin-right: 8px;">{f}</span>'
            for f in active_filters
        ])
        
        st.markdown(f"""
        <div style="margin-bottom: 15px;">
            <span style="color: #7F8C8D; font-size: 12px; margin-right: 10px;">Active filters:</span>
            {tags_html}
        </div>
        """, unsafe_allow_html=True)
