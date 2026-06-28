from __future__ import annotations

import html

import streamlit as st


def render_section_header(title: str, subtitle: str) -> None:
    """Render a reusable dashboard section header."""
    safe_title = html.escape(str(title))
    safe_subtitle = html.escape(str(subtitle))

    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-title">{safe_title}</div>
            <div class="section-subtitle">{safe_subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
