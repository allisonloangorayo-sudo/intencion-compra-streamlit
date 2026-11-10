"""Estilos de la interfaz.

Sistema visual:
- Verde esmeralda = compra, gris pizarra = no compra (en toda la app, gráficas incluidas).
- Rosa = lo que baja la probabilidad, ámbar = zona de duda.
- Bricolage Grotesque para todo el texto; IBM Plex Mono solo dentro del ticket.
"""

INK = "#17202e"
MUTED = "#5b6575"
FAINT = "#8a93a3"
LINE = "#e3e7ee"
CANVAS = "#f3f5f8"
SURFACE = "#ffffff"
FIELD = "#eef1f5"

EMERALD = "#0e7c66"
EMERALD_DEEP = "#0a5c4c"
EMERALD_SOFT = "#d6f1e8"
MINT = "#a9dccb"
SLATE = "#c5ccd6"
SAFFRON = "#e09a0b"
SAFFRON_SOFT = "#fcefd2"
ROSE = "#d4466a"
ROSE_SOFT = "#fbe3e9"
STAGE = "#0d3d34"

FONT = "'Bricolage Grotesque', 'Segoe UI', system-ui, sans-serif"
MONO = "'IBM Plex Mono', ui-monospace, 'SFMono-Regular', Menlo, monospace"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wdth,wght@12..96,75..100,200..800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

/* ---------- Base ---------- */
html, body, .stApp, .stApp * {{ font-family: {FONT} !important; }}
.stApp code, .stApp pre, .stApp pre *, .receipt, .receipt * {{ font-family: {MONO} !important; }}
.receipt .r-title, .receipt .r-total, .receipt .r-verdict, .receipt.empty p, .receipt.empty b {{
    font-family: {FONT} !important;
}}
.stApp [data-testid="stIconMaterial"], .stApp .material-symbols-rounded {{
    font-family: 'Material Symbols Rounded' !important;
}}
.stApp {{ background: {CANVAS}; color: {INK}; --ink: {INK}; }}
header[data-testid="stHeader"] {{ display: none; }}
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"], #MainMenu {{ display: none !important; }}
.block-container {{ max-width: 1240px; padding: 1.1rem 1.75rem 3rem; }}
::selection {{ background: {EMERALD_SOFT}; }}
.stMarkdown p, .stMarkdown li {{ color: {INK}; line-height: 1.6; font-size: 1rem; }}
a {{ color: {EMERALD}; }}
.stApp code {{ color: {INK} !important; background: {FIELD} !important; border-radius: 6px; }}
:focus-visible {{ outline: 2px solid {EMERALD} !important; outline-offset: 2px; }}

/* ---------- Barra superior ---------- */
.topbar {{
    display: flex; justify-content: space-between; align-items: center; padding: .2rem .2rem 1.1rem;
}}
.topbar .brand {{ display: inline-flex; align-items: center; gap: .6rem; font-weight: 700; font-size: 1.02rem; color: {INK}; }}
.topbar .mark {{
    display: grid; place-items: center; width: 32px; height: 32px; border-radius: 9px;
    background: {STAGE}; color: #7fe0c1;
}}
.topbar .mark svg {{ width: 19px; height: 19px; }}
.topbar nav a {{
    font-size: .92rem; font-weight: 600; color: {INK}; text-decoration: none;
    padding: .5rem .95rem; border-radius: 999px; border: 1px solid {LINE}; background: {SURFACE};
}}
.topbar nav a:hover {{ border-color: {INK}; }}

/* ---------- Portada (escenario) ---------- */
.stage {{
    position: relative; overflow: hidden; background: {STAGE}; border-radius: 32px;
    display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: 2rem;
    padding: 3rem 3.4rem 0; min-height: 28rem; margin-bottom: 2.2rem; isolation: isolate;
}}
.stage::before {{
    content: ""; position: absolute; inset: 0; z-index: -1; opacity: .5;
    background-image: radial-gradient(rgba(127, 224, 193, .16) 1px, transparent 1px);
    background-size: 22px 22px;
    mask-image: linear-gradient(115deg, transparent 35%, #000 75%);
}}
.stage-copy {{ padding-bottom: 3rem; align-self: center; }}
.stApp [data-testid="stHeaderActionElements"], .stage h1 a {{ display: none !important; }}
.stage h1 {{
    font-family: {FONT}; font-variation-settings: "opsz" 96, "wdth" 82; font-weight: 720;
    font-size: clamp(2.5rem, 4.9vw, 4.3rem); line-height: .98; letter-spacing: -0.035em;
    color: #f4fbf8; margin: 0 0 1.3rem; padding: 0; max-width: 14ch; text-wrap: balance;
}}
.stage .lead {{ font-size: 1.16rem; line-height: 1.55; color: #b9d8cf; max-width: 32rem; margin: 0 0 1.6rem; }}
.stage .trail {{ width: 100%; max-width: 470px; display: block; margin: 0 0 .9rem; }}
.stage .meta {{ font-size: .9rem; color: #8fbcaf; max-width: 30rem; margin: 0; line-height: 1.5; }}
.stage-art {{ position: relative; align-self: end; display: flex; justify-content: center; }}
.stage-art .receipt-wrap {{ width: 100%; max-width: 360px; margin: 0; }}

/* ---------- Pestañas como control segmentado ---------- */
[role="tablist"] {{
    background: {SURFACE}; border: 1px solid {LINE} !important; border-radius: 999px;
    padding: 5px; gap: 4px; width: fit-content; max-width: 100%; overflow-x: auto;
    box-shadow: none !important;
}}
[data-testid="stTab"] {{
    height: auto; border-radius: 999px; padding: .5rem 1.15rem !important; margin: 0;
    color: {MUTED}; background: transparent; border: none !important;
}}
[data-testid="stTab"] p {{ font-weight: 600; font-size: .95rem !important; color: {MUTED}; white-space: nowrap; }}
[data-testid="stTab"]:hover {{ background: {FIELD}; }}
[data-testid="stTab"]:hover p {{ color: {INK}; }}
[data-testid="stTab"][aria-selected="true"] {{ background: {INK}; }}
[data-testid="stTab"][aria-selected="true"] p {{ color: #fff !important; }}
.react-aria-SelectionIndicator {{ display: none !important; }}
[role="tabpanel"] {{ padding-top: 1.8rem; }}

/* ---------- Tipografía de secciones ---------- */
.section-title {{
    font-variation-settings: "opsz" 72, "wdth" 86; font-weight: 720; font-size: 2.25rem; line-height: 1.05;
    letter-spacing: -0.03em; color: {INK}; margin: 2.6rem 0 .45rem;
}}
.section-title.first {{ margin-top: .2rem; }}
.section-sub {{ color: {MUTED}; font-size: 1.05rem; margin-bottom: 1.2rem; max-width: 46rem; line-height: 1.5; }}
.subhead {{
    font-variation-settings: "opsz" 32; font-weight: 680; font-size: 1.2rem; letter-spacing: -0.015em;
    color: {INK}; margin: 0 0 .35rem; line-height: 1.25;
}}
.explain {{ font-size: .93rem; color: {MUTED}; line-height: 1.55; margin-top: .35rem; max-width: 46rem; }}
.explain b {{ color: {INK}; font-weight: 650; }}
.prose {{ font-size: 1.05rem; line-height: 1.65; color: {INK}; max-width: 46rem; }}

/* ---------- Paneles (contenedores con key="panel_*") ---------- */
[class*="st-key-panel"] {{
    background: {SURFACE}; border: 1px solid {LINE}; border-radius: 22px;
    padding: 1.35rem 1.5rem 1.5rem;
}}
[class*="st-key-panel"] [data-testid="stVerticalBlock"] {{ gap: .55rem; }}
[class*="st-key-panel"] {{ margin-bottom: .9rem; }}

/* ---------- Formulario ---------- */
.st-key-panel_form [data-testid="stForm"] {{ border: none; padding: 0; }}
.form-group {{
    font-weight: 680; font-size: 1rem; color: {INK}; margin: .9rem 0 0;
    padding-top: .9rem; border-top: 1px solid {LINE};
}}
.form-group.first {{ border-top: none; padding-top: 0; margin-top: .2rem; }}
.form-group span {{ display: block; font-weight: 400; font-size: .86rem; color: {MUTED}; margin: .1rem 0 .5rem; }}
[data-testid="stWidgetLabel"] p {{ font-size: .88rem !important; color: {MUTED} !important; font-weight: 500; }}
[data-baseweb="input"], [data-baseweb="select"] > div {{ border-radius: 12px !important; }}
[data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"] {{ display: none !important; }}
[data-testid="stNumberInputContainer"] {{ border-radius: 12px; }}
[data-testid="stNumberInputField"] {{ font-variant-numeric: tabular-nums; font-weight: 600; padding-left: .9rem !important; }}
[data-testid="stSlider"] [data-testid="stSliderThumbValue"] {{ font-weight: 650; font-size: .82rem; }}
[data-testid="stSliderTickBar"] {{ display: none; }}
[data-testid="stFormSubmitButton"] button {{
    background: {EMERALD}; border: none; border-radius: 999px; min-height: 3rem; margin-top: .6rem;
}}
[data-testid="stFormSubmitButton"] button:hover {{ background: {EMERALD_DEEP}; }}
[data-testid="stFormSubmitButton"] button p {{ color: #fff !important; font-weight: 650; font-size: 1rem; }}

/* Casos de ejemplo como fichas */
.st-key-presets [role="radiogroup"] {{ gap: .5rem; flex-wrap: wrap; margin-top: .3rem; }}
.st-key-presets [data-testid="stRadioOption"] {{
    background: {FIELD}; border: 1.5px solid transparent; border-radius: 999px;
    padding: .4rem .95rem; margin: 0; cursor: pointer;
}}
.st-key-presets [data-testid="stRadioOption"] > div > div:first-child {{ display: none; }}
.st-key-presets [data-testid="stRadioOption"] p {{ font-size: .9rem !important; font-weight: 600; color: {INK}; }}
.st-key-presets [data-testid="stRadioOption"]:hover {{ border-color: {SLATE}; }}
.st-key-presets [data-testid="stRadioOption"][data-selected="true"] {{ background: {EMERALD_SOFT}; border-color: {EMERALD}; }}
.st-key-presets [data-testid="stRadioOption"][data-selected="true"] p {{ color: {EMERALD_DEEP}; }}
.st-key-presets [data-testid="stRadioOption"]:has(input:focus-visible) {{ outline: 2px solid {EMERALD}; outline-offset: 2px; }}

/* ---------- Ticket ---------- */
.receipt-wrap {{ filter: drop-shadow(0 18px 30px rgba(23, 32, 46, .13)); margin: 0 .3rem 1.6rem; }}
.receipt-wrap.demo {{
    transform: rotate(3.5deg) translateY(2.4rem); transform-origin: 50% 0;
    filter: drop-shadow(0 30px 40px rgba(0, 0, 0, .35));
}}
.receipt-wrap.demo .receipt {{ animation: none; }}

.receipt {{
    position: relative; background: {SURFACE}; border-radius: 6px 6px 0 0;
    padding: 1.5rem 1.5rem 1.4rem; font-family: {MONO}; font-size: .86rem; color: {INK};
    animation: print .7s cubic-bezier(.2, .8, .2, 1) both;
}}
.receipt::after {{
    content: ""; position: absolute; left: 0; right: 0; bottom: -12px; height: 12px;
    background:
        linear-gradient(135deg, {SURFACE} 50%, transparent 50%) 0 0 / 16px 12px repeat-x,
        linear-gradient(-135deg, {SURFACE} 50%, transparent 50%) 0 0 / 16px 12px repeat-x;
}}
@keyframes print {{
    from {{ clip-path: inset(0 0 100% 0); transform: translateY(-14px); }}
    to   {{ clip-path: inset(0 0 -20px 0); transform: none; }}
}}
@media (prefers-reduced-motion: reduce) {{ .receipt {{ animation: none; }} }}
.receipt .r-head {{ text-align: center; margin-bottom: .9rem; }}
.receipt .r-title {{ font-family: {FONT}; font-weight: 750; font-size: 1.15rem; letter-spacing: -0.01em; }}
.receipt .r-sub {{ color: {MUTED}; font-size: .8rem; margin-top: .15rem; }}
.receipt hr {{ border: none; border-top: 1.5px dashed {SLATE}; margin: .8rem 0; }}
.receipt .r-label {{ color: {MUTED}; font-size: .78rem; margin-bottom: .35rem; }}
.receipt .r-row {{ display: flex; justify-content: space-between; gap: 1rem; padding: .16rem 0; }}
.receipt .r-row span:last-child {{ font-variant-numeric: tabular-nums; white-space: nowrap; }}
.receipt .up {{ color: {EMERALD}; font-weight: 600; }}
.receipt .down {{ color: {ROSE}; font-weight: 600; }}
.receipt .r-total-label {{ display: flex; justify-content: space-between; align-items: baseline; }}
.receipt .r-total {{
    font-family: {FONT}; font-variation-settings: "opsz" 96, "wdth" 82; font-weight: 760; font-size: 3.4rem;
    letter-spacing: -0.04em; line-height: 1; text-align: right; margin: .25rem 0 .7rem;
}}
.receipt .r-bar {{ position: relative; height: 10px; background: {FIELD}; border-radius: 999px; }}
.receipt .r-bar i {{ position: absolute; inset: 0 auto 0 0; border-radius: 999px; }}
.receipt .r-bar b {{ position: absolute; top: -5px; bottom: -5px; left: 50%; width: 2px; background: {INK}; opacity: .55; }}
.receipt .r-scale {{ display: flex; justify-content: space-between; font-size: .72rem; color: {FAINT}; margin-top: .35rem; }}
.receipt .r-verdict {{
    margin-top: 1rem; padding: .6rem .8rem; border-radius: 10px; font-family: {FONT};
    font-weight: 650; font-size: .98rem; text-align: center;
}}
.v-yes {{ background: {EMERALD_SOFT}; color: {EMERALD_DEEP}; }}
.v-mid {{ background: {SAFFRON_SOFT}; color: #8a5a00; }}
.v-no  {{ background: {FIELD}; color: {MUTED}; }}
.receipt .r-foot {{
    display: flex; flex-direction: column; align-items: center; gap: .45rem; margin-top: 1.2rem;
    font-size: .72rem; color: {FAINT};
}}
.receipt .barcode {{ height: 34px; max-width: 100%; opacity: .85; }}
.receipt.empty {{ animation: none; color: {FAINT}; text-align: center; padding: 2.2rem 1.5rem 2rem; }}
.receipt.empty .ghost {{ height: 10px; border-radius: 4px; background: {FIELD}; margin: .55rem auto; }}
.receipt.empty .r-title {{ color: {INK}; margin-top: 1.1rem; }}
.receipt.empty p {{ font-family: {FONT}; font-size: .92rem; color: {MUTED}; margin: .4rem auto 0; max-width: 18rem; }}

.advice {{ padding: 0 .3rem; }}
.advice .subhead {{ margin-top: .2rem; }}

/* ---------- Comparación (puntos) ---------- */
.dots {{ display: grid; gap: 1.05rem; margin-top: .6rem; }}
.dot-row {{ display: grid; grid-template-columns: minmax(9rem, 13rem) 1fr minmax(7rem, 10rem); gap: 1.4rem; align-items: center; }}
.dot-row .val {{ text-align: right; font-size: 1rem; line-height: 1.25; }}
.dot-row .val b {{ font-weight: 700; color: {INK}; font-variant-numeric: tabular-nums; }}
.dot-row .val small {{ display: block; color: {MUTED}; font-size: .78rem; }}
.dot-row .name {{ font-size: .92rem; font-weight: 600; color: {INK}; line-height: 1.25; }}
.dot-row .name small {{ display: block; font-weight: 400; color: {MUTED}; font-size: .8rem; }}
.dot-track {{ position: relative; height: 26px; }}
.dot-track::before {{ content: ""; position: absolute; left: 0; right: 0; top: 12px; height: 2px; background: {LINE}; border-radius: 2px; }}
.dot {{ position: absolute; top: 2px; width: 22px; height: 22px; margin-left: -11px; border-radius: 50%; border: 3px solid {SURFACE}; }}
.dot.buy {{ background: {EMERALD}; }}
.dot.nobuy {{ background: {SLATE}; }}
.dot.me {{ background: {INK}; border-radius: 3px; transform: rotate(45deg); width: 13px; height: 13px; margin-left: -6.5px; top: 6.5px; border: none; box-shadow: 0 0 0 2px {SURFACE}; }}
.legend {{ display: flex; flex-wrap: wrap; gap: 1.2rem; font-size: .85rem; color: {MUTED}; margin-top: .2rem; }}
.legend span {{ display: inline-flex; align-items: center; gap: .45rem; }}
.legend .dot {{ position: static; margin: 0; border: none; width: 14px; height: 14px; }}
.legend .dot.me {{ width: 10px; height: 10px; box-shadow: none; }}

/* ---------- Waffle y datos ---------- */
.waffle {{ display: grid; grid-template-columns: repeat(20, 1fr); gap: 4px; max-width: 520px; }}
.waffle i {{ aspect-ratio: 1; border-radius: 3px; background: {SLATE}; opacity: .55; }}
.waffle i.on {{ background: {EMERALD}; opacity: 1; }}
.big-fact {{
    font-variation-settings: "opsz" 72, "wdth" 86; font-weight: 700; font-size: 1.75rem; line-height: 1.2;
    letter-spacing: -0.025em; color: {INK}; margin: 0 0 1rem; max-width: 30rem;
}}
.big-fact em {{ font-style: normal; color: {EMERALD}; }}
.facts {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .9rem 1.4rem; margin-top: 1.2rem; }}
.facts div {{ border-top: 1px solid {LINE}; padding-top: .55rem; }}
.facts b {{ display: block; font-size: 1.35rem; font-weight: 720; letter-spacing: -0.02em; color: {INK}; }}
.facts span {{ font-size: .85rem; color: {MUTED}; line-height: 1.4; }}

/* ---------- Marcador de métricas ---------- */
.scoreboard {{
    display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); background: {SURFACE};
    border: 1px solid {LINE}; border-radius: 22px; margin-bottom: 1.4rem;
}}
.scoreboard > div {{ padding: 1.2rem 1.35rem; border-left: 1px solid {LINE}; }}
.scoreboard > div:first-child {{ border-left: none; }}
.scoreboard .label {{ font-size: .88rem; font-weight: 600; color: {MUTED}; }}
.scoreboard .value {{
    font-variation-settings: "opsz" 72, "wdth" 84; font-weight: 740; font-size: 2.4rem; letter-spacing: -0.035em;
    color: {INK}; line-height: 1.1; margin: .2rem 0 .35rem;
}}
.scoreboard .note {{ font-size: .84rem; color: {MUTED}; line-height: 1.4; }}

/* ---------- Pasos (secuencias reales) ---------- */
.steps {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(128px, 1fr)); gap: .5rem;
    margin: .4rem 0 .9rem; counter-reset: s;
}}
.steps div {{
    counter-increment: s; background: {SURFACE}; border: 1px solid {LINE}; border-radius: 14px;
    padding: .75rem .85rem; display: flex; flex-direction: column; gap: .5rem;
    font-weight: 650; font-size: .92rem; color: {INK}; line-height: 1.25;
}}
.steps div::before {{
    content: counter(s); display: grid; place-items: center; width: 1.6rem; height: 1.6rem;
    border-radius: 50%; background: {EMERALD_SOFT}; color: {EMERALD_DEEP}; font-size: .8rem; font-weight: 700;
}}
.steps div small {{ display: block; font-weight: 400; font-size: .78rem; color: {MUTED}; }}
.steps div:last-child::before {{ background: {EMERALD}; color: #fff; }}

/* ---------- Usos ---------- */
.uses {{
    display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); background: {SURFACE};
    border: 1px solid {LINE}; border-radius: 22px;
}}
.uses > div {{ padding: 1.3rem 1.4rem; border-left: 1px solid {LINE}; }}
.uses > div:first-child {{ border-left: none; }}
.uses svg {{ width: 30px; height: 30px; color: {EMERALD}; }}
.uses h4 {{ font-family: {FONT}; font-size: 1.05rem; font-weight: 680; margin: .55rem 0 .3rem; padding: 0; color: {INK}; }}
.uses p {{ font-size: .9rem; color: {MUTED}; line-height: 1.5; margin: 0; }}

/* ---------- Diccionario ---------- */
table.dict {{ width: 100%; border-collapse: collapse; font-size: .9rem; }}
table.dict th {{
    text-align: left; font-weight: 650; color: {MUTED}; font-size: .84rem;
    padding: .55rem .7rem; border-bottom: 1px solid {LINE};
}}
table.dict td {{ padding: .6rem .7rem; border-bottom: 1px solid {LINE}; vertical-align: top; color: {INK}; }}
table.dict tr:last-child td {{ border-bottom: none; }}
table.dict code {{ font-size: .8rem; padding: .1rem .35rem; }}
.tag {{ display: inline-block; padding: .12rem .6rem; border-radius: 999px; font-size: .8rem; font-weight: 650; }}
.tag-yes {{ background: {EMERALD_SOFT}; color: {EMERALD_DEEP}; }}
.tag-no {{ background: {FIELD}; color: {MUTED}; }}
.tag-target {{ background: {INK}; color: #fff; }}

[data-testid="stExpander"] {{ border: 1px solid {LINE}; border-radius: 16px; background: {SURFACE}; }}
[data-testid="stExpander"] summary p {{ font-weight: 600; }}

.footer {{
    margin-top: 4rem; padding-top: 1.4rem; border-top: 1px solid {LINE}; color: {MUTED};
    font-size: .88rem; line-height: 1.6; display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;
}}
.footer b {{ color: {INK}; font-weight: 700; }}
.footer > div:last-child {{ text-align: right; }}
.footer a {{ color: {EMERALD}; text-decoration: none; font-weight: 600; }}

/* ---------- Celular ---------- */
@media (max-width: 760px) {{
    .block-container {{ padding: .8rem 1rem 3rem; }}
    .stage {{ grid-template-columns: 1fr; padding: 2.2rem 1.5rem 0; border-radius: 24px; min-height: 0; }}
    .stage-art {{ display: none; }}
    .stage-copy {{ padding-bottom: 2rem; }}
    .topbar nav a {{ padding: .4rem .75rem; font-size: .85rem; }}
    .footer {{ grid-template-columns: 1fr; }}
    .footer > div:last-child {{ text-align: left; }}
    .topbar .long {{ display: none; }}
    .stage .lead {{ font-size: 1.02rem; }}
    .scoreboard, .uses {{ grid-template-columns: 1fr 1fr; }}
    .scoreboard > div:nth-child(3), .uses > div:nth-child(3) {{ border-left: none; }}
    .scoreboard > div:nth-child(n+3), .uses > div:nth-child(n+3) {{ border-top: 1px solid {LINE}; }}
    .dot-row {{ grid-template-columns: 1fr auto; gap: .3rem .8rem; }}
    .dot-row .dot-track {{ grid-column: 1 / -1; grid-row: 2; }}
    .section-title {{ font-size: 1.6rem; }}
    table.dict th:nth-child(3), table.dict td:nth-child(3) {{ display: none; }}
    .receipt .r-total {{ font-size: 2.8rem; }}
}}
</style>
"""
