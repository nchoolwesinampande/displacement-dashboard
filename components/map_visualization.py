"""
Map Visualization Component
Creates interactive cluster maps for geographic visualization of beneficiary data.
"""

import folium
from folium.plugins import MarkerCluster
import pandas as pd
from typing import Optional, Dict, List


# Color mapping for solutions pathways
PATHWAY_COLORS = {
    'Return': '#9B59B6',           # Purple
    'Local Integration': '#F39C12', # Orange
    'Relocation': '#1ABC9C',        # Teal
}

# Color mapping for displacement status
STATUS_COLORS = {
    'IDP': '#E74C3C',              # Red
    'Returnee': '#3498DB',          # Blue
    'Host Community': '#2ECC71',    # Green
}

# Color mapping for pathway stages
STAGE_COLORS = {
    'Assessment': '#BDC3C7',       # Light Gray
    'Planning': '#F39C12',          # Orange
    'Implementation': '#3498DB',    # Blue
    'Achieved': '#27AE60',          # Green
}


def create_cluster_map(
    df: pd.DataFrame,
    lat_col: str = 'latitude',
    lon_col: str = 'longitude',
    color_by: str = 'solutions_pathway',
    zoom_start: int = 6,
    center: Optional[List[float]] = None
) -> folium.Map:
    """
    Create an interactive cluster map with colored markers.
    
    Args:
        df: DataFrame with beneficiary data
        lat_col: Column name for latitude
        lon_col: Column name for longitude
        color_by: Column to use for marker coloring ('solutions_pathway', 'displacement_status', 'pathway_stage')
        zoom_start: Initial zoom level
        center: Map center coordinates [lat, lon]. If None, calculated from data.
        
    Returns:
        Folium Map object
    """
    
    # Calculate center if not provided
    if center is None:
        center = [df[lat_col].mean(), df[lon_col].mean()]
    
    # Select color mapping based on color_by parameter
    if color_by == 'solutions_pathway':
        color_map = PATHWAY_COLORS
    elif color_by == 'displacement_status':
        color_map = STATUS_COLORS
    elif color_by == 'pathway_stage':
        color_map = STAGE_COLORS
    else:
        color_map = PATHWAY_COLORS
    
    # Create base map
    m = folium.Map(
        location=center,
        zoom_start=zoom_start,
        tiles='CartoDB positron',
        control_scale=True
    )
    
    # Create marker cluster
    marker_cluster = MarkerCluster(
        name='Beneficiaries',
        overlay=True,
        control=True,
        options={
            'spiderfyOnMaxZoom': True,
            'showCoverageOnHover': True,
            'zoomToBoundsOnClick': True,
            'maxClusterRadius': 50
        }
    )
    
    # Add markers for each beneficiary
    for _, row in df.iterrows():
        # Get marker color
        color_value = row.get(color_by, 'Unknown')
        marker_color = color_map.get(color_value, '#7F8C8D')
        
        # Create popup content
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 200px;">
            <h4 style="margin: 0 0 10px 0; color: #2C3E50; border-bottom: 2px solid {marker_color}; padding-bottom: 5px;">
                {row.get('beneficiary_id', 'N/A')}
            </h4>
            <table style="width: 100%; font-size: 12px;">
                <tr>
                    <td style="color: #7F8C8D; padding: 2px 0;">Region:</td>
                    <td style="text-align: right; font-weight: bold;">{row.get('region', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="color: #7F8C8D; padding: 2px 0;">District:</td>
                    <td style="text-align: right; font-weight: bold;">{row.get('district', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="color: #7F8C8D; padding: 2px 0;">Status:</td>
                    <td style="text-align: right; font-weight: bold;">{row.get('displacement_status', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="color: #7F8C8D; padding: 2px 0;">Pathway:</td>
                    <td style="text-align: right; font-weight: bold;">{row.get('solutions_pathway', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="color: #7F8C8D; padding: 2px 0;">Stage:</td>
                    <td style="text-align: right; font-weight: bold;">{row.get('pathway_stage', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="color: #7F8C8D; padding: 2px 0;">HH Size:</td>
                    <td style="text-align: right; font-weight: bold;">{row.get('household_size', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="color: #7F8C8D; padding: 2px 0;">HoH Gender:</td>
                    <td style="text-align: right; font-weight: bold;">{row.get('gender_hoh', 'N/A')}</td>
                </tr>
            </table>
        </div>
        """
        
        # Create marker
        folium.CircleMarker(
            location=[row[lat_col], row[lon_col]],
            radius=8,
            popup=folium.Popup(popup_html, max_width=250),
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.7,
            weight=2
        ).add_to(marker_cluster)
    
    # Add marker cluster to map
    marker_cluster.add_to(m)
    
    # Add legend
    legend_html = create_legend_html(color_by, color_map)
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m


def create_legend_html(title: str, color_map: Dict[str, str]) -> str:
    """
    Create HTML for map legend.
    
    Args:
        title: Legend title
        color_map: Dictionary mapping categories to colors
        
    Returns:
        HTML string for legend
    """
    
    # Format title
    display_title = title.replace('_', ' ').title()
    
    legend_items = ""
    for label, color in color_map.items():
        legend_items += f"""
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="width: 16px; height: 16px; background-color: {color}; 
                            border-radius: 50%; margin-right: 8px; border: 2px solid white;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.2);"></div>
                <span style="font-size: 12px; color: #2C3E50;">{label}</span>
            </div>
        """
    
    legend_html = f"""
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000; 
                background-color: white; padding: 15px 20px; border-radius: 8px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.2); font-family: Arial, sans-serif;">
        <h4 style="margin: 0 0 10px 0; color: #2C3E50; font-size: 14px; 
                   border-bottom: 1px solid #eee; padding-bottom: 8px;">
            {display_title}
        </h4>
        {legend_items}
    </div>
    """
    
    return legend_html


def create_heatmap(
    df: pd.DataFrame,
    lat_col: str = 'latitude',
    lon_col: str = 'longitude',
    weight_col: Optional[str] = None,
    zoom_start: int = 6,
    center: Optional[List[float]] = None
) -> folium.Map:
    """
    Create a heatmap showing concentration of beneficiaries.
    
    Args:
        df: DataFrame with beneficiary data
        lat_col: Column name for latitude
        lon_col: Column name for longitude
        weight_col: Optional column for weighting (e.g., household_size)
        zoom_start: Initial zoom level
        center: Map center coordinates
        
    Returns:
        Folium Map object with heatmap layer
    """
    from folium.plugins import HeatMap
    
    if center is None:
        center = [df[lat_col].mean(), df[lon_col].mean()]
    
    m = folium.Map(
        location=center,
        zoom_start=zoom_start,
        tiles='CartoDB dark_matter'
    )
    
    # Prepare heat data
    if weight_col and weight_col in df.columns:
        heat_data = df[[lat_col, lon_col, weight_col]].values.tolist()
    else:
        heat_data = df[[lat_col, lon_col]].values.tolist()
    
    # Add heatmap layer
    HeatMap(
        heat_data,
        min_opacity=0.4,
        max_zoom=12,
        radius=25,
        blur=15,
        gradient={0.4: 'blue', 0.65: 'lime', 0.8: 'orange', 1: 'red'}
    ).add_to(m)
    
    return m


def create_choropleth_by_region(
    df: pd.DataFrame,
    geojson_path: Optional[str] = None,
    region_col: str = 'region',
    value_col: str = 'beneficiary_id',
    aggregation: str = 'count'
) -> folium.Map:
    """
    Create a choropleth map showing aggregated values by region.
    Note: Requires GeoJSON file with region boundaries.
    
    Args:
        df: DataFrame with beneficiary data
        geojson_path: Path to GeoJSON file with region boundaries
        region_col: Column name for region
        value_col: Column to aggregate
        aggregation: Aggregation method ('count', 'sum', 'mean')
        
    Returns:
        Folium Map object with choropleth layer
    """
    
    # Aggregate data by region
    if aggregation == 'count':
        region_data = df.groupby(region_col).size().reset_index(name='value')
    elif aggregation == 'sum':
        region_data = df.groupby(region_col)[value_col].sum().reset_index(name='value')
    elif aggregation == 'mean':
        region_data = df.groupby(region_col)[value_col].mean().reset_index(name='value')
    
    # Create base map centered on Somalia
    m = folium.Map(
        location=[5.1521, 46.1996],
        zoom_start=6,
        tiles='CartoDB positron'
    )
    
    # If no GeoJSON, create simple markers for each region
    if geojson_path is None:
        # Calculate region centers from data
        region_centers = df.groupby(region_col).agg({
            'latitude': 'mean',
            'longitude': 'mean'
        }).reset_index()
        
        region_centers = region_centers.merge(region_data, on=region_col)
        
        max_value = region_centers['value'].max()
        
        for _, row in region_centers.iterrows():
            # Scale radius based on value
            radius = 20 + (row['value'] / max_value) * 40
            
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=radius,
                popup=f"{row[region_col]}: {row['value']} beneficiaries",
                color='#3498DB',
                fill=True,
                fill_color='#3498DB',
                fill_opacity=0.6
            ).add_to(m)
    
    return m
