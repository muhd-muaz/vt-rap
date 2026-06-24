from __future__ import annotations

from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
THEME_CSS_PATH = PROJECT_ROOT / "app" / "styles" / "theme_v2.css"


def load_theme_v2() -> None:
    """Load the redesigned VT-RAP app theme."""
    if not THEME_CSS_PATH.exists():
        st.warning(f"Theme file not found: {THEME_CSS_PATH}")
        return

    css = THEME_CSS_PATH.read_text(encoding="utf-8")

    st.markdown(
        f"""
        <style>
        {css}
        </style>
        """,
        unsafe_allow_html=True,
    )
