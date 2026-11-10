"""
Aplicación Streamlit: ¿esta sesión terminará en compra?

Carga model.joblib (generado por train.py) y NO vuelve a entrenar.
Todo lo que muestra de los datos y del modelo viene precalculado en el artefacto.

Ejecutar:
    streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from ui import charts
from ui.components import (
    compact, compare_html, empty_receipt_html, facts_html, hero_html, receipt_html, scoreboard_html,
    steps_html, topbar_html, uses_html, verdict, waffle_html,
)
from ui.styles import CSS

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "model.joblib"
REPO_URL = "https://github.com/allisonloangorayo-sudo/intencion-compra-streamlit"

# ---------------------------------------------------------------------------
# Textos y etiquetas
# ---------------------------------------------------------------------------
MODEL_NAMES = {"logistic_regression": "Regresión logística", "random_forest": "Random forest"}

VISITOR_LABELS = {"New_Visitor": "Nuevo", "Returning_Visitor": "Recurrente", "Other": "Otro"}
MONTH_LABELS = {
    "Feb": "Febrero", "Mar": "Marzo", "May": "Mayo", "June": "Junio", "Jul": "Julio",
    "Aug": "Agosto", "Sep": "Septiembre", "Oct": "Octubre", "Nov": "Noviembre", "Dec": "Diciembre",
}
MONTH_SHORT = {
    "Feb": "Feb", "Mar": "Mar", "May": "May", "June": "Jun", "Jul": "Jul",
    "Aug": "Ago", "Sep": "Sep", "Oct": "Oct", "Nov": "Nov", "Dec": "Dic",
}
WEEKEND_LABELS = {"True": "Sí", "False": "No"}
DISPLAY = {"Month": MONTH_LABELS, "VisitorType": VISITOR_LABELS, "Weekend": WEEKEND_LABELS}

INTEGER_FEATURES = {"Administrative", "Informational", "ProductRelated"}
RATE_FEATURES = {"BounceRates", "ExitRates"}

VARIABLE_DICTIONARY = [
    ("Administrative", "Páginas de cuenta, inicio de sesión o configuración que visitó", "Numérica", "Sí"),
    ("Administrative_Duration", "Segundos totales en esas páginas", "Numérica", "Sí"),
    ("Informational", "Páginas informativas visitadas (contacto, preguntas frecuentes, envíos)", "Numérica", "Sí"),
    ("Informational_Duration", "Segundos totales en páginas informativas", "Numérica", "Sí"),
    ("ProductRelated", "Páginas de productos visitadas", "Numérica", "Sí"),
    ("ProductRelated_Duration", "Segundos totales mirando productos", "Numérica", "Sí"),
    ("BounceRates", "Promedio de rebote de las páginas vistas: % de visitas que entran por esa página y se van sin hacer nada más", "Numérica", "Sí"),
    ("ExitRates", "Promedio de salida de las páginas vistas: % de visitas a esa página que fueron la última de la sesión", "Numérica", "Sí"),
    ("PageValues", "Valor promedio de las páginas vistas según Google Analytics: qué tanto suelen aparecer antes de una compra", "Numérica", "Sí"),
    ("SpecialDay", "Cercanía a una fecha comercial (San Valentín, Día de la Madre): 0 lejos, 1 el día clave", "Numérica", "Sí"),
    ("Month", "Mes de la visita", "Categórica", "Sí"),
    ("VisitorType", "Visitante nuevo, recurrente u otro", "Categórica", "Sí"),
    ("Weekend", "Si la visita fue en fin de semana", "Categórica", "Sí"),
    ("OperatingSystems", "Sistema operativo (código numérico anónimo)", "Código", "No"),
    ("Browser", "Navegador (código numérico anónimo)", "Código", "No"),
    ("Region", "Región del visitante (código numérico anónimo)", "Código", "No"),
    ("TrafficType", "Fuente del tráfico (código numérico anónimo)", "Código", "No"),
    ("Revenue", "¿La sesión terminó en compra? Es la variable que se predice", "Objetivo", "Objetivo"),
]

# Etiquetas del formulario que reemplazan las del artefacto (más cortas, caben en una línea)
FORM_LABELS = {
    "BounceRates": "Tasa de rebote promedio",
    "ExitRates": "Tasa de salida promedio",
    "PageValues": "Valor de página promedio (Google Analytics)",
}

# Nombres cortos para el ticket
RECEIPT_LABELS = {
    "PageValues": "Valor de página", "ExitRates": "Tasa de salida", "BounceRates": "Tasa de rebote",
    "ProductRelated": "Páginas de producto", "ProductRelated_Duration": "Tiempo en productos",
    "Administrative": "Páginas de cuenta", "Administrative_Duration": "Tiempo en cuenta",
    "Informational": "Páginas informativas", "Informational_Duration": "Tiempo informativo",
    "SpecialDay": "Fecha especial", "Weekend": "Fin de semana",
}

PRESETS = {
    "Visita típica": None,  # se llena con los valores de referencia del entrenamiento
    "Alta intención": {
        "Administrative": 3, "Administrative_Duration": 80.0,
        "Informational": 1, "Informational_Duration": 30.0,
        "ProductRelated": 35, "ProductRelated_Duration": 1400.0,
        "BounceRates": 0.0, "ExitRates": 0.012, "PageValues": 40.0,
        "SpecialDay": 0.0, "Month": "Nov", "VisitorType": "New_Visitor", "Weekend": "False",
    },
    "Rebote rápido": {
        "Administrative": 0, "Administrative_Duration": 0.0,
        "Informational": 0, "Informational_Duration": 0.0,
        "ProductRelated": 2, "ProductRelated_Duration": 15.0,
        "BounceRates": 0.2, "ExitRates": 0.2, "PageValues": 0.0,
        "SpecialDay": 0.0, "Month": "May", "VisitorType": "Returning_Visitor", "Weekend": "False",
    },
}


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
@st.cache_resource
def load_artifact(path: Path) -> dict:
    return joblib.load(path)


def num(n: int) -> str:
    """Entero con separador de miles en formato colombiano: 12.330"""
    return f"{n:,}".replace(",", ".")


def dec(x: float, decimals: int = 2) -> str:
    """Decimal con coma: 0,93"""
    return f"{x:.{decimals}f}".replace(".", ",")


def pct(x: float, decimals: int = 1) -> str:
    return dec(x * 100, decimals) + " %"


def fmt_value(feature: str, value) -> str:
    if feature in DISPLAY:
        return DISPLAY[feature].get(str(value), str(value))
    if feature in RATE_FEATURES:
        return pct(float(value))
    if feature in INTEGER_FEATURES:
        return f"{int(value)}"
    if feature == "SpecialDay":
        return f"{float(value):.1f}".replace(".", ",")
    whole, frac = f"{float(value):.1f}".split(".")
    return f"{int(whole):,}".replace(",", ".") + "," + frac


def fmt_duration(seconds: float) -> str:
    seconds = float(seconds)
    if seconds < 60:
        return f"{seconds:.0f} s"
    if seconds < 3600:
        return f"{seconds / 60:.0f} min"
    return dec(seconds / 3600, 1) + " h"


def html(markup: str) -> None:
    st.markdown(compact(markup), unsafe_allow_html=True)


def section(title: str, subtitle: str = "", first: bool = False) -> None:
    cls = "section-title first" if first else "section-title"
    html(f'<div class="{cls}">{title}</div>')
    if subtitle:
        html(f'<div class="section-sub">{subtitle}</div>')


def subhead(text: str) -> None:
    html(f'<div class="subhead">{text}</div>')


def explain(text: str) -> None:
    html(f'<div class="explain">{text}</div>')


def chart(c) -> None:
    st.altair_chart(c, width="stretch", theme=None)


def panel(key: str):
    """Contenedor blanco con borde (estilo en ui/styles.py: st-key-panel*)."""
    return st.container(key=f"panel_{key}")


def explain_prediction(model, values: dict, features: list[str], reference: dict) -> pd.DataFrame:
    """Efecto de cada variable: probabilidad actual menos la probabilidad si esa
    variable tuviera el valor de una sesión típica (las demás quedan igual)."""
    base = pd.DataFrame([values], columns=features)
    variants = []
    for f in features:
        row = dict(values)
        row[f] = reference[f]
        variants.append(row)
    probs = model.predict_proba(pd.DataFrame(variants, columns=features))[:, 1]
    p = float(model.predict_proba(base)[0, 1])
    return pd.DataFrame({"variable": features, "puntos": (p - probs) * 100})


def build_receipt(artifact: dict, vals: dict, proba: float, contrib: pd.DataFrame, demo: bool = False) -> str:
    top = contrib.reindex(contrib["puntos"].abs().sort_values(ascending=False).index)
    top = top[top["puntos"].abs() >= 0.5].head(4)

    def short(f: str) -> str:
        if f == "Month":
            return f"Mes ({MONTH_LABELS.get(vals[f], vals[f])})"
        if f == "VisitorType":
            return f"Visitante {VISITOR_LABELS.get(vals[f], vals[f]).lower()}"
        return RECEIPT_LABELS[f]

    weekend = "fin de semana" if vals["Weekend"] == "True" else "entre semana"
    header = (f"{MONTH_LABELS.get(vals['Month'], vals['Month'])}, visitante "
              f"{VISITOR_LABELS.get(vals['VisitorType'], '').lower()}, {weekend}")
    items = [
        ("Páginas de producto", fmt_value("ProductRelated", vals["ProductRelated"])),
        ("Tiempo en productos", fmt_duration(vals["ProductRelated_Duration"])),
        ("Valor de página", fmt_value("PageValues", vals["PageValues"])),
        ("Tasa de salida", fmt_value("ExitRates", vals["ExitRates"])),
        ("Tasa de rebote", fmt_value("BounceRates", vals["BounceRates"])),
    ]
    effects = [(short(r["variable"]), float(r["puntos"])) for _, r in top.iterrows()]
    return receipt_html(proba, artifact.get("threshold", 0.5), header, items, effects, demo=demo)


@st.cache_data(show_spinner=False)
def demo_receipt(_artifact: dict) -> str:
    """Ticket de ejemplo para la portada, calculado con el modelo real."""
    vals = PRESETS["Alta intención"]
    features = _artifact["features"]
    proba = float(_artifact["model"].predict_proba(pd.DataFrame([vals], columns=features))[0, 1])
    contrib = explain_prediction(_artifact["model"], vals, features, _artifact["reference_values"])
    return build_receipt(_artifact, vals, proba, contrib, demo=True)


# ---------------------------------------------------------------------------
# Pestaña: Predicción
# ---------------------------------------------------------------------------
def numeric_input(feature: str, label: str, rng: dict):
    # El valor inicial viene de st.session_state (lo fija el caso de ejemplo elegido)
    if feature in INTEGER_FEATURES:
        return st.number_input(label, min_value=0, max_value=int(rng["max"]), step=1, key=feature)
    if feature in RATE_FEATURES:
        return st.slider(label, min_value=0.0, max_value=float(rng["max"]), step=0.001,
                         format="%.3f", key=feature)
    if feature == "SpecialDay":
        return st.select_slider(label, options=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0], key=feature)
    fmt = "%.1f" if feature == "PageValues" else "%.0f"
    return st.number_input(label, min_value=0.0, max_value=float(rng["max"]), step=10.0, format=fmt,
                           key=feature)


def render_prediction_tab(artifact: dict) -> None:
    model = artifact["model"]
    features = artifact["features"]
    categorical_features = artifact["categorical_features"]
    options = artifact["category_options"]
    ranges = artifact["numeric_ranges"]
    labels = {**artifact["feature_labels"], **FORM_LABELS}
    reference = artifact["reference_values"]
    threshold = artifact.get("threshold", 0.5)

    left, right = st.columns([1.2, 1], gap="large")

    with left, panel("form"):
        subhead("Describe la visita")
        explain("Empieza con un ejemplo y cambia lo que quieras. Los valores típicos son la mediana "
                "de las 12.330 visitas del dataset.")
        with st.container(key="presets"):
            preset_name = st.radio("Ejemplos", list(PRESETS), horizontal=True, key="preset_choice",
                                   label_visibility="collapsed")
        preset = PRESETS[preset_name] or {f: reference[f] for f in features}
        if st.session_state.get("_preset") != preset_name:
            for k, v in preset.items():
                st.session_state[k] = int(v) if k in INTEGER_FEATURES else (
                    float(v) if isinstance(v, (int, float)) else v
                )
            st.session_state["_preset"] = preset_name
            st.session_state.pop("resultado", None)

        values = {}
        with st.form("sesion", border=False):
            html('<div class="form-group first">Qué miró<span>Páginas visitadas y segundos en cada tipo</span></div>')
            c1, c2 = st.columns(2)
            for count_f, dur_f in [
                ("ProductRelated", "ProductRelated_Duration"),
                ("Administrative", "Administrative_Duration"),
                ("Informational", "Informational_Duration"),
            ]:
                with c1:
                    values[count_f] = numeric_input(count_f, labels[count_f], ranges[count_f])
                with c2:
                    values[dur_f] = numeric_input(dur_f, labels[dur_f], ranges[dur_f])

            html('<div class="form-group">Cómo se comportó<span>Métricas de Google Analytics de las '
                 'páginas que vio</span></div>')
            values["PageValues"] = numeric_input("PageValues", labels["PageValues"], ranges["PageValues"])
            c3, c4 = st.columns(2)
            with c3:
                values["BounceRates"] = numeric_input("BounceRates", labels["BounceRates"], ranges["BounceRates"])
            with c4:
                values["ExitRates"] = numeric_input("ExitRates", labels["ExitRates"], ranges["ExitRates"])

            html('<div class="form-group">Cuándo fue<span>Mes, tipo de visitante y fechas comerciales</span></div>')
            values["SpecialDay"] = numeric_input("SpecialDay", labels["SpecialDay"], ranges["SpecialDay"])
            c5, c6, c7 = st.columns(3)
            for col, f in zip([c5, c6, c7], categorical_features):
                with col:
                    values[f] = st.selectbox(
                        labels[f], options[f],
                        format_func=lambda x, f=f: DISPLAY.get(f, {}).get(x, x), key=f,
                    )

            submitted = st.form_submit_button("Calcular probabilidad", type="primary", width="stretch")

        if submitted:
            X_new = pd.DataFrame([values], columns=features)
            proba = float(model.predict_proba(X_new)[0, 1])
            contrib = explain_prediction(model, values, features, reference)
            st.session_state["resultado"] = {"proba": proba, "values": values,
                                             "contrib": contrib.to_dict("records")}

    result = st.session_state.get("resultado")
    with right, st.container(key="ticket"):
        if not result:
            html(empty_receipt_html())
            html(
                '<div class="advice"><div class="subhead">¿Qué hace esta herramienta?</div>'
                '<div class="explain">Una tienda online registra cómo navega cada visitante: qué '
                'páginas mira, cuánto tiempo se queda y si sale rápido. Con esos datos, el modelo '
                'estima la probabilidad de que la visita termine en compra.</div></div>'
            )
            return

        proba, vals = result["proba"], result["values"]
        html(build_receipt(artifact, vals, proba, pd.DataFrame(result["contrib"])))

        css = verdict(proba, threshold)[0]
        advice = {
            "v-yes": ("Qué haría una tienda", "Cuidar esta visita: pago sin fricción, envío claro y nada "
                      "que la distraiga. Gastar un cupón aquí suele ser innecesario."),
            "v-mid": ("Qué haría una tienda", "Esta es la visita que vale la pena empujar: un cupón, envío "
                      "gratis o el chat de ayuda pueden inclinar la decisión."),
            "v-no": ("Qué haría una tienda", "El comportamiento se parece al de quien se va sin comprar. "
                     "Un incentivo aquí rinde poco; mejor guardarlo para visitas en duda."),
        }[css]
        html(f'<div class="advice"><div class="subhead">{advice[0]}</div>'
             f'<div class="explain">{advice[1]}</div></div>')

    with panel("compare"):
        subhead("¿Se parece más a quien compra o a quien no?")
        explain("Cada línea compara esta visita con la mediana de quienes compraron y de quienes no, "
                "en las 12.330 visitas del dataset.")
        med = artifact["insights"]["medians_by_class"]
        hints = {
            "PageValues": "Más alto, más cerca de comprar",
            "ProductRelated": "Cuántos productos miró",
            "ProductRelated_Duration": "Tiempo total mirando productos",
            "ExitRates": "Más bajo, más cerca de comprar",
            "BounceRates": "Más bajo, más cerca de comprar",
        }
        rows = []
        for f, hint in hints.items():
            fmt = fmt_duration if f == "ProductRelated_Duration" else (lambda v, f=f: fmt_value(f, v))
            rows.append({
                "name": RECEIPT_LABELS[f], "hint": hint,
                "me": float(vals[f]), "buy": float(med[f]["compra"]), "nobuy": float(med[f]["no_compra"]),
                "me_txt": fmt(vals[f]), "buy_txt": fmt(med[f]["compra"]), "nobuy_txt": fmt(med[f]["no_compra"]),
            })
        html(compare_html(rows))

    with st.expander("¿Cómo se calcula «lo que movió la probabilidad»?"):
        st.markdown(
            "Para cada variable, la app cambia solo ese dato por el valor de una visita típica y mira "
            "cuánto cambia la probabilidad. Si al quitarlo la probabilidad baja, ese dato la estaba "
            "subiendo (verde); si sube, la estaba bajando (rosa). Es una aproximación: los efectos no "
            "suman exactamente el total porque el modelo combina variables entre sí."
        )


# ---------------------------------------------------------------------------
# Pestaña: Datos
# ---------------------------------------------------------------------------
def render_data_tab(artifact: dict) -> None:
    ins = artifact["insights"]

    section(
        "Los datos",
        "Online Shoppers Purchasing Intention Dataset (Sakar et al., 2019, repositorio UCI): un año de "
        "visitas a una tienda online real, con datos anónimos de Google Analytics.",
        first=True,
    )
    c1, c2 = st.columns([1.1, 1], gap="large")
    with c1, panel("waffle"):
        per_100 = round(ins["positive_rate"] * 100)
        html(f'<div class="big-fact">De cada 100 visitas, solo {per_100} terminan en compra.</div>')
        html(waffle_html(ins["positive_rate"]))
        explain(f"Cada cuadro representa unas {round(ins['n_rows'] / 200)} visitas; los verdes "
                f"compraron. En total, {num(ins['class_counts']['Compra'])} de {num(ins['n_rows'])}.")
    with c2:
        subhead("¿Para qué sirven estos datos?")
        html(
            '<div class="prose">Si una tienda sabe <b>durante la visita</b> qué tan probable es que '
            "alguien compre, puede actuar a tiempo: mostrar un cupón a quien duda, ofrecer ayuda por "
            "chat o no gastar publicidad en quien solo está mirando.</div>"
        )
        explain("Como casi nadie compra, un modelo que siempre diga «no compra» acertaría el "
                f"{pct(1 - ins['positive_rate'])} de las veces y no serviría para nada. Por eso el "
                "modelo se mide con recall, F1 y ROC-AUC.")
        html(facts_html([
            ("visitas, una por fila", num(ins["n_rows"])),
            ("columnas; 13 entran al modelo", f"{ins['n_cols']}"),
            ("datos faltantes", f"{ins['missing_values']}"),
            ("meses con visitas (no hay enero ni abril)", "10"),
        ]))

    section("Qué separa a quien compra de quien no",
            "Tasa de compra según cada variable. La barra más oscura marca dónde se compra más.")
    c3, c4 = st.columns(2, gap="large")
    with c3, panel("pagevalues"):
        subhead("El valor de página es la señal más fuerte")
        chart(charts.rate_bar_chart(ins["rate_by_pagevalues"], "rango", "Valor de página promedio"))
        explain("Con valor 0 compra el <b>4 %</b>; por encima de 50, el <b>81 %</b>. Google Analytics le "
                "da valor a una página cuando suele aparecer antes de una compra.")
    with c4, panel("exit"):
        subhead("Quien sale rápido, no compra")
        chart(charts.rate_bar_chart(ins["rate_by_exitrates"], "rango", "Tasa de salida promedio"))
        explain("La tasa de salida dice qué tan seguido una página es la última de la visita. "
                "Con tasas bajas compra el 27 %; con tasas altas, menos del 1 %.")

    c5, c6 = st.columns(2, gap="large")
    with c5, panel("products"):
        subhead("Mirar más productos ayuda")
        chart(charts.rate_bar_chart(ins["rate_by_productrelated"], "rango", "Páginas de producto visitadas"))
        explain("Quien ve 5 productos o menos compra el 4 % de las veces; quien ve más de 60, el 26 %.")
    with c6, panel("month"):
        subhead("Noviembre es el mejor mes")
        chart(charts.rate_bar_chart(ins["rate_by_month"], "categoria", "Mes", labels=MONTH_SHORT))
        explain("Noviembre llega al 25 %, seguramente por los descuentos de fin de año. Febrero, al 2 %.")

    c7, c8 = st.columns(2, gap="large")
    with c7, panel("visitor"):
        subhead("Los visitantes nuevos compran más")
        chart(charts.rate_bar_chart(ins["rate_by_visitor"], "categoria", "Tipo de visitante",
                                    horizontal=True, labels=VISITOR_LABELS))
        explain("Muchos recurrentes vuelven a comparar o revisar sin intención de comprar ese día.")
    with c8, panel("weekend"):
        subhead("El fin de semana cambia poco")
        chart(charts.rate_bar_chart(ins["rate_by_weekend"], "categoria", "¿Fin de semana?",
                                    horizontal=True, labels=WEEKEND_LABELS, highlight_max=False))
        explain("17 % frente a 15 %. Por eso esta variable casi no pesa en el modelo.")

    section("Diccionario de variables", "Qué mide cada columna y cuáles usa el modelo.")
    with panel("dict"):
        rows = "".join(
            f"<tr><td><code>{name}</code></td><td>{desc}</td><td>{tipo}</td>"
            f'<td><span class="tag tag-{"yes" if uso == "Sí" else "no" if uso == "No" else "target"}">'
            f"{uso}</span></td></tr>"
            for name, desc, tipo, uso in VARIABLE_DICTIONARY
        )
        html('<table class="dict"><thead><tr><th>Columna</th><th>Qué mide</th><th>Tipo</th>'
             f"<th>¿Entra al modelo?</th></tr></thead><tbody>{rows}</tbody></table>")
    explain(
        "<b>¿Por qué se descartan cuatro variables?</b> Sistema operativo, navegador, región y fuente de "
        "tráfico vienen como códigos sin nombre (1, 2, 3…). Nadie podría llenarlos con sentido en la app, "
        "y tratarlos como números haría creer al modelo que el navegador 8 es «mayor» que el 2."
    )


# ---------------------------------------------------------------------------
# Pestaña: Modelo
# ---------------------------------------------------------------------------
def render_model_tab(artifact: dict) -> None:
    ins = artifact["insights"]
    m = artifact["metrics"]
    labels = artifact["feature_labels"]
    cm = m["confusion_matrix"]
    fp, fn, tp = cm[0][1], cm[1][0], cm[1][1]

    section("Cómo funciona el modelo",
            f"Un random forest entrenado con {num(ins['train_size'])} visitas y evaluado con "
            f"{num(ins['test_size'])} que nunca vio.", first=True)
    html(
        '<div class="prose">Un <b>random forest</b> es un grupo de 300 árboles de decisión. Cada árbol '
        "aprende reglas sencillas, como <i>«si el valor de página pasa de 5 y la tasa de salida es baja, "
        "probablemente compra»</i>, a partir de una muestra distinta de los datos. Para una visita nueva, "
        "cada árbol da su estimación y el modelo las promedia. Ese promedio es la probabilidad del ticket.</div>"
    )
    subhead("<br>Del dato a la probabilidad")
    html(steps_html([
        ("Datos de la visita", "13 variables"),
        ("Rellenar faltantes", "mediana o moda"),
        ("Escala logarítmica", "duraciones y conteos"),
        ("Estandarizar", "media 0, desviación 1"),
        ("One-hot", "mes, visitante, fin de semana"),
        ("Random forest", "300 árboles"),
        ("Probabilidad", "de 0 % a 100 %"),
    ]))
    explain(
        "Todos los pasos viven en un mismo <b>Pipeline</b> de scikit-learn guardado en "
        "<code>model.joblib</code>, así que cada visita nueva se transforma igual que en el entrenamiento. "
        "Con <code>class_weight=\"balanced\"</code>, las compras pesan lo mismo que las no compras aunque "
        "sean pocas."
    )

    section("¿Qué tan bien funciona?", f"Resultados en las {num(ins['test_size'])} visitas de prueba.")
    html(scoreboard_html([
        ("ROC-AUC", dec(m["roc_auc"], 3),
         "En 93 de cada 100 parejas comprador / no comprador, le da más probabilidad al comprador"),
        ("Recall de compra", pct(m["recall_compra"], 0),
         f"Encuentra {num(tp)} de las {num(tp + fn)} visitas que sí compraron"),
        ("Precisión de compra", pct(m["precision_compra"], 0),
         f"De {num(tp + fp)} visitas que marcó como compra, {num(tp)} compraron"),
        ("F1 de compra", dec(m["f1_compra"]), "Equilibrio entre recall y precisión, de 0 a 1"),
    ]))

    c1, c2 = st.columns([1, 1.2], gap="large")
    with c1, panel("confusion"):
        subhead("Matriz de confusión")
        chart(charts.confusion_chart(cm))
        explain(
            f"<b>Verde = aciertos, rosa = errores.</b> Se le escaparon {num(fn)} compradores y dio "
            f"{num(fp)} falsas alarmas. Para un incentivo, una falsa alarma cuesta poco (un cupón de más); "
            "perder un comprador cuesta más. Por eso el modelo prioriza el recall."
        )
    with c2, panel("hist"):
        subhead("¿Separa bien a quien compra de quien no?")
        chart(charts.proba_hist_chart(ins["proba_hist"]))
        explain("Las visitas sin compra (gris) se amontonan cerca de 0 %; las que compraron (verde) se "
                "reparten hacia la derecha. La línea punteada es el umbral de 50 %.")

    c3, c4 = st.columns(2, gap="large")
    with c3, panel("roc"):
        subhead("Curva ROC")
        chart(charts.curve_chart(ins["roc_curve"], "Falsas alarmas", "Compradores encontrados", diagonal=True))
        explain("Cuanto más se pega la curva a la esquina superior izquierda, mejor. La diagonal es un "
                f"modelo que adivina al azar. El área bajo la curva es {dec(m['roc_auc'], 3)}.")
    with c4, panel("pr"):
        subhead("Curva precisión–recall")
        chart(charts.curve_chart(ins["pr_curve"], "Recall", "Precisión", diagonal=False,
                                 baseline=ins["positive_rate"]))
        explain(f"Más exigente cuando hay pocas compras. La línea punteada ({pct(ins['positive_rate'])}) "
                f"es un modelo al azar; el área bajo la curva es {dec(m['pr_auc'], 3)}, casi cinco veces más.")

    section("¿Qué variables usa más?")
    c5, c6 = st.columns([1.35, 1], gap="large")
    with c5, panel("importance"):
        chart(charts.importance_chart(ins["permutation_importance"], labels))
    with c6:
        explain(
            "<b>Importancia por permutación:</b> se desordena una variable al azar en los datos de prueba y "
            "se mide cuánto empeora el ROC-AUC. Si empeora mucho, el modelo dependía de ella."
            "<br><br>El <b>valor de página</b> domina, seguido del <b>mes</b>. Sin el valor de página, el "
            f"ROC-AUC cae de {dec(m['roc_auc'])} a {dec(ins['roc_auc_without_pagevalues'])}. Se conserva "
            "porque Google Analytics lo calcula con el historial de la tienda y está disponible mientras la "
            "persona navega."
        )

    section("¿Por qué random forest?", "Se compararon dos modelos con validación cruzada de 5 pliegues.")
    c7, c8 = st.columns([1.35, 1], gap="large")
    with c7, panel("comparison"):
        chart(charts.model_comparison_chart(ins["model_comparison"], MODEL_NAMES))
    with c8:
        comp = ins["model_comparison"]
        explain(
            "La <b>regresión logística</b> suma el efecto de cada variable por separado. El "
            "<b>random forest</b> además capta combinaciones, como «muchas páginas de producto <i>y</i> "
            "salida baja»."
            f"<br><br>En validación cruzada, el random forest obtuvo un F1 de {dec(comp['random_forest']['cv_f1'], 3)} "
            f"frente a {dec(comp['logistic_regression']['cv_f1'], 3)}. En prueba, recall y F1 son casi "
            "iguales, pero el random forest ordena mejor las visitas: PR-AUC "
            f"{dec(comp['random_forest']['pr_auc'])} frente a {dec(comp['logistic_regression']['pr_auc'])}."
        )

    section("Limitaciones")
    html(
        '<div class="prose"><ul>'
        "<li>Los datos vienen de <b>una sola tienda</b> durante un año; otra tienda podría comportarse distinto.</li>"
        "<li>El modelo depende mucho del <b>valor de página</b>, que requiere tener Google Analytics configurado.</li>"
        "<li>El umbral de 50 % es una elección: una tienda que quiera menos falsas alarmas podría subirlo.</li>"
        "<li>«Lo que movió la probabilidad» es una aproximación: cambia una variable a la vez.</li>"
        "</ul></div>"
    )


# ---------------------------------------------------------------------------
# Pestaña: Proyecto
# ---------------------------------------------------------------------------
def render_project_tab(artifact: dict) -> None:
    section("Sobre el proyecto",
            "Reto de Machine Learning: una solución pequeña pero completa, del dataset al despliegue, "
            "que otra persona pueda reproducir.", first=True)

    subhead("¿Para qué le serviría a una tienda?")
    html(uses_html([
        ("tag", "Incentivos a tiempo",
         "Mostrar un cupón o envío gratis solo a las visitas que dudan, en lugar de regalar descuentos a todos."),
        ("chat", "Ayuda en el momento justo",
         "Abrir el chat de soporte cuando una visita con alta probabilidad empieza a mostrar señales de salida."),
        ("chart", "Medir campañas",
         "Comparar la probabilidad promedio de las visitas de cada campaña para saber cuál trae compradores."),
    ]))

    subhead("<br>Cómo se construyó")
    html(steps_html([
        ("Dataset", "CSV público"),
        ("Google Colab", "exploración"),
        ("train.py", "entrena y evalúa"),
        ("model.joblib", "modelo y metadatos"),
        ("app.py", "esta interfaz"),
        ("GitHub", "código versionado"),
        ("Docker", "imagen reproducible"),
        ("Nube", "app pública"),
    ]))
    explain(
        "<b>train.py</b> se ejecuta una vez y guarda el modelo. <b>app.py</b> solo lo carga: nunca vuelve "
        "a entrenar. El <b>Dockerfile</b> empaqueta Python, las librerías con versiones fijas, la app y el "
        "modelo en una imagen que corre igual en cualquier computador."
    )

    subhead("<br>Reproducirlo en tu computador")
    st.code(
        f"git clone {REPO_URL}.git\n"
        "cd intencion-compra-streamlit\n"
        "docker build -t intencion-compra-app .\n"
        "docker run -p 8501:8501 intencion-compra-app\n"
        "# Abrir http://localhost:8501",
        language="bash",
    )
    explain(f'Código e instrucciones en <a href="{REPO_URL}" target="_blank">GitHub</a>.')


# ---------------------------------------------------------------------------
# Página
# ---------------------------------------------------------------------------
def main() -> None:
    st.set_page_config(page_title="Intención de compra", page_icon="🛒", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)

    if not MODEL_PATH.exists():
        st.error("No se encontró model.joblib. Ejecute primero: python train.py")
        st.stop()
    artifact = load_artifact(MODEL_PATH)

    html(topbar_html(REPO_URL))
    html(hero_html(num(artifact["insights"]["n_rows"]), dec(artifact["metrics"]["roc_auc"]),
                   demo_receipt(artifact)))

    tab_pred, tab_data, tab_model, tab_project = st.tabs(
        ["Predicción", "Los datos", "El modelo", "El proyecto"]
    )
    with tab_pred:
        render_prediction_tab(artifact)
    with tab_data:
        render_data_tab(artifact)
    with tab_model:
        render_model_tab(artifact)
    with tab_project:
        render_project_tab(artifact)

    html(f"""
    <footer class="footer">
      <div><b>Intención de compra</b><br>Por Allison Loango y Angie Loango.<br>
      Proyecto de Ciencia de Datos, Universidad Externado de Colombia.</div>
      <div>Datos: Sakar et al. (2019), Online Shoppers Purchasing Intention Dataset, repositorio UCI.<br>
      <a href="{REPO_URL}" target="_blank" rel="noopener">Ver el código en GitHub</a></div>
    </footer>
    """)


if __name__ == "__main__":
    main()
