"""
Components package for the Beneficiary Solutions Dashboard.
Contains visualization and UI components.
"""

from .sankey_diagram import create_sankey
from .map_visualization import create_cluster_map, create_heatmap
from .indicator_cards import render_metric, render_metric_row, render_target_bar
from .filters import render_sidebar_filters, apply_filters, render_active_filters
from .charts import (
    funnel_chart, pathway_distribution, status_distribution,
    shelter_distribution, documentation_distribution, trend_chart,
    stage_composition,
)

__all__ = [
    "create_sankey",
    "create_cluster_map",
    "create_heatmap",
    "render_metric",
    "render_metric_row",
    "render_target_bar",
    "render_sidebar_filters",
    "apply_filters",
    "render_active_filters",
    "funnel_chart",
    "pathway_distribution",
    "status_distribution",
    "shelter_distribution",
    "documentation_distribution",
    "trend_chart",
    "stage_composition",
]
