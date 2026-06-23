from __future__ import annotations

import streamlit as st


DARK_THEME = {
    "mode": "Dark",
    "background": "#070A12",
    "panel": "#0D111C",
    "card": "#121826",
    "elevated_card": "#182033",
    "text": "#F5F7FA",
    "text_secondary": "#B6BDCB",
    "text_muted": "#7D8597",
    "border": "rgba(255, 255, 255, 0.08)",
    "accent": "#2DD4BF",
    "accent_blue": "#60A5FA",
    "critical": "#FB7185",
    "high": "#FDBA74",
    "medium": "#FDE68A",
    "low": "#86EFAC",
    "shadow": "0 22px 60px rgba(0, 0, 0, 0.32)",
    "chart_template": "plotly_dark",
}


def get_theme() -> dict[str, str]:
    """Return the permanent dark dashboard theme."""
    return DARK_THEME


def inject_theme_css(theme: dict[str, str]) -> None:
    """Inject active theme CSS variables."""
    st.markdown(
        f"""
        <style>
        :root {{
            --background-main: {theme["background"]};
            --background-panel: {theme["panel"]};
            --background-card: {theme["card"]};
            --background-elevated-card: {theme["elevated_card"]};
            --border-soft: {theme["border"]};
            --text-main: {theme["text"]};
            --text-secondary: {theme["text_secondary"]};
            --text-muted: {theme["text_muted"]};
            --accent-primary: {theme["accent"]};
            --accent-blue: {theme["accent_blue"]};
            --risk-critical: {theme["critical"]};
            --risk-high: {theme["high"]};
            --risk-medium: {theme["medium"]};
            --risk-low: {theme["low"]};
            --shadow-card: {theme["shadow"]};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )