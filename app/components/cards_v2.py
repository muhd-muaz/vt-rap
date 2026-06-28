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


def render_filter_panel_heading(title: str, subtitle: str) -> None:
    """Render a compact V2 heading for page-level filters."""
    safe_title = html.escape(str(title))
    safe_subtitle = html.escape(str(subtitle))

    st.markdown(
        f"""
        <div class="v2-filter-panel-heading">
            <div class="v2-filter-panel-title">{safe_title}</div>
            <div class="v2-filter-panel-subtitle">{safe_subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_detail_panel(
    title: str,
    eyebrow: str,
    items: list[tuple[str, str, str]],
    score_label: str | None = None,
    score_value: str | None = None,
) -> None:
    """Render a reusable escaped V2 detail panel."""
    safe_title = html.escape(str(title))
    safe_eyebrow = html.escape(str(eyebrow))

    score_markup = ""
    if score_label is not None and score_value is not None:
        safe_score_label = html.escape(str(score_label))
        safe_score_value = html.escape(str(score_value))
        score_markup = f"""
                <div class="v2-detail-score">
                    <span>{safe_score_label}</span>
                    <strong>{safe_score_value}</strong>
                </div>
        """

    item_markup = "\n".join(
        f"""
                <div>
                    <span>{html.escape(str(label))}</span>
                    <strong>{html.escape(str(value))}</strong>
                    <p>{html.escape(str(caption))}</p>
                </div>
        """
        for label, value, caption in items
    )

    st.markdown(
        f"""
        <div class="v2-detail-panel">
            <div class="v2-detail-heading">
                <div>
                    <div class="v2-eyebrow">{safe_eyebrow}</div>
                    <div class="v2-detail-title">{safe_title}</div>
                </div>
                {score_markup}
            </div>
            <div class="v2-detail-grid">
                {item_markup}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
