from __future__ import annotations

import streamlit as st


def render_section_header(title: str, subtitle: str) -> None:
    """Render a reusable dashboard section header."""
    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-title">{title}</div>
            <div class="section-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
