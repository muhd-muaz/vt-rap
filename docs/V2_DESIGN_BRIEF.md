# VT-RAP V2 Design Brief

## Product
VT-RAP is an internal reliability analytics command center for elevator callback, mantrap, fault, equipment risk, and account risk analysis.

## Design goal
Create a premium dark enterprise dashboard with a calm Apple/macOS-inspired command-center feel.

## Audience
Management, system department staff, and supervisors reviewing operational reliability.

## Do
- Make the dashboard feel expensive, serious, and clean.
- Use dark graphite surfaces, subtle borders, and controlled blue accents.
- Prioritize readability over decoration.
- Use clear KPI hierarchy.
- Make tables easy to scan.
- Keep filters visible and obvious.
- Redesign one page at a time.

## Do not
- Do not make it look cyberpunk or gamer-like.
- Do not use random gradients everywhere.
- Do not over-animate.
- Do not hide important filters.
- Do not break Streamlit functionality.
- Do not modify backend analytics logic during UI redesign.

## Current visual problems
- Sidebar is too large and heavy.
- Main page spacing is acceptable but not polished.
- KPI cards look generic.
- Chart cards lack visual confidence.
- Old pages still look inconsistent with Executive V2.
- Streamlit default widgets are still visually obvious.

## Desired visual direction
- Native dark-mode minimalism.
- macOS/iPadOS-style glass surfaces.
- Better spacing rhythm.
- More refined cards.
- Less clutter.
- Stronger page-level composition.
- Serious internal command center, not marketing website.

## Technical constraints
- Streamlit app.
- Stable dashboard app/streamlit_app.py must not be broken.
- V2 dashboard app/streamlit_app_v2.py is experimental.
- Use CSS and reusable Streamlit components.
- Preserve all existing data and dashboard logic.