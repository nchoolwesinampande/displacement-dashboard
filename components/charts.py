"""
Chart builders for the dashboard.

Minimal, consistent Plotly figures (mostly horizontal bars and a single flow
diagram) styled through utils.theme.style_fig. Pies and heavy chrome are
deliberately avoided in favour of bars that read clearly with lots of
whitespace.
"""

import pandas as pd
import plotly.graph_objects as go

from utils.theme import (
    STAGE_ORDER, STAGE_COLORS, PATHWAY_COLORS, STATUS_COLORS,
    SHELTER_COLORS, DOC_COLORS, PRIMARY, INK, INK_SOFT, MUTED, BORDER,
    style_fig,
)


def funnel_chart(df: pd.DataFrame) -> go.Figure:
    """Horizontal funnel of beneficiaries by pathway stage (Assessment → Achieved)."""
    counts = df["pathway_stage"].value_counts()
    values = [int(counts.get(s, 0)) for s in STAGE_ORDER]
    total = max(sum(values), 1)

    # Reverse so Assessment sits at the top, Achieved at the bottom.
    labels = STAGE_ORDER[::-1]
    vals = values[::-1]

    fig = go.Figure(go.Bar(
        y=labels,
        x=vals,
        orientation="h",
        marker=dict(color=[STAGE_COLORS[s] for s in labels],
                    line=dict(width=0)),
        text=[f"{v:,}  ·  {v / total * 100:.0f}%" for v in vals],
        textposition="outside",
        textfont=dict(size=12, color=INK_SOFT),
        hovertemplate="%{y}: %{x:,}<extra></extra>",
        width=0.6,
    ))
    style_fig(fig, height=300, show_legend=False, y_grid=False)
    fig.update_xaxes(visible=False, range=[0, max(vals) * 1.18 if vals else 1])
    fig.update_yaxes(tickfont=dict(size=14, color=INK))
    fig.update_layout(margin=dict(l=8, r=64, t=8, b=8))
    return fig


def _category_hbar(counts: pd.Series, color_map: dict, height: int = 240) -> go.Figure:
    """Sorted horizontal bar chart for a categorical breakdown."""
    counts = counts.sort_values(ascending=True)
    total = max(int(counts.sum()), 1)
    colors = [color_map.get(idx, PRIMARY) for idx in counts.index]

    fig = go.Figure(go.Bar(
        y=list(counts.index),
        x=list(counts.values),
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{int(v):,}  ·  {v / total * 100:.0f}%" for v in counts.values],
        textposition="outside",
        textfont=dict(size=12, color=INK_SOFT),
        hovertemplate="%{y}: %{x:,}<extra></extra>",
        width=0.62,
    ))
    style_fig(fig, height=height, show_legend=False, y_grid=False)
    fig.update_xaxes(visible=False, range=[0, max(counts.values) * 1.22 if len(counts) else 1])
    fig.update_yaxes(tickfont=dict(size=13, color=INK))
    fig.update_layout(margin=dict(l=8, r=72, t=8, b=8))
    return fig


def pathway_distribution(df: pd.DataFrame) -> go.Figure:
    return _category_hbar(df["solutions_pathway"].value_counts(), PATHWAY_COLORS)


def status_distribution(df: pd.DataFrame) -> go.Figure:
    return _category_hbar(df["displacement_status"].value_counts(), STATUS_COLORS)


def shelter_distribution(df: pd.DataFrame) -> go.Figure:
    order = ["Emergency", "Transitional", "Permanent"]
    counts = df["shelter_status"].value_counts().reindex(order).fillna(0)
    return _category_hbar(counts, SHELTER_COLORS, height=220)


def documentation_distribution(df: pd.DataFrame) -> go.Figure:
    order = ["None", "Partial", "Complete"]
    counts = df["documentation_status"].value_counts().reindex(order).fillna(0)
    return _category_hbar(counts, DOC_COLORS, height=220)


def trend_chart(monthly: pd.DataFrame) -> go.Figure:
    """Monthly registrations (soft bars) with a cumulative line on a 2nd axis."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly["month"],
        y=monthly["value"],
        name="Registered",
        marker=dict(color="#C7D2FE", line=dict(width=0)),
        hovertemplate="%{x}: %{y:,}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=monthly["month"],
        y=monthly["cumulative"],
        name="Cumulative",
        mode="lines",
        line=dict(color=PRIMARY, width=2.5, shape="spline"),
        yaxis="y2",
        hovertemplate="%{x}: %{y:,} total<extra></extra>",
    ))
    style_fig(fig, height=320, show_legend=True)
    fig.update_layout(
        yaxis=dict(title_text=""),
        yaxis2=dict(overlaying="y", side="right", showgrid=False,
                    tickfont=dict(size=12, color=MUTED)),
        margin=dict(l=8, r=8, t=36, b=8),
        bargap=0.45,
    )
    fig.update_xaxes(tickangle=-45)
    return fig


def stage_composition(df: pd.DataFrame, by: str) -> go.Figure:
    """Stacked horizontal bars: stage mix within each category (region/pathway)."""
    pivot = (
        df.groupby([by, "pathway_stage"]).size().unstack(fill_value=0)
        .reindex(columns=STAGE_ORDER, fill_value=0)
    )
    # Order rows by total caseload (largest at top).
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=True).index]

    fig = go.Figure()
    for stage in STAGE_ORDER:
        fig.add_trace(go.Bar(
            y=list(pivot.index),
            x=list(pivot[stage].values),
            name=stage,
            orientation="h",
            marker=dict(color=STAGE_COLORS[stage], line=dict(width=0)),
            hovertemplate="%{y} · " + stage + ": %{x:,}<extra></extra>",
        ))
    style_fig(fig, height=300, show_legend=True, y_grid=False)
    fig.update_layout(barmode="stack", margin=dict(l=8, r=8, t=36, b=8))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(tickfont=dict(size=13, color=INK))
    return fig
