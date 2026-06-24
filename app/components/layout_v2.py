from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class PageDefinition:
    """Dashboard page metadata."""

    key: str
    label: str
    description: str


PAGES = [
    PageDefinition(
        key="Executive Overview",
        label="Executive",
        description="Management-level reliability overview.",
    ),
    PageDefinition(
        key="Equipment Risk",
        label="Equipment Risk",
        description="Equipment-level callback and mantrap risk.",
    ),
    PageDefinition(
        key="Account Risk",
        label="Account Risk",
        description="Account-level reliability exposure.",
    ),
    PageDefinition(
        key="Fault Analysis",
        label="Fault Intelligence",
        description="Fault family and actual fault-code intelligence.",
    ),
    PageDefinition(
        key="Emerging Alerts",
        label="Emerging Alerts",
        description="Low-history equipment with early warning signals.",
    ),
    PageDefinition(
        key="Data Quality",
        label="Data Quality",
        description="Validation, completeness, and trust indicators.",
    ),
]


def render_sidebar_brand() -> None:
    """Render V2 sidebar brand block."""
    st.sidebar.markdown(
        """
        <div class="v2-sidebar-brand">
            <div class="v2-brand-mark">VT</div>
            <div>
                <div class="v2-brand-title">VT-RAP</div>
                <div class="v2-brand-subtitle">Reliability Command Center</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_status(validation_status: str, last_refresh: str) -> None:
    """Render sidebar pipeline status."""
    status_class = "passed" if validation_status.lower() == "passed" else "review"

    st.sidebar.markdown(
        f"""
        <div class="v2-sidebar-status-card">
            <div class="v2-sidebar-section-label">Pipeline</div>
            <div class="v2-status-row">
                <span class="v2-status-dot {status_class}"></span>
                <span>{validation_status}</span>
            </div>
            <div class="v2-sidebar-muted">Last refresh</div>
            <div class="v2-sidebar-strong">{last_refresh}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_navigation(default_page: str = "Executive Overview") -> str:
    """Render V2 sidebar navigation."""
    render_sidebar_brand()

    st.sidebar.markdown(
        '<div class="v2-sidebar-section-label">Navigation</div>',
        unsafe_allow_html=True,
    )

    page_labels = [page.label for page in PAGES]
    label_to_key = {page.label: page.key for page in PAGES}
    key_to_label = {page.key: page.label for page in PAGES}

    selected_label = st.sidebar.radio(
        label="",
        options=page_labels,
        index=page_labels.index(key_to_label.get(default_page, "Executive")),
        label_visibility="collapsed",
    )

    return label_to_key[selected_label]


def render_page_header(
    title: str,
    description: str,
    period_label: str,
    validation_status: str,
) -> None:
    """Render V2 page header."""
    status_class = "passed" if validation_status.lower() == "passed" else "review"

    st.markdown(
        f"""
        <div class="v2-page-header">
            <div>
                <div class="v2-eyebrow">VT-RAP Command Center</div>
                <h1>{title}</h1>
                <p>{description}</p>
            </div>
            <div class="v2-header-badges">
                <div class="v2-badge">Period: {period_label}</div>
                <div class="v2-badge">
                    <span class="v2-status-dot {status_class}"></span>
                    {validation_status}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, subtitle: str) -> None:
    """Render V2 section heading."""
    st.markdown(
        f"""
        <div class="v2-section-header">
            <div class="v2-section-title">{title}</div>
            <div class="v2-section-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
