"""
Sankey flow diagram: displacement status → solutions pathway → pathway stage.
Restyled to the minimal design system (muted nodes, soft links, no chrome).
"""

import plotly.graph_objects as go
import pandas as pd

from utils.theme import (
    STAGE_COLORS, PATHWAY_COLORS, STATUS_COLORS, MUTED, INK_SOFT, FONT,
)

# Single lookup for every node label across the three columns.
NODE_COLORS = {**STATUS_COLORS, **PATHWAY_COLORS, **STAGE_COLORS}


def _rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


def create_sankey(
    df: pd.DataFrame,
    source_col: str = "displacement_status",
    middle_col: str = "solutions_pathway",
    target_col: str = "pathway_stage",
    title: str = "",
) -> go.Figure:
    """Three-column Sankey of beneficiary flow."""
    source_values = df[source_col].unique().tolist()
    middle_values = df[middle_col].unique().tolist()
    target_values = df[target_col].unique().tolist()
    labels = source_values + middle_values + target_values
    idx = {label: i for i, label in enumerate(labels)}
    node_colors = [NODE_COLORS.get(label, MUTED) for label in labels]

    sources, targets, values, link_colors = [], [], [], []

    def add_flows(left_col, right_col):
        flows = df.groupby([left_col, right_col]).size().reset_index(name="count")
        for _, row in flows.iterrows():
            sources.append(idx[row[left_col]])
            targets.append(idx[row[right_col]])
            values.append(int(row["count"]))
            link_colors.append(_rgba(NODE_COLORS.get(row[left_col], MUTED), 0.28))

    add_flows(source_col, middle_col)
    add_flows(middle_col, target_col)

    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            pad=22,
            thickness=14,
            line=dict(color="white", width=0),
            label=labels,
            color=node_colors,
            hovertemplate="%{label}: %{value}<extra></extra>",
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            hovertemplate="%{source.label} → %{target.label}: %{value}<extra></extra>",
        ),
    ))
    fig.update_layout(
        font=dict(family=FONT, size=13, color=INK_SOFT),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=440,
        margin=dict(l=8, r=8, t=10, b=10),
    )
    return fig
