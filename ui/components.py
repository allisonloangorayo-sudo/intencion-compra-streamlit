"""Piezas HTML de la interfaz: portada, ticket, comparación, waffle, pasos e íconos.

Cada función devuelve HTML en una sola línea: st.markdown interpreta las líneas
con sangría como bloques de código, así que se eliminan saltos y sangrías.
"""

from __future__ import annotations

import re

from ui.styles import EMERALD, SAFFRON, SLATE


def compact(html: str) -> str:
    html = re.sub(r"\s*\n\s*", " ", html)       # saltos y sangrías -> un espacio
    return re.sub(r">\s+<", "><", html).strip()  # sin espacios entre etiquetas


def _es(x: float, decimals: int = 1) -> str:
    return f"{x:.{decimals}f}".replace(".", ",")


# ---------------------------------------------------------------------------
# Barra superior y portada
# ---------------------------------------------------------------------------
MARK = (
    '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" '
    'stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h12v18l-2-1.4-2 1.4-2-1.4-2 1.4-2-1.4L6 21Z"/>'
    '<path d="M9 8h6M9 12h6M9 16h3"/></svg>'
)


def topbar_html(repo_url: str) -> str:
    return compact(f"""
    <header class="topbar">
      <span class="brand"><span class="mark">{MARK}</span>Intención de compra</span>
      <nav><a href="{repo_url}" target="_blank" rel="noopener"><span class="long">Código en </span>GitHub</a></nav>
    </header>
    """)


def _trail_svg() -> str:
    """Recorrido de una visita: lo que lee el modelo."""
    stops = [("Inicio", 30), ("Producto", 140), ("Producto", 250), ("Carrito", 360), ("Pago", 470)]
    nodes = []
    for i, (label, x) in enumerate(stops):
        last = i == len(stops) - 1
        fill = "#7fe0c1" if last else "#0d3d34"
        nodes.append(
            f'<circle cx="{x}" cy="22" r="{7 if last else 5.5}" fill="{fill}" stroke="#7fe0c1" stroke-width="1.6"/>'
            f'<text x="{x}" y="50" text-anchor="middle" font-size="12.5" '
            f'fill="{"#ffffff" if last else "#b9d8cf"}" font-weight="{600 if last else 500}">{label}</text>'
        )
    return f"""
    <svg class="trail" viewBox="0 0 500 100" role="img" font-family="Bricolage Grotesque, sans-serif"
         aria-label="Recorrido de una visita: inicio, producto, producto, carrito y pago, o salida sin compra">
      <path d="M30 22 H470" stroke="#7fe0c1" stroke-width="1.6"/>
      <path d="M250 60 C250 78 262 86 284 86" stroke="#5f8f84" stroke-width="1.4" stroke-dasharray="3 4" fill="none"/>
      <text x="292" y="90" font-size="12" fill="#8fbcaf">o se va sin comprar</text>
      {"".join(nodes)}
    </svg>
    """


def hero_html(n_rows: str, roc_auc: str, demo_receipt: str) -> str:
    return compact(f"""
    <section class="stage">
      <div class="stage-copy">
        <h1>¿Esta visita terminará en compra?</h1>
        <p class="lead">Describe cómo navega una persona en una tienda online. Un modelo entrenado
        con {n_rows} visitas reales estima la probabilidad de que compre y te muestra qué la empujó
        hacia arriba o hacia abajo.</p>
        {_trail_svg()}
        <p class="meta">El modelo no sabe quién es la persona: solo lee su recorrido. Acierta el orden
        entre compradores y no compradores con un ROC-AUC de {roc_auc}.</p>
      </div>
      <div class="stage-art" aria-hidden="true">{demo_receipt}</div>
    </section>
    """)


# ---------------------------------------------------------------------------
# Ticket
# ---------------------------------------------------------------------------
def verdict(p: float, threshold: float) -> tuple[str, str, str]:
    """(clase css, texto del ticket, color de la barra)"""
    if p >= threshold:
        return "v-yes", "Clasificación: compra", EMERALD
    if p >= 0.25:
        return "v-mid", "No compra, pero está dudando", SAFFRON
    return "v-no", "Clasificación: no compra", SLATE


def _barcode(seed: str) -> str:
    """Código de barras decorativo, siempre igual para el mismo texto."""
    widths = [1 + (ord(ch) * 7 + i * 3) % 4 for i, ch in enumerate(seed * 4)][:46]
    stops, x = [], 0
    for i, w in enumerate(widths):
        color = "var(--ink)" if i % 2 == 0 else "transparent"
        stops.append(f"{color} {x}px {x + w}px")
        x += w
    return f'<div class="barcode" style="background:linear-gradient(90deg,{",".join(stops)});width:{x}px"></div>'


def receipt_html(p: float, threshold: float, header: str, items: list[tuple[str, str]],
                 effects: list[tuple[str, float]], demo: bool = False) -> str:
    css, text, color = verdict(p, threshold)
    rows = "".join(f'<div class="r-row"><span>{k}</span><span>{v}</span></div>' for k, v in items)
    if effects:
        eff = "".join(
            f'<div class="r-row"><span>{k}</span>'
            f'<span class="{"up" if v > 0 else "down"}">{"+" if v > 0 else "−"}{_es(abs(v))} pts</span></div>'
            for k, v in effects
        )
    else:
        eff = '<div class="r-row"><span>Nada se aleja de una visita típica</span><span>0 pts</span></div>'
    total = _es(p * 100) + " %"
    code = f"{p:.4f}{header}"
    wrap = "receipt-wrap demo" if demo else "receipt-wrap"
    return compact(f"""
    <div class="{wrap}"><div class="receipt" role="group" aria-label="Resultado: {total}">
      <div class="r-head">
        <div class="r-title">Ticket de la visita</div>
        <div class="r-sub">{header}</div>
      </div>
      <div class="r-label">Lo que hizo</div>
      {rows}
      <hr>
      <div class="r-label">Lo que movió la probabilidad</div>
      {eff}
      <hr>
      <div class="r-total-label"><span>Probabilidad de compra</span></div>
      <div class="r-total">{total}</div>
      <div class="r-bar"><i style="width:{max(p * 100, 1.5):.1f}%;background:{color}"></i><b></b></div>
      <div class="r-scale"><span>0 %</span><span>umbral 50 %</span><span>100 %</span></div>
      <div class="r-verdict {css}">{text}</div>
      <div class="r-foot">{_barcode(code)}<span>Umbral de decisión: 50 %</span></div>
    </div></div>
    """)


def empty_receipt_html() -> str:
    ghosts = "".join(f'<div class="ghost" style="width:{w}%"></div>' for w in (70, 85, 60, 78, 50))
    return compact(f"""
    <div class="receipt-wrap"><div class="receipt empty">
      {ghosts}
      <div class="r-title">Aquí se imprime el resultado</div>
      <p>Elige un ejemplo o escribe los datos de una visita y pulsa <b>Calcular probabilidad</b>.</p>
    </div></div>
    """)


# ---------------------------------------------------------------------------
# Comparación con compradores reales
# ---------------------------------------------------------------------------
def compare_html(rows: list[dict]) -> str:
    """rows: name, hint, me, buy, nobuy (valores numéricos) y textos me_txt, buy_txt, nobuy_txt."""
    out = []
    for r in rows:
        top = max(r["me"], r["buy"], r["nobuy"]) or 1.0
        pos = {k: 3 + 94 * (r[k] / top) for k in ("me", "buy", "nobuy")}
        title = (f'Esta visita: {r["me_txt"]}. Comprador típico: {r["buy_txt"]}. '
                 f'No comprador típico: {r["nobuy_txt"]}.')
        out.append(
            f'<div class="dot-row"><div class="name">{r["name"]}<small>{r["hint"]}</small></div>'
            f'<div class="dot-track" title="{title}" aria-label="{title}">'
            f'<span class="dot nobuy" style="left:{pos["nobuy"]:.1f}%"></span>'
            f'<span class="dot buy" style="left:{pos["buy"]:.1f}%"></span>'
            f'<span class="dot me" style="left:{pos["me"]:.1f}%"></span></div>'
            f'<div class="val"><b>{r["me_txt"]}</b><small>comprador típico: {r["buy_txt"]}</small></div></div>'
        )
    legend = (
        '<div class="legend"><span><i class="dot me"></i>Esta visita</span>'
        '<span><i class="dot buy"></i>Comprador típico</span>'
        '<span><i class="dot nobuy"></i>No comprador típico</span></div>'
    )
    return compact(f'{legend}<div class="dots">{"".join(out)}</div>')


# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------
def waffle_html(positive_rate: float, cells: int = 200) -> str:
    on = round(positive_rate * cells)
    squares = "".join(f'<i class="{"on" if i < on else ""}"></i>' for i in range(cells))
    return f'<div class="waffle" role="img" aria-label="{on} de {cells} cuadros en verde">{squares}</div>'


def facts_html(facts: list[tuple[str, str]]) -> str:
    return compact('<div class="facts">' + "".join(
        f"<div><b>{v}</b><span>{k}</span></div>" for k, v in facts) + "</div>")


# ---------------------------------------------------------------------------
# Modelo y proyecto
# ---------------------------------------------------------------------------
def scoreboard_html(cards: list[tuple[str, str, str]]) -> str:
    return compact('<div class="scoreboard">' + "".join(
        f'<div><div class="label">{a}</div><div class="value">{b}</div><div class="note">{c}</div></div>'
        for a, b, c in cards) + "</div>")


def steps_html(steps: list[tuple[str, str]]) -> str:
    return compact('<div class="steps">' + "".join(
        f"<div><span>{a}<small>{b}</small></span></div>" for a, b in steps) + "</div>")


ICONS = {
    "tag": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8Z"/>'
           '<circle cx="7.5" cy="7.5" r="1.5"/></svg>',
    "chat": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12Z"/>'
            '<path d="M8.5 11.5h7M8.5 14.5h4"/></svg>',
    "chart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 3v18h18"/>'
             '<path d="M7 15l4-4 3 3 6-7"/></svg>',
}


def uses_html(uses: list[tuple[str, str, str]]) -> str:
    return compact('<div class="uses">' + "".join(
        f"<div>{ICONS[icon]}<h4>{title}</h4><p>{text}</p></div>" for icon, title, text in uses) + "</div>")


__all__ = [
    "compact", "topbar_html", "hero_html", "receipt_html", "empty_receipt_html", "compare_html", "waffle_html",
    "facts_html", "scoreboard_html", "steps_html", "uses_html", "verdict",
]
