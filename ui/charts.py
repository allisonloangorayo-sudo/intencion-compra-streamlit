"""Gráficas de la app (Altair, incluido con Streamlit) y el medidor de probabilidad."""

from __future__ import annotations

import math

import altair as alt
import pandas as pd

from ui.styles import AMBER, BLUE, GRAY, GREEN_SOFT, INK, LINE, MUTED, RED_SOFT

FONT = "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"


def _style(chart: alt.Chart, height: int = 260) -> alt.Chart:
    return (
        chart.properties(height=height)
        .configure(font=FONT, background="transparent")
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor=MUTED, titleColor=MUTED, labelFontSize=12, titleFontSize=12,
            titleFontWeight=500, gridColor=LINE, domainColor=LINE, tickColor=LINE,
            labelPadding=6,
        )
        .configure_legend(labelColor=MUTED, titleColor=MUTED, labelFontSize=12, orient="top")
    )


# ---------------------------------------------------------------------------
# Medidor
# ---------------------------------------------------------------------------
def gauge_color(p: float) -> str:
    if p >= 0.5:
        return GREEN_SOFT
    if p >= 0.25:
        return AMBER
    return RED_SOFT


def gauge_svg(p: float) -> str:
    """Semicírculo SVG con la probabilidad de compra."""
    p = min(max(p, 0.0), 1.0)
    cx, cy, r = 120, 120, 96
    phi = math.pi * (1 - p)
    x, y = cx + r * math.cos(phi), cy - r * math.sin(phi)
    track = f"M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}"
    value = f"M {cx - r} {cy} A {r} {r} 0 0 1 {x:.2f} {y:.2f}" if p > 0.002 else ""
    # Marca del umbral (50 %)
    tx, ty1, ty2 = cx, cy - r - 12, cy - r + 12
    pct = f"{p * 100:.1f}".replace(".", ",") + " %"
    return f"""
<div style="display:flex;justify-content:center;">
<svg viewBox="0 0 240 150" width="100%" style="max-width:340px" role="img"
     aria-label="Probabilidad de compra {pct}">
  <path d="{track}" fill="none" stroke="{LINE}" stroke-width="18" stroke-linecap="round"/>
  {"<path d='" + value + "' fill='none' stroke='" + gauge_color(p) + "' stroke-width='18' stroke-linecap='round'/>" if value else ""}
  <line x1="{tx}" y1="{ty1}" x2="{tx}" y2="{ty2}" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="2 2"/>
  <text x="{tx}" y="{ty1 - 4}" text-anchor="middle" font-size="9" fill="{MUTED}"
        font-family="{FONT}">umbral 50 %</text>
  <text x="{cx}" y="{cy - 14}" text-anchor="middle" font-size="38" font-weight="700"
        fill="{INK}" font-family="{FONT}" letter-spacing="-1">{pct}</text>
  <text x="{cx - r}" y="{cy + 22}" text-anchor="middle" font-size="10" fill="{MUTED}"
        font-family="{FONT}">0 %</text>
  <text x="{cx + r}" y="{cy + 22}" text-anchor="middle" font-size="10" fill="{MUTED}"
        font-family="{FONT}">100 %</text>
</svg>
</div>
"""


# ---------------------------------------------------------------------------
# Predicción
# ---------------------------------------------------------------------------
def contributions_chart(df: pd.DataFrame) -> alt.Chart:
    """df: columnas etiqueta, puntos (positivo = sube la probabilidad)."""
    df = df.copy()
    df["efecto"] = df["puntos"].apply(lambda v: "Sube" if v >= 0 else "Baja")
    df["texto"] = df["puntos"].apply(lambda v: f"{v:+.1f} pts".replace(".", ","))
    order = df.sort_values("puntos", ascending=False)["etiqueta"].tolist()
    base = alt.Chart(df).encode(
        y=alt.Y("etiqueta:N", sort=order, title=None, axis=alt.Axis(labelLimit=260)),
        x=alt.X("puntos:Q", title="Cambio en la probabilidad (puntos)"),
    )
    bars = base.mark_bar(cornerRadius=4, height=18).encode(
        color=alt.Color(
            "efecto:N",
            scale=alt.Scale(domain=["Sube", "Baja"], range=[GREEN_SOFT, RED_SOFT]),
            legend=alt.Legend(title=None),
        ),
        tooltip=[alt.Tooltip("etiqueta:N", title="Variable"),
                 alt.Tooltip("texto:N", title="Efecto")],
    )
    rule = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color=MUTED).encode(x="x:Q")
    return _style(bars + rule, height=max(180, 34 * len(df)))


# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------
def donut_chart(counts: dict) -> alt.Chart:
    df = pd.DataFrame({"clase": list(counts), "sesiones": list(counts.values())})
    df["pct"] = df["sesiones"] / df["sesiones"].sum()
    share = df.loc[df["clase"] == "Compra", "pct"].iloc[0]
    center = pd.DataFrame({"t": [f"{share * 100:.1f}".replace(".", ",") + " %"], "s": ["compran"]})
    arcs = alt.Chart(df).mark_arc(innerRadius=78, cornerRadius=4, padAngle=0.01).encode(
        theta="sesiones:Q",
        color=alt.Color("clase:N", scale=alt.Scale(domain=["No compra", "Compra"], range=[GRAY, BLUE]),
                        legend=alt.Legend(title=None)),
        tooltip=[alt.Tooltip("clase:N", title="Clase"),
                 alt.Tooltip("sesiones:Q", title="Sesiones", format=","),
                 alt.Tooltip("pct:Q", title="Porcentaje", format=".1%")],
    )
    big = alt.Chart(center).mark_text(fontSize=26, fontWeight=700, color=INK, dy=-6).encode(text="t:N")
    small = alt.Chart(center).mark_text(fontSize=12, color=MUTED, dy=16).encode(text="s:N")
    return _style(arcs + big + small, height=260)


def rate_bar_chart(records: list[dict], key: str, x_title: str, highlight_max: bool = False,
                   horizontal: bool = False, labels: dict | None = None) -> alt.Chart:
    df = pd.DataFrame(records)
    if labels:
        df[key] = df[key].map(lambda v: labels.get(v, v))
    order = df[key].tolist()
    df["texto"] = (df["tasa"] * 100).map(lambda v: f"{v:.0f} %")
    color = alt.value(BLUE)
    if highlight_max:
        df["destacado"] = df["tasa"] == df["tasa"].max()
        color = alt.condition("datum.destacado", alt.value(BLUE), alt.value("#9ecbf5"))
    tooltip = [alt.Tooltip(f"{key}:N", title=x_title),
               alt.Tooltip("tasa:Q", title="Tasa de compra", format=".1%"),
               alt.Tooltip("sesiones:Q", title="Sesiones", format=",")]
    if horizontal:
        base = alt.Chart(df).encode(
            y=alt.Y(f"{key}:N", sort=order, title=None, scale=alt.Scale(paddingInner=0.35)),
            x=alt.X("tasa:Q", title="Tasa de compra", axis=alt.Axis(format="%"),
                    scale=alt.Scale(domain=[0, float(df["tasa"].max()) * 1.18])),
        )
        bars = base.mark_bar(cornerRadius=4).encode(color=color, tooltip=tooltip)
        text = base.mark_text(align="left", dx=6, color=INK, fontSize=12).encode(text="texto:N")
        return _style(bars + text, height=48 * len(df) + 30)
    base = alt.Chart(df).encode(
        x=alt.X(f"{key}:N", sort=order, title=x_title, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("tasa:Q", title="Tasa de compra", axis=alt.Axis(format="%")),
    )
    bars = base.mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, size=38).encode(
        color=color, tooltip=tooltip
    )
    text = base.mark_text(dy=-8, color=INK, fontSize=12).encode(text="texto:N")
    return _style(bars + text, height=280)


# ---------------------------------------------------------------------------
# Modelo
# ---------------------------------------------------------------------------
def model_comparison_chart(comparison: dict, names: dict) -> alt.Chart:
    metrics = {"roc_auc": "ROC-AUC", "pr_auc": "PR-AUC", "recall_compra": "Recall (compra)",
               "precision_compra": "Precisión (compra)", "f1_compra": "F1 (compra)"}
    rows = [
        {"modelo": names[m], "métrica": label, "valor": vals[k]}
        for m, vals in comparison.items() for k, label in metrics.items()
    ]
    df = pd.DataFrame(rows)
    chart = alt.Chart(df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X("métrica:N", title=None, sort=list(metrics.values()), axis=alt.Axis(labelAngle=0)),
        xOffset=alt.XOffset("modelo:N", sort=[names["logistic_regression"], names["random_forest"]]),
        y=alt.Y("valor:Q", title=None, scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("modelo:N", legend=alt.Legend(title=None),
                        scale=alt.Scale(domain=[names["logistic_regression"], names["random_forest"]],
                                        range=[GRAY, BLUE])),
        tooltip=["modelo:N", "métrica:N", alt.Tooltip("valor:Q", format=".3f")],
    )
    return _style(chart, height=280)


def confusion_chart(cm: list[list[int]]) -> alt.Chart:
    labels = ["No compra", "Compra"]
    rows = []
    for i, real in enumerate(labels):
        for j, pred in enumerate(labels):
            ok = i == j
            rows.append({"real": real, "predicho": pred, "sesiones": cm[i][j],
                         "texto": f"{cm[i][j]:,}".replace(",", "."),
                         "tipo": "Acierto" if ok else "Error"})
    df = pd.DataFrame(rows)
    base = alt.Chart(df).encode(
        x=alt.X("predicho:N", title="Lo que predijo el modelo", sort=labels,
                axis=alt.Axis(labelAngle=0, orient="top")),
        y=alt.Y("real:N", title="Lo que pasó realmente", sort=labels),
    )
    rect = base.mark_rect(cornerRadius=10, stroke="white", strokeWidth=6).encode(
        color=alt.Color("tipo:N", scale=alt.Scale(domain=["Acierto", "Error"],
                                                 range=["#cfe5fb", "#fde2e1"]),
                        legend=None),
        tooltip=["real:N", "predicho:N", alt.Tooltip("texto:N", title="Sesiones")],
    )
    text = base.mark_text(fontSize=22, fontWeight=700, color=INK).encode(text="texto:N")
    return _style(rect + text, height=240)


def curve_chart(points: list[dict], x_title: str, y_title: str, diagonal: bool,
                baseline: float | None = None) -> alt.Chart:
    df = pd.DataFrame(points)
    line = alt.Chart(df).mark_line(color=BLUE, strokeWidth=2.5, interpolate="step-after").encode(
        x=alt.X("x:Q", title=x_title, scale=alt.Scale(domain=[0, 1])),
        y=alt.Y("y:Q", title=y_title, scale=alt.Scale(domain=[0, 1])),
    )
    area = alt.Chart(df).mark_area(color=BLUE, opacity=0.08, interpolate="step-after").encode(
        x="x:Q", y="y:Q"
    )
    layers = [area, line] if diagonal else [line]
    if diagonal:
        ref = pd.DataFrame({"x": [0, 1], "y": [0, 1]})
        layers.append(alt.Chart(ref).mark_line(color=GRAY, strokeDash=[4, 4]).encode(x="x:Q", y="y:Q"))
    if baseline is not None:
        ref = pd.DataFrame({"x": [0, 1], "y": [baseline, baseline]})
        layers.append(alt.Chart(ref).mark_line(color=GRAY, strokeDash=[4, 4]).encode(x="x:Q", y="y:Q"))
    return _style(alt.layer(*layers), height=280)


def proba_hist_chart(records: list[dict]) -> alt.Chart:
    df = pd.DataFrame(records)
    chart = alt.Chart(df).mark_bar(opacity=0.7, binSpacing=1).encode(
        x=alt.X("desde:Q", bin="binned", title="Probabilidad de compra que asignó el modelo",
                axis=alt.Axis(format="%")),
        x2="hasta:Q",
        y=alt.Y("sesiones:Q", title="Sesiones", stack=None),
        color=alt.Color("clase_real:N", title="Lo que pasó realmente",
                        scale=alt.Scale(domain=["No compra", "Compra"], range=[GRAY, BLUE])),
        tooltip=["clase_real:N", alt.Tooltip("desde:Q", format=".0%", title="Desde"),
                 alt.Tooltip("hasta:Q", format=".0%", title="Hasta"), "sesiones:Q"],
    )
    rule = alt.Chart(pd.DataFrame({"x": [0.5]})).mark_rule(color=MUTED, strokeDash=[4, 4]).encode(x="x:Q")
    return _style(chart + rule, height=280)


def importance_chart(records: list[dict], labels: dict) -> alt.Chart:
    df = pd.DataFrame(records)
    df["etiqueta"] = df["variable"].map(lambda v: labels.get(v, v))
    df = df.sort_values("importancia", ascending=False)
    df["destacado"] = df["importancia"] == df["importancia"].max()
    chart = alt.Chart(df).mark_bar(cornerRadius=4, height=16).encode(
        y=alt.Y("etiqueta:N", sort=df["etiqueta"].tolist(), title=None, axis=alt.Axis(labelLimit=260)),
        x=alt.X("importancia:Q", title="Caída del ROC-AUC al desordenar la variable"),
        color=alt.condition("datum.destacado", alt.value(BLUE), alt.value("#9ecbf5")),
        tooltip=[alt.Tooltip("etiqueta:N", title="Variable"),
                 alt.Tooltip("importancia:Q", title="Importancia", format=".4f")],
    )
    return _style(chart, height=26 * len(df))
