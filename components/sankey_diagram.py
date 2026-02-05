"""
Sankey Diagram Component
Visualizes beneficiary flow through displacement status, solutions pathways, and stages.
"""

import plotly.graph_objects as go
import pandas as pd
from typing import List, Tuple


# Professional color palette for humanitarian dashboards
COLORS = {
    # Displacement Status
    'IDP': '#E74C3C',           # Red
    'Returnee': '#3498DB',       # Blue
    'Host Community': '#2ECC71', # Green
    
    # Solutions Pathways
    'Return': '#9B59B6',         # Purple
    'Local Integration': '#F39C12', # Orange
    'Relocation': '#1ABC9C',     # Teal
    
    # Pathway Stages
    'Assessment': '#BDC3C7',     # Light Gray
    'Planning': '#95A5A6',       # Gray
    'Implementation': '#7F8C8D', # Dark Gray
    'Achieved': '#27AE60',       # Success Green
}


def create_sankey(
    df: pd.DataFrame,
    source_col: str = 'displacement_status',
    middle_col: str = 'solutions_pathway',
    target_col: str = 'pathway_stage',
    title: str = 'Beneficiary Flow Through Solutions Pathways'
) -> go.Figure:
    """
    Create an interactive Sankey diagram showing flow from displacement status
    through solutions pathway to pathway stage.
    
    Args:
        df: DataFrame with beneficiary data
        source_col: Column name for the source nodes (default: displacement_status)
        middle_col: Column name for the middle nodes (default: solutions_pathway)
        target_col: Column name for the target nodes (default: pathway_stage)
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    
    # Get unique values for each column
    source_values = df[source_col].unique().tolist()
    middle_values = df[middle_col].unique().tolist()
    target_values = df[target_col].unique().tolist()
    
    # Create node labels (all unique values combined)
    all_labels = source_values + middle_values + target_values
    
    # Create node colors
    node_colors = []
    for label in all_labels:
        node_colors.append(COLORS.get(label, '#7F8C8D'))
    
    # Create mappings for node indices
    label_to_index = {label: idx for idx, label in enumerate(all_labels)}
    
    # Calculate flows from source to middle
    source_to_middle = df.groupby([source_col, middle_col]).size().reset_index(name='count')
    
    # Calculate flows from middle to target
    middle_to_target = df.groupby([middle_col, target_col]).size().reset_index(name='count')
    
    # Build source, target, and value lists for Sankey
    sources = []
    targets = []
    values = []
    link_colors = []
    
    # Add source to middle flows
    for _, row in source_to_middle.iterrows():
        sources.append(label_to_index[row[source_col]])
        targets.append(label_to_index[row[middle_col]])
        values.append(row['count'])
        # Use source color with transparency
        base_color = COLORS.get(row[source_col], '#7F8C8D')
        link_colors.append(f'rgba{tuple(list(int(base_color[i:i+2], 16) for i in (1, 3, 5)) + [0.4])}')
    
    # Add middle to target flows
    for _, row in middle_to_target.iterrows():
        sources.append(label_to_index[row[middle_col]])
        targets.append(label_to_index[row[target_col]])
        values.append(row['count'])
        # Use middle color with transparency
        base_color = COLORS.get(row[middle_col], '#7F8C8D')
        link_colors.append(f'rgba{tuple(list(int(base_color[i:i+2], 16) for i in (1, 3, 5)) + [0.4])}')
    
    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color='white', width=1),
            label=all_labels,
            color=node_colors,
            hovertemplate='%{label}<br>Total: %{value}<extra></extra>'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            hovertemplate='%{source.label} → %{target.label}<br>Count: %{value}<extra></extra>'
        )
    )])
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, color='#2C3E50'),
            x=0.5,
            xanchor='center'
        ),
        font=dict(size=12, color='#2C3E50'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


def create_simple_sankey(
    df: pd.DataFrame,
    source_col: str,
    target_col: str,
    title: str = 'Flow Diagram'
) -> go.Figure:
    """
    Create a simple two-level Sankey diagram.
    
    Args:
        df: DataFrame with beneficiary data
        source_col: Column name for the source nodes
        target_col: Column name for the target nodes
        title: Chart title
        
    Returns:
        Plotly Figure object
    """
    
    # Get unique values
    source_values = df[source_col].unique().tolist()
    target_values = df[target_col].unique().tolist()
    
    # Create node labels
    all_labels = source_values + target_values
    
    # Create node colors
    node_colors = [COLORS.get(label, '#7F8C8D') for label in all_labels]
    
    # Create mappings
    label_to_index = {label: idx for idx, label in enumerate(all_labels)}
    
    # Calculate flows
    flows = df.groupby([source_col, target_col]).size().reset_index(name='count')
    
    sources = [label_to_index[row[source_col]] for _, row in flows.iterrows()]
    targets = [label_to_index[row[target_col]] for _, row in flows.iterrows()]
    values = flows['count'].tolist()
    
    # Create link colors with transparency
    link_colors = []
    for _, row in flows.iterrows():
        base_color = COLORS.get(row[source_col], '#7F8C8D')
        rgb = tuple(int(base_color[i:i+2], 16) for i in (1, 3, 5))
        link_colors.append(f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.4)')
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color='white', width=1),
            label=all_labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors
        )
    )])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16), x=0.5, xanchor='center'),
        font=dict(size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig
