from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from components.cards import get_summary_value


def render_metric_card(
    title: str,
    value: str,
    caption: str,
    accent: str = "default",
) -> None:
    """Render redesigned metric card."""
    safe_title = html.escape(str(title))
    safe_value = html.escape(str(value))
    safe_caption = html.escape(str(caption))

    st.markdown(
        f"""
        <div class="v2-metric-card accent-{accent}">
            <div class="v2-metric-topline"></div>
            <div class="v2-metric-content">
                <div class="v2-metric-label">{safe_title}</div>
                <div class="v2-metric-value">{safe_value}</div>
                <div class="v2-metric-caption">{safe_caption}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_metric_card(
    executive_summary: pd.DataFrame,
    title: str,
    metric_name: str,
    caption: str,
    suffix: str = "",
    accent: str = "default",
) -> None:
    """Render redesigned summary metric card from executive summary."""
    value = get_summary_value(executive_summary, metric_name)

    if suffix and value != "-":
        value = f"{value}{suffix}"

    render_metric_card(
        title=title,
        value=value,
        caption=caption,
        accent=accent,
    )


def render_chart_card(title: str, subtitle: str, chart_key: str, figure) -> None:
    """Render a Plotly chart inside a V2 card surface."""
    safe_title = html.escape(str(title))
    safe_subtitle = html.escape(str(subtitle))

    st.markdown(
        f"""
        <div class="v2-card-heading">
            <div>
                <div class="v2-card-title">{safe_title}</div>
                <div class="v2-card-subtitle">{safe_subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
        key=chart_key,
    )
