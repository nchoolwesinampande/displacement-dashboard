"""
Indicator Cards Component
Renders styled KPI metric cards for dashboard display.
"""

import streamlit as st
from typing import Optional, Union, List, Dict
import pandas as pd


def render_kpi_card(
    title: str,
    value: Union[int, float, str],
    delta: Optional[Union[int, float]] = None,
    delta_description: str = "vs. previous period",
    icon: str = "",
    color: str = "#3498DB",
    format_value: bool = True
) -> None:
    """
    Render a styled KPI metric card.
    
    Args:
        title: Card title/label
        value: Main metric value
        delta: Change from previous period (positive or negative)
        delta_description: Description text for the delta
        icon: Emoji or icon to display
        color: Accent color for the card
        format_value: Whether to format large numbers with commas
    """
    
    # Format the value
    if format_value and isinstance(value, (int, float)):
        if isinstance(value, float) and value < 1:
            formatted_value = f"{value:.1%}"
        elif value >= 1000000:
            formatted_value = f"{value/1000000:.1f}M"
        elif value >= 1000:
            formatted_value = f"{value/1000:.1f}K"
        else:
            formatted_value = f"{value:,.0f}"
    else:
        formatted_value = str(value)
    
    # Determine delta styling
    if delta is not None:
        if delta > 0:
            delta_color = "#27AE60"
            delta_icon = "↑"
            delta_text = f"+{delta:,.0f}" if isinstance(delta, (int, float)) else f"+{delta}"
        elif delta < 0:
            delta_color = "#E74C3C"
            delta_icon = "↓"
            delta_text = f"{delta:,.0f}" if isinstance(delta, (int, float)) else str(delta)
        else:
            delta_color = "#7F8C8D"
            delta_icon = "→"
            delta_text = "0"
        
        delta_html = f"""
            <div style="display: flex; align-items: center; margin-top: 8px;">
                <span style="color: {delta_color}; font-size: 14px; font-weight: 600;">
                    {delta_icon} {delta_text}
                </span>
                <span style="color: #95A5A6; font-size: 12px; margin-left: 8px;">
                    {delta_description}
                </span>
            </div>
        """
    else:
        delta_html = ""
    
    # Render the card - simple structure without icons
    card_html = f"""<div style="background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid {color}; height: 100%;"><p style="color: #7F8C8D; font-size: 14px; margin: 0 0 8px 0; font-weight: 500;">{title}</p><h2 style="color: #2C3E50; font-size: 32px; margin: 0; font-weight: 700;">{formatted_value}</h2></div>"""
    
    st.markdown(card_html, unsafe_allow_html=True)


def render_kpi_row(kpis: List[Dict]) -> None:
    """
    Render a row of KPI cards.
    
    Args:
        kpis: List of dictionaries with KPI parameters
              Each dict should have: title, value, and optionally delta, icon, color
    """
    
    cols = st.columns(len(kpis))
    
    for col, kpi in zip(cols, kpis):
        with col:
            render_kpi_card(
                title=kpi.get('title', 'Metric'),
                value=kpi.get('value', 0),
                delta=kpi.get('delta'),
                delta_description=kpi.get('delta_description', 'vs. previous period'),
                icon=kpi.get('icon', ''),
                color=kpi.get('color', '#3498DB'),
                format_value=kpi.get('format_value', True)
            )


def render_progress_indicator(
    title: str,
    current: Union[int, float],
    target: Union[int, float],
    color: str = "#3498DB",
    show_percentage: bool = True
) -> None:
    """
    Render a progress bar indicator.
    
    Args:
        title: Indicator title
        current: Current value
        target: Target value
        color: Progress bar color
        show_percentage: Whether to show percentage
    """
    
    percentage = min((current / target) * 100, 100) if target > 0 else 0
    
    progress_html = f"""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="color: #2C3E50; font-size: 14px; font-weight: 500;">{title}</span>
            <span style="color: #7F8C8D; font-size: 14px;">
                {current:,.0f} / {target:,.0f}
                {f' ({percentage:.1f}%)' if show_percentage else ''}
            </span>
        </div>
        <div style="
            background-color: #ECF0F1;
            border-radius: 10px;
            height: 12px;
            overflow: hidden;
        ">
            <div style="
                background: linear-gradient(90deg, {color} 0%, {color}dd 100%);
                width: {percentage}%;
                height: 100%;
                border-radius: 10px;
                transition: width 0.5s ease-in-out;
            "></div>
        </div>
    </div>
    """
    
    st.markdown(progress_html, unsafe_allow_html=True)


def render_indicator_grid(
    df: pd.DataFrame,
    indicators: List[Dict]
) -> None:
    """
    Render a grid of OECD-DAC aligned indicators.
    
    Args:
        df: Filtered DataFrame
        indicators: List of indicator configurations
    """
    
    st.markdown("""
    <h4 style="color: #2C3E50; margin-bottom: 20px;">
        📈 Programme Indicators (OECD-DAC Aligned)
    </h4>
    """, unsafe_allow_html=True)
    
    for indicator in indicators:
        if indicator['type'] == 'count':
            current = len(df[df[indicator['column']] == indicator['value']]) if 'value' in indicator else len(df)
        elif indicator['type'] == 'percentage':
            if 'condition' in indicator:
                current = len(df[df[indicator['column']] == indicator['condition']]) / len(df) * indicator.get('target', 100) if len(df) > 0 else 0
            else:
                current = len(df) / indicator.get('target', 100) * 100
        elif indicator['type'] == 'sum':
            current = df[indicator['column']].sum()
        else:
            current = len(df)
        
        render_progress_indicator(
            title=indicator['title'],
            current=current,
            target=indicator['target'],
            color=indicator.get('color', '#3498DB'),
            show_percentage=indicator.get('show_percentage', True)
        )


def render_stat_card(
    label: str,
    value: Union[int, float, str],
    sublabel: Optional[str] = None,
    color: str = "#3498DB"
) -> None:
    """
    Render a simple stat card for inline statistics.
    
    Args:
        label: Stat label
        value: Stat value
        sublabel: Optional sublabel/description
        color: Accent color
    """
    
    sublabel_html = f'<p style="color: #95A5A6; font-size: 11px; margin: 4px 0 0 0;">{sublabel}</p>' if sublabel else ""
    
    card_html = f"""
    <div style="
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px 16px;
        text-align: center;
        border-top: 3px solid {color};
    ">
        <p style="color: #7F8C8D; font-size: 12px; margin: 0 0 4px 0;">{label}</p>
        <p style="color: #2C3E50; font-size: 20px; font-weight: 700; margin: 0;">
            {value if isinstance(value, str) else f'{value:,.0f}'}
        </p>
        {sublabel_html}
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
