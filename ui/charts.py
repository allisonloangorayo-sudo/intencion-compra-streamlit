"""Gráficas de la app (Altair, incluido con Streamlit).

Colores con significado: esmeralda = compra, pizarra = no compra.
"""

from __future__ import annotations

import altair as alt
import pandas as pd

from ui.styles import EMERALD, EMERALD_SOFT, INK, LINE, MINT, MUTED, ROSE_SOFT, SLATE

FONT = "Bricolage Grotesque, Segoe UI, system-ui, sans-serif"


def _style(chart: alt.Chart, height: int = 260) -> alt.Chart:
    return (
        chart.properties(height=height)
        .configure(font=FONT, background="transparent", padding={"left": 2, "right": 8, "top": 8, "bottom": 2})
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor=MUTED, titleColor=MUTED, labelFontSize=12, titleFontSize=12,
            titleFontWeight=500, gridColor=LINE, gridDash=[2, 3], domain=False, ticks=False,
            labelPadding=8, titlePadding=10,
        )
        .configure_legend(labelColor=MUTED, titleColor=MUTED, labelFontSize=12, titleFontSize=12,
                          orient="top", symbolType="circle", symbolSize=90)
    )


def rate_bar_chart(records: list[dict], key: str, x_title: str, highlight_max: bool = True,
                   horizontal: bool = False, labels: dict | None = None) -> alt.Chart:
    df = pd.DataFrame(records)
    if labels:
        df[key] = df[key].map(lambda v: labels.get(v, v))
    order = df[key].tolist()
    df["texto"] = (df["tasa"] * 100).map(lambda v: f"{v:.0f} %")
    df["destacado"] = (df["tasa"] == df["tasa"].max()) & highlight_max
    color = alt.condition("datum.destacado", alt.value(EMERALD), alt.value(MINT))
    tooltip = [alt.Tooltip(f"{key}:N", title=x_title),
               alt.Tooltip("tasa:Q", title="Tasa de compra", format=".1%"),
               alt.Tooltip("sesiones:Q", title="Visitas", format=",")]
    top = float(df["tasa"].max()) * 1.18
    if horizontal:
        base = alt.Chart(df).encode(
            y=alt.Y(f"{key}:N", sort=order, title=None, scale=alt.Scale(paddingInner=0.38),
                    axis=alt.Axis(labelFontSize=13, labelColor=INK)),
            x=alt.X("tasa:Q", title=None, axis=None, scale=alt.Scale(domain=[0, top])),
        )
        bars = base.mark_bar(cornerRadius=6).encode(color=color, tooltip=tooltip)
        text = base.mark_text(align="left", dx=8, color=INK, fontSize=13, fontWeight=600).encode(text="texto:N")
        return _style(bars + text, height=46 * len(df) + 10)
    base = alt.Chart(df).encode(
        x=alt.X(f"{key}:N", sort=order, title=x_title, axis=alt.Axis(labelAngle=0, labelColor=INK)),
        y=alt.Y("tasa:Q", title=None, axis=None, scale=alt.Scale(domain=[0, top])),
    )
    bars = base.mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8, size=40).encode(
        color=color, tooltip=tooltip
    )
    text = base.mark_text(dy=-10, color=INK, fontSize=13, fontWeight=600).encode(text="texto:N")
    return _style(bars + text, height=260)


def model_comparison_chart(comparison: dict, names: dict) -> alt.Chart:
    metrics = {"roc_auc": "ROC-AUC", "pr_auc": "PR-AUC", "recall_compra": "Recall",
               "precision_compra": "Precisión", "f1_compra": "F1"}
    order = [names["logistic_regression"], names["random_forest"]]
    rows = [
        {"modelo": names[m], "métrica": label, "valor": vals[k],
         "texto": f"{vals[k]:.2f}".replace(".", ",")}
        for m, vals in comparison.items() for k, label in metrics.items()
    ]
    df = pd.DataFrame(rows)
    base = alt.Chart(df).encode(
        x=alt.X("métrica:N", title=None, sort=list(metrics.values()),
                axis=alt.Axis(labelAngle=0, labelColor=INK, labelFontSize=13)),
        xOffset=alt.XOffset("modelo:N", sort=order),
        y=alt.Y("valor:Q", title=None, scale=alt.Scale(domain=[0, 1.08]), axis=None),
    )
    bars = base.mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
        color=alt.Color("modelo:N", legend=alt.Legend(title=None),
                        scale=alt.Scale(domain=order, range=[SLATE, EMERALD])),
        tooltip=["modelo:N", "métrica:N", alt.Tooltip("valor:Q", format=".3f")],
    )
    text = base.mark_text(dy=-8, fontSize=11, color=MUTED).encode(text="texto:N")
    return _style(bars + text, height=270)


def confusion_chart(cm: list[list[int]]) -> alt.Chart:
    labels = ["No compra", "Compra"]
    rows = []
    for i, real in enumerate(labels):
        for j, pred in enumerate(labels):
            rows.append({"real": real, "predicho": pred, "sesiones": cm[i][j],
                         "texto": f"{cm[i][j]:,}".replace(",", "."),
                         "tipo": "Acierto" if i == j else "Error"})
    df = pd.DataFrame(rows)
    base = alt.Chart(df).encode(
        x=alt.X("predicho:N", title="Lo que predijo el modelo", sort=labels,
                axis=alt.Axis(labelAngle=0, orient="top", labelColor=INK, labelFontSize=13)),
        y=alt.Y("real:N", title="Lo que pasó", sort=labels, axis=alt.Axis(labelColor=INK, labelFontSize=13)),
    )
    rect = base.mark_rect(cornerRadius=14, stroke="white", strokeWidth=8).encode(
        color=alt.Color("tipo:N", scale=alt.Scale(domain=["Acierto", "Error"],
                                                 range=[EMERALD_SOFT, ROSE_SOFT]), legend=None),
        tooltip=["real:N", "predicho:N", alt.Tooltip("texto:N", title="Visitas")],
    )
    text = base.mark_text(fontSize=26, fontWeight=700, color=INK).encode(text="texto:N")
    return _style(rect + text, height=250)


def curve_chart(points: list[dict], x_title: str, y_title: str, diagonal: bool,
                baseline: float | None = None) -> alt.Chart:
    df = pd.DataFrame(points)
    line = alt.Chart(df).mark_line(color=EMERALD, strokeWidth=2.5, interpolate="step-after").encode(
        x=alt.X("x:Q", title=x_title, scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format="%", tickCount=5)),
        y=alt.Y("y:Q", title=y_title, scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format="%", tickCount=5)),
    )
    area = alt.Chart(df).mark_area(color=EMERALD, opacity=0.09, interpolate="step-after").encode(x="x:Q", y="y:Q")
    layers = [area, line] if diagonal else [line]
    if diagonal:
        ref = pd.DataFrame({"x": [0, 1], "y": [0, 1]})
        layers.append(alt.Chart(ref).mark_line(color=SLATE, strokeDash=[4, 4]).encode(x="x:Q", y="y:Q"))
    if baseline is not None:
        ref = pd.DataFrame({"x": [0, 1], "y": [baseline, baseline]})
        layers.append(alt.Chart(ref).mark_line(color=SLATE, strokeDash=[4, 4]).encode(x="x:Q", y="y:Q"))
    return _style(alt.layer(*layers), height=270)


def proba_hist_chart(records: list[dict]) -> alt.Chart:
    df = pd.DataFrame(records)
    chart = alt.Chart(df).mark_bar(binSpacing=2, cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X("desde:Q", bin="binned", title="Probabilidad de compra que asignó el modelo",
                axis=alt.Axis(format="%", tickCount=5)),
        x2="hasta:Q",
        y=alt.Y("sesiones:Q", title="Visitas", stack=None),
        color=alt.Color("clase_real:N", title="Lo que pasó",
                        scale=alt.Scale(domain=["No compra", "Compra"], range=[SLATE, EMERALD])),
        opacity=alt.condition("datum.clase_real == 'Compra'", alt.value(0.92), alt.value(0.75)),
        tooltip=[alt.Tooltip("clase_real:N", title="Lo que pasó"),
                 alt.Tooltip("desde:Q", format=".0%", title="Desde"),
                 alt.Tooltip("hasta:Q", format=".0%", title="Hasta"),
                 alt.Tooltip("sesiones:Q", title="Visitas")],
    )
    rule = alt.Chart(pd.DataFrame({"x": [0.5]})).mark_rule(color=INK, strokeDash=[4, 4], opacity=0.5).encode(x="x:Q")
    return _style(chart + rule, height=270)


def importance_chart(records: list[dict], labels: dict) -> alt.Chart:
    df = pd.DataFrame(records)
    df["etiqueta"] = df["variable"].map(lambda v: labels.get(v, v))
    df = df.sort_values("importancia", ascending=False)
    df["destacado"] = df["importancia"] == df["importancia"].max()
    chart = alt.Chart(df).mark_bar(cornerRadius=5, height=14).encode(
        y=alt.Y("etiqueta:N", sort=df["etiqueta"].tolist(), title=None,
                axis=alt.Axis(labelLimit=280, labelColor=INK)),
        x=alt.X("importancia:Q", title="Cuánto empeora el ROC-AUC al desordenar la variable"),
        color=alt.condition("datum.destacado", alt.value(EMERALD), alt.value(MINT)),
        tooltip=[alt.Tooltip("etiqueta:N", title="Variable"),
                 alt.Tooltip("importancia:Q", title="Importancia", format=".4f")],
    )
    return _style(chart, height=25 * len(df))
