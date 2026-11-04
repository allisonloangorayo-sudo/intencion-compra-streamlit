"""Estilos de la interfaz: diseño minimalista, tipografía Inter y tarjetas suaves."""

INK = "#1d1d1f"
MUTED = "#6e6e73"
LINE = "#e5e5ea"
SURFACE = "#f5f5f7"
BLUE = "#0071e3"
GREEN = "#248a3d"
GREEN_SOFT = "#34c759"
RED = "#d70015"
RED_SOFT = "#ff3b30"
AMBER = "#ff9f0a"
GRAY = "#c7c7cc"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stMarkdown, .stText, button, input, textarea, select {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}}
.block-container {{
    max-width: 1180px;
    padding-top: 4.2rem;
    padding-bottom: 4rem;
}}
#MainMenu, footer {{ visibility: hidden; }}
h1, h2, h3 {{ color: {INK}; letter-spacing: -0.02em; }}
h3 {{ font-weight: 600; font-size: 1.25rem; margin-top: .4rem; }}
.stMarkdown p, .stMarkdown li {{ color: {INK}; line-height: 1.6; }}
[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"] p,
.stButton button[kind="primary"] p {{ color: #fff !important; font-weight: 600; }}
.subhead {{
    font-size: 1.15rem; font-weight: 600; letter-spacing: -0.015em; color: {INK};
    margin: 1.4rem 0 .5rem 0;
}}

/* Encabezado */
.hero-eyebrow {{
    font-size: .8rem; font-weight: 600; letter-spacing: .08em; text-transform: uppercase;
    color: {BLUE}; margin-bottom: .35rem;
}}
.hero-title {{
    font-size: 2.6rem; font-weight: 700; line-height: 1.1; letter-spacing: -0.035em;
    color: {INK}; margin: 0 0 .6rem 0;
}}
.hero-sub {{ font-size: 1.12rem; color: {MUTED}; max-width: 760px; margin-bottom: 1.4rem; }}

/* Pestañas */
.stTabs [data-baseweb="tab-list"] {{
    gap: .25rem; border-bottom: 1px solid {LINE};
}}
.stTabs [data-baseweb="tab"] {{
    font-weight: 500; font-size: .98rem; padding: .6rem 1rem; color: {MUTED};
}}
.stTabs [aria-selected="true"] {{ color: {INK}; }}

/* Tarjetas */
.card {{
    background: {SURFACE}; border-radius: 18px; padding: 1.25rem 1.4rem; height: 100%;
    min-height: 150px;
}}
.card-white {{
    background: #fff; border: 1px solid {LINE}; border-radius: 18px; padding: 1.25rem 1.4rem;
}}
.kpi-label {{ font-size: .82rem; color: {MUTED}; margin-bottom: .2rem; }}
.kpi-value {{ font-size: 1.9rem; font-weight: 700; letter-spacing: -0.03em; color: {INK}; }}
.kpi-note {{ font-size: .82rem; color: {MUTED}; margin-top: .2rem; line-height: 1.4; }}

.section-title {{
    font-size: 1.55rem; font-weight: 700; letter-spacing: -0.025em; color: {INK};
    margin: 2.2rem 0 .3rem 0;
}}
.section-sub {{ color: {MUTED}; font-size: 1rem; margin-bottom: 1rem; max-width: 820px; }}

.explain {{
    font-size: .92rem; color: {MUTED}; line-height: 1.55; margin-top: .2rem;
}}
.explain b {{ color: {INK}; font-weight: 600; }}

/* Resultado */
.result-label {{ font-size: .85rem; color: {MUTED}; text-align: center; margin-top: -.4rem; }}
.pill {{
    display: inline-block; padding: .3rem .8rem; border-radius: 999px; font-weight: 600;
    font-size: .9rem;
}}
.pill-yes {{ background: #e8f7ec; color: {GREEN}; }}
.pill-no  {{ background: #f2f2f7; color: {MUTED}; }}
.pill-mid {{ background: #fff4e5; color: #b25000; }}

.empty-state {{
    border: 1.5px dashed {LINE}; border-radius: 18px; padding: 2.6rem 1.5rem;
    text-align: center; color: {MUTED};
}}

/* Pasos del pipeline */
.flow {{ display: flex; flex-wrap: wrap; align-items: center; gap: .45rem; margin: .6rem 0 1rem; }}
.flow-step {{
    background: {SURFACE}; border-radius: 12px; padding: .55rem .85rem; font-size: .88rem;
    font-weight: 500; color: {INK};
}}
.flow-step small {{ display: block; color: {MUTED}; font-weight: 400; font-size: .76rem; }}
.flow-arrow {{ color: {GRAY}; font-size: 1.1rem; }}

/* Formulario */
[data-testid="stForm"] {{
    border: 1px solid {LINE}; border-radius: 18px; padding: 1.1rem 1.3rem;
}}
.form-group {{
    font-size: .78rem; font-weight: 600; letter-spacing: .06em; text-transform: uppercase;
    color: {MUTED}; margin: .4rem 0 .2rem;
}}
.stButton > button, [data-testid="stFormSubmitButton"] > button {{
    border-radius: 999px; font-weight: 600; padding: .55rem 1.2rem;
}}
[data-testid="stExpander"] {{ border: 1px solid {LINE}; border-radius: 14px; }}

/* Diccionario de variables */
table.dict {{ width: 100%; border-collapse: collapse; font-size: .9rem; }}
table.dict th {{
    text-align: left; font-weight: 600; color: {MUTED}; font-size: .78rem; letter-spacing: .04em;
    text-transform: uppercase; padding: .6rem .7rem; border-bottom: 1px solid {LINE};
}}
table.dict td {{ padding: .6rem .7rem; border-bottom: 1px solid {LINE}; vertical-align: top; color: {INK}; }}
table.dict code {{ background: {SURFACE}; color: {INK}; padding: .1rem .35rem; border-radius: 6px; font-size: .82rem; }}
.tag {{ display: inline-block; padding: .12rem .55rem; border-radius: 999px; font-size: .78rem; font-weight: 600; }}
.tag-yes {{ background: #e8f2fd; color: {BLUE}; }}
.tag-no {{ background: #f2f2f7; color: {MUTED}; }}
.tag-target {{ background: #e8f7ec; color: {GREEN}; }}
@media (max-width: 640px) {{ table.dict th:nth-child(3), table.dict td:nth-child(3) {{ display: none; }} }}

.footer {{
    margin-top: 3rem; padding-top: 1.2rem; border-top: 1px solid {LINE};
    color: {MUTED}; font-size: .85rem;
}}
.footer a {{ color: {BLUE}; text-decoration: none; }}

@media (max-width: 640px) {{
    .hero-title {{ font-size: 1.9rem; }}
    .kpi-value {{ font-size: 1.5rem; }}
}}
</style>
"""
