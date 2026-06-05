"""
Indicator cards and target bars.

Flat, minimal metric cards (label / big number / optional caption) and thin
progress bars for tracking against programme targets.
"""

import streamlit as st
from typing import List, Dict, Optional, Union

from utils.theme import INK, INK_SOFT, MUTED, BORDER, PRIMARY


def _fmt(value: Union[int, float]) -> str:
    """Compact number formatting (1,234 / 12.3K / 1.2M)."""
    if isinstance(value, float) and not value.is_integer() and abs(value) < 1000:
        return f"{value:,.1f}"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs(value) >= 10_000:
        return f"{value / 1000:.1f}K"
    return f"{value:,.0f}"


def render_metric(label: str, value: Union[int, float, str], caption: str = "",
                  accent: str = PRIMARY, value_suffix: str = "") -> None:
    """Render a single flat metric card."""
    display = value if isinstance(value, str) else _fmt(value)
    caption_html = (
        f'<div style="color:{MUTED};font-size:12px;margin-top:6px;">{caption}</div>'
        if caption else ""
    )
    st.markdown(
        f"""
        <div style="background:#FFFFFF;border:1px solid {BORDER};border-radius:14px;
                    padding:18px 20px;height:100%;">
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="width:8px;height:8px;border-radius:50%;background:{accent};
                             display:inline-block;"></span>
                <span style="color:{INK_SOFT};font-size:12.5px;font-weight:500;
                             letter-spacing:.02em;">{label}</span>
            </div>
            <div style="color:{INK};font-size:30px;font-weight:700;margin-top:10px;
                        line-height:1;">{display}<span style="font-size:16px;
                        font-weight:600;color:{MUTED};">{value_suffix}</span></div>
            {caption_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_row(metrics: List[Dict]) -> None:
    """Render a row of flat metric cards."""
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            render_metric(
                label=m.get("label", ""),
                value=m.get("value", 0),
                caption=m.get("caption", ""),
                accent=m.get("accent", PRIMARY),
                value_suffix=m.get("value_suffix", ""),
            )


def render_target_bar(label: str, current: Union[int, float],
                      target: Union[int, float], accent: str = PRIMARY,
                      unit: str = "") -> None:
    """Thin progress bar showing current vs a programme target."""
    target = max(target, 1)
    pct = min(current / target * 100, 100)
    cur_txt = f"{current:,.0f}{unit}" if not isinstance(current, str) else current
    tgt_txt = f"{target:,.0f}{unit}"

    st.markdown(
        f"""
        <div style="margin-bottom:18px;">
            <div style="display:flex;justify-content:space-between;align-items:baseline;
                        margin-bottom:7px;">
                <span style="color:{INK};font-size:13.5px;font-weight:500;">{label}</span>
                <span style="color:{MUTED};font-size:12.5px;">
                    {cur_txt} <span style="color:{BORDER};">/</span> {tgt_txt}
                    &nbsp;<span style="color:{INK_SOFT};font-weight:600;">{pct:.0f}%</span>
                </span>
            </div>
            <div style="background:#F1F5F9;border-radius:999px;height:7px;overflow:hidden;">
                <div style="width:{pct}%;height:100%;border-radius:999px;background:{accent};"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
