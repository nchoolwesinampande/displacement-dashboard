"""
Design system for the Beneficiary Solutions Dashboard.

A single, restrained set of tokens (neutrals + one indigo accent + small,
muted categorical palettes) plus a Plotly styling helper, so every chart in
the app shares the same clean, minimal look.
"""

# ---- Neutrals --------------------------------------------------------------
INK = "#0F172A"        # primary text / headings
INK_SOFT = "#475569"   # body / secondary text
MUTED = "#94A3B8"      # axis ticks, captions
BORDER = "#E5E7EB"     # hairline borders, gridlines
SURFACE = "#FFFFFF"    # cards
CANVAS = "#FFFFFF"     # page background

# ---- Accent ----------------------------------------------------------------
PRIMARY = "#4F46E5"        # indigo
PRIMARY_SOFT = "#EEF2FF"

# ---- Categorical palettes (muted, harmonious) ------------------------------
# Pathway stages read as a neutral -> green progression ("further along").
STAGE_ORDER = ["Assessment", "Planning", "Implementation", "Achieved"]
STAGE_COLORS = {
    "Assessment": "#E2E8F0",
    "Planning": "#A7F3D0",
    "Implementation": "#34D399",
    "Achieved": "#059669",
}

PATHWAY_COLORS = {
    "Return": "#6366F1",            # indigo
    "Local Integration": "#14B8A6",  # teal
    "Relocation": "#F59E0B",        # amber
}

STATUS_COLORS = {
    "IDP": "#3B82F6",            # blue
    "Returnee": "#8B5CF6",       # violet
    "Host Community": "#94A3B8",  # slate
}

SHELTER_COLORS = {
    "Emergency": "#F59E0B",
    "Transitional": "#60A5FA",
    "Permanent": "#059669",
}

DOC_COLORS = {
    "None": "#CBD5E1",
    "Partial": "#A7F3D0",
    "Complete": "#059669",
}

# Generic fallback sequence.
SEQUENCE = ["#4F46E5", "#14B8A6", "#F59E0B", "#3B82F6", "#8B5CF6", "#94A3B8"]

FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


def style_fig(fig, height=360, show_legend=True, y_grid=True, x_grid=False):
    """Apply the shared minimal styling to a Plotly figure (in place)."""
    fig.update_layout(
        font=dict(family=FONT, size=13, color=INK_SOFT),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=8, r=8, t=10, b=8),
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left", x=0,
            title_text="",
            font=dict(size=12, color=INK_SOFT),
        ),
        hoverlabel=dict(
            bgcolor=INK,
            bordercolor=INK,
            font=dict(family=FONT, color="white", size=12),
        ),
        colorway=SEQUENCE,
        bargap=0.35,
    )
    fig.update_xaxes(
        showgrid=x_grid, gridcolor=BORDER, zeroline=False, showline=False,
        ticks="", tickfont=dict(size=12, color=MUTED),
        title_font=dict(size=12, color=MUTED),
    )
    fig.update_yaxes(
        showgrid=y_grid, gridcolor=BORDER, zeroline=False, showline=False,
        ticks="", tickfont=dict(size=12, color=MUTED),
        title_font=dict(size=12, color=MUTED),
    )
    return fig
