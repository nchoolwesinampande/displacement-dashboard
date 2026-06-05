"""
Geographic visualisation: a clean light-basemap cluster map and a heatmap.
Marker colours come from the shared design system.
"""

import folium
from folium.plugins import MarkerCluster, HeatMap
import pandas as pd
from typing import Optional, List, Dict

from utils.theme import (
    PATHWAY_COLORS, STATUS_COLORS, STAGE_COLORS, INK, INK_SOFT, MUTED, BORDER,
)

_COLOR_MAPS = {
    "solutions_pathway": PATHWAY_COLORS,
    "displacement_status": STATUS_COLORS,
    "pathway_stage": STAGE_COLORS,
}


def _color_map_for(color_by: str) -> Dict[str, str]:
    return _COLOR_MAPS.get(color_by, PATHWAY_COLORS)


def create_cluster_map(
    df: pd.DataFrame,
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    color_by: str = "solutions_pathway",
    zoom_start: int = 6,
    center: Optional[List[float]] = None,
) -> folium.Map:
    """Light cluster map with colour-coded circle markers and a minimal legend."""
    if center is None:
        center = [df[lat_col].mean(), df[lon_col].mean()] if len(df) else [5.15, 46.2]

    color_map = _color_map_for(color_by)

    m = folium.Map(
        location=center,
        zoom_start=zoom_start,
        tiles="CartoDB positron",
        control_scale=True,
    )

    cluster = MarkerCluster(options={"maxClusterRadius": 45, "showCoverageOnHover": False})

    for _, row in df.iterrows():
        marker_color = color_map.get(row.get(color_by, ""), MUTED)
        popup_html = f"""
        <div style="font-family:Inter,sans-serif;width:190px;color:{INK};">
            <div style="font-weight:600;font-size:13px;border-bottom:1px solid {BORDER};
                        padding-bottom:6px;margin-bottom:6px;">{row.get('beneficiary_id','')}</div>
            <table style="width:100%;font-size:12px;color:{INK_SOFT};">
                <tr><td>Region</td><td style="text-align:right;color:{INK};">{row.get('region','')}</td></tr>
                <tr><td>District</td><td style="text-align:right;color:{INK};">{row.get('district','')}</td></tr>
                <tr><td>Status</td><td style="text-align:right;color:{INK};">{row.get('displacement_status','')}</td></tr>
                <tr><td>Pathway</td><td style="text-align:right;color:{INK};">{row.get('solutions_pathway','')}</td></tr>
                <tr><td>Stage</td><td style="text-align:right;color:{INK};">{row.get('pathway_stage','')}</td></tr>
                <tr><td>Household</td><td style="text-align:right;color:{INK};">{row.get('household_size','')}</td></tr>
            </table>
        </div>
        """
        folium.CircleMarker(
            location=[row[lat_col], row[lon_col]],
            radius=6,
            popup=folium.Popup(popup_html, max_width=240),
            color=marker_color,
            weight=1,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.75,
        ).add_to(cluster)

    cluster.add_to(m)
    m.get_root().html.add_child(folium.Element(_legend_html(color_by, color_map)))
    return m


def _legend_html(color_by: str, color_map: Dict[str, str]) -> str:
    title = color_by.replace("_", " ").title()
    items = "".join(
        f"""<div style="display:flex;align-items:center;margin-bottom:6px;">
                <span style="width:10px;height:10px;border-radius:50%;background:{color};
                             margin-right:8px;"></span>
                <span style="font-size:12px;color:{INK_SOFT};">{label}</span>
            </div>"""
        for label, color in color_map.items()
    )
    return f"""
    <div style="position:fixed;bottom:24px;left:24px;z-index:1000;background:#FFFFFF;
                padding:12px 14px;border:1px solid {BORDER};border-radius:10px;
                box-shadow:0 4px 16px rgba(15,23,42,0.08);font-family:Inter,sans-serif;">
        <div style="font-size:11px;font-weight:600;color:{MUTED};text-transform:uppercase;
                    letter-spacing:.04em;margin-bottom:8px;">{title}</div>
        {items}
    </div>
    """


def create_heatmap(
    df: pd.DataFrame,
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    weight_col: Optional[str] = None,
    zoom_start: int = 6,
    center: Optional[List[float]] = None,
) -> folium.Map:
    """Concentration heatmap on the same light basemap."""
    if center is None:
        center = [df[lat_col].mean(), df[lon_col].mean()] if len(df) else [5.15, 46.2]

    m = folium.Map(location=center, zoom_start=zoom_start, tiles="CartoDB positron")

    if weight_col and weight_col in df.columns:
        heat_data = df[[lat_col, lon_col, weight_col]].values.tolist()
    else:
        heat_data = df[[lat_col, lon_col]].values.tolist()

    HeatMap(
        heat_data,
        min_opacity=0.35,
        radius=24,
        blur=18,
        gradient={0.3: "#C7D2FE", 0.55: "#818CF8", 0.8: "#4F46E5", 1.0: "#3730A3"},
    ).add_to(m)

    return m
