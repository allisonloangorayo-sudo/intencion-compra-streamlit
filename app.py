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

PRESETS = {
    "Sesión típica": None,  # se llena con los valores de referencia del entrenamiento
    "Sesión con alta intención": {
        "Administrative": 3, "Administrative_Duration": 80.0,
        "Informational": 1, "Informational_Duration": 30.0,
        "ProductRelated": 35, "ProductRelated_Duration": 1400.0,
        "BounceRates": 0.0, "ExitRates": 0.012, "PageValues": 40.0,
        "SpecialDay": 0.0, "Month": "Nov", "VisitorType": "New_Visitor", "Weekend": "False",
    },
    "Sesión de rebote rápido": {
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


def kpi(label: str, value: str, note: str = "") -> str:
    note_html = f'<div class="kpi-note">{note}</div>' if note else ""
    return f'<div class="card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{note_html}</div>'


def section(title: str, subtitle: str = "") -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-sub">{subtitle}</div>', unsafe_allow_html=True)


def subhead(text: str) -> None:
    st.markdown(f'<div class="subhead">{text}</div>', unsafe_allow_html=True)


def explain(text: str) -> None:
    st.markdown(f'<div class="explain">{text}</div>', unsafe_allow_html=True)


def chart(c) -> None:
    st.altair_chart(c, width="stretch", theme=None)


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
    return st.number_input(label, min_value=0.0, max_value=float(rng["max"]), step=10.0, key=feature)


def render_prediction_tab(artifact: dict) -> None:
    model = artifact["model"]
    features = artifact["features"]
    numeric_features = artifact["numeric_features"]
    categorical_features = artifact["categorical_features"]
    options = artifact["category_options"]
    ranges = artifact["numeric_ranges"]
    labels = artifact["feature_labels"]
    reference = artifact["reference_values"]
    threshold = artifact.get("threshold", 0.5)

    left, right = st.columns([1.05, 1], gap="large")

    with left:
        preset_name = st.selectbox(
            "Empieza con un caso de ejemplo", list(PRESETS),
            help="Llena el formulario con valores de ejemplo. Después puedes cambiar cualquier campo.",
        )
        preset = PRESETS[preset_name] or {f: reference[f] for f in features}
        if st.session_state.get("_preset") != preset_name:
            for k, v in preset.items():
                st.session_state[k] = int(v) if k in INTEGER_FEATURES else (
                    float(v) if isinstance(v, (int, float)) else v
                )
            st.session_state["_preset"] = preset_name
            st.session_state.pop("resultado", None)

        values = {}
        with st.form("sesion"):
            st.markdown('<div class="form-group">Navegación</div>', unsafe_allow_html=True)
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

            st.markdown('<div class="form-group">Comportamiento en las páginas</div>', unsafe_allow_html=True)
            values["PageValues"] = numeric_input("PageValues", labels["PageValues"], ranges["PageValues"])
            c3, c4 = st.columns(2)
            with c3:
                values["BounceRates"] = numeric_input("BounceRates", labels["BounceRates"], ranges["BounceRates"])
            with c4:
                values["ExitRates"] = numeric_input("ExitRates", labels["ExitRates"], ranges["ExitRates"])

            st.markdown('<div class="form-group">Contexto de la visita</div>', unsafe_allow_html=True)
            values["SpecialDay"] = numeric_input("SpecialDay", labels["SpecialDay"], ranges["SpecialDay"])
            c5, c6, c7 = st.columns(3)
            for col, f in zip([c5, c6, c7], categorical_features):
                with col:
                    values[f] = st.selectbox(
                        labels[f], options[f],
                        format_func=lambda x, f=f: DISPLAY.get(f, {}).get(x, x), key=f,
                    )

            submitted = st.form_submit_button("Calcular probabilidad", type="primary",
                                              width="stretch")

        if submitted:
            X_new = pd.DataFrame([values], columns=features)
            proba = float(model.predict_proba(X_new)[0, 1])
            contrib = explain_prediction(model, values, features, reference)
            st.session_state["resultado"] = {"proba": proba, "values": values,
                                             "contrib": contrib.to_dict("records")}

    with right:
        result = st.session_state.get("resultado")
        if not result:
            st.markdown(
                '<div class="empty-state"><div style="font-size:2rem">🛒</div>'
                '<div style="font-weight:600;color:#1d1d1f;margin:.4rem 0">Aquí verás el resultado</div>'
                'Elige un caso de ejemplo o cambia los datos de la sesión y pulsa '
                '<b>Calcular probabilidad</b>.</div>',
                unsafe_allow_html=True,
            )
            explain(
                "<br><b>¿Qué hace esta herramienta?</b> Una tienda online registra cómo navega cada "
                "visitante: qué páginas mira, cuánto tiempo se queda y si sale rápido. Con esos datos, "
                "el modelo estima la probabilidad de que la visita termine en una compra."
            )
            return

        proba = result["proba"]
        pred = int(proba >= threshold)
        st.markdown(charts.gauge_svg(proba), unsafe_allow_html=True)
        st.markdown('<div class="result-label">Probabilidad de compra estimada</div>', unsafe_allow_html=True)

        if pred == 1:
            pill = '<span class="pill pill-yes">Clasificación: compra</span>'
            msg = ("Supera el umbral de 50 %. El modelo espera que esta sesión <b>termine en compra</b>. "
                   "Para una tienda, es una visita a cuidar: facilitar el pago y evitar distracciones.")
        elif proba >= 0.25:
            pill = '<span class="pill pill-mid">Clasificación: no compra (zona de duda)</span>'
            msg = ("Está por debajo del umbral, pero lejos de cero. Es el tipo de visita donde "
                   "un incentivo (cupón, envío gratis, chat de ayuda) podría inclinar la decisión.")
        else:
            pill = '<span class="pill pill-no">Clasificación: no compra</span>'
            msg = ("La probabilidad es baja: el comportamiento se parece al de visitas que se van sin "
                   "comprar. Gastar incentivos aquí suele rendir poco.")
        st.markdown(f'<div style="text-align:center;margin:.8rem 0 .6rem">{pill}</div>', unsafe_allow_html=True)
        explain(msg)

        subhead("¿Por qué este resultado?")
        contrib = pd.DataFrame(result["contrib"])
        contrib["etiqueta"] = contrib["variable"].map(lambda v: labels.get(v, v))
        top = contrib.reindex(contrib["puntos"].abs().sort_values(ascending=False).index)
        top = top[top["puntos"].abs() >= 0.5].head(6)
        if top.empty:
            explain("Todas las variables tienen valores muy parecidos a los de una sesión típica, "
                    "por eso ninguna mueve la probabilidad de forma notable.")
        else:
            chart(charts.contributions_chart(top[["etiqueta", "puntos"]]))
            lines = []
            for _, r in top.head(3).iterrows():
                f = r["variable"]
                verb = "sube" if r["puntos"] > 0 else "baja"
                lines.append(
                    f"• <b>{labels[f]}</b>: {fmt_value(f, result['values'][f])} "
                    f"(en una sesión típica: {fmt_value(f, reference[f])}) → {verb} la probabilidad "
                    f"{dec(abs(r['puntos']), 1)} puntos."
                )
            explain("<br>".join(lines))
            explain(
                "<br><b>Cómo leer esta gráfica:</b> para cada variable, la app cambia solo ese dato por el "
                "valor de una sesión típica y mira cuánto cambia la probabilidad. Las barras verdes "
                "empujan hacia la compra y las rojas en contra. Es una aproximación: los efectos no "
                "suman exactamente el total porque el modelo combina variables entre sí."
            )

        with st.expander("Comparar con compradores y no compradores reales"):
            med = artifact["insights"]["medians_by_class"]
            key_vars = ["PageValues", "ProductRelated", "ProductRelated_Duration", "ExitRates", "BounceRates"]
            table = pd.DataFrame({
                "Variable": [labels[f] for f in key_vars],
                "Esta sesión": [fmt_value(f, result["values"][f]) for f in key_vars],
                "Comprador típico": [fmt_value(f, med[f]["compra"]) for f in key_vars],
                "No comprador típico": [fmt_value(f, med[f]["no_compra"]) for f in key_vars],
            })
            st.dataframe(table, hide_index=True, width="stretch")
            explain("Valores medianos de las 12.330 sesiones del dataset, separadas según si compraron o no.")


# ---------------------------------------------------------------------------
# Pestaña: Datos
# ---------------------------------------------------------------------------
def render_data_tab(artifact: dict) -> None:
    ins = artifact["insights"]

    section(
        "Los datos",
        "Online Shoppers Purchasing Intention Dataset (Sakar et al., 2019, repositorio UCI). "
        "Registra un año de visitas a una tienda online real, con datos anónimos de Google Analytics.",
    )
    cols = st.columns(4)
    cards = [
        ("Sesiones", num(ins["n_rows"]), "Cada fila es una visita de un usuario distinto"),
        ("Terminaron en compra", pct(ins["positive_rate"]), "Clase minoritaria: el reto del problema"),
        ("Variables", f"{ins['n_cols'] - 1}", "13 entran al modelo, 4 se descartan"),
        ("Datos faltantes", f"{ins['missing_values']}", "No hubo que rellenar valores"),
    ]
    for col, (label, value, note) in zip(cols, cards):
        col.markdown(kpi(label, value, note), unsafe_allow_html=True)

    section("¿Para qué sirven estos datos?")
    st.markdown(
        "La mayoría de visitas a una tienda online terminan sin compra. Si una tienda sabe "
        "**durante la visita** qué tan probable es que alguien compre, puede actuar a tiempo: "
        "mostrar un cupón a quien duda, ofrecer ayuda por chat o no gastar publicidad en quien solo "
        "está mirando. Estos datos permiten aprender ese patrón a partir de miles de visitas pasadas."
    )

    c1, c2 = st.columns([1, 1.4], gap="large")
    with c1:
        subhead("Pocas visitas compran")
        chart(charts.donut_chart(ins["class_counts"]))
        explain(
            f"De {num(ins['n_rows'])} sesiones, solo {num(ins['class_counts']['Compra'])} terminaron en "
            "compra. Por eso no sirve medir el modelo solo con <b>accuracy</b>: un modelo que siempre "
            f"diga \"no compra\" acertaría el {pct(1 - ins['positive_rate'])} de las veces y no serviría "
            "para nada."
        )
    with c2:
        subhead("El valor de página es la señal más fuerte")
        chart(charts.rate_bar_chart(ins["rate_by_pagevalues"], "rango", "Valor de página promedio",
                                    highlight_max=True))
        explain(
            "Cuando las páginas visitadas tienen valor 0, solo compra el <b>4 %</b>. Cuando superan 50, "
            "compra el <b>81 %</b>. Google Analytics le da valor a una página cuando suele aparecer "
            "antes de una compra en el historial de la tienda."
        )

    c3, c4 = st.columns(2, gap="large")
    with c3:
        subhead("Quien sale rápido, no compra")
        chart(charts.rate_bar_chart(ins["rate_by_exitrates"], "rango", "Tasa de salida promedio"))
        explain(
            "La tasa de salida indica qué tan seguido una página es la última de la visita. "
            "Con tasas bajas compra el 27 %; con tasas altas, menos del 1 %."
        )
    with c4:
        subhead("Mirar más productos ayuda")
        chart(charts.rate_bar_chart(ins["rate_by_productrelated"], "rango", "Páginas de producto visitadas"))
        explain(
            "Quien ve 5 productos o menos compra el 4 % de las veces; quien ve más de 60, el 26 %. "
            "Explorar el catálogo es señal de interés."
        )

    subhead("Noviembre es el mejor mes")
    chart(charts.rate_bar_chart(ins["rate_by_month"], "categoria", "Mes", highlight_max=True,
                                labels=MONTH_SHORT))
    explain(
        "Noviembre tiene la tasa de compra más alta (25 %), seguramente por las temporadas de descuentos "
        "de fin de año. Febrero es el más bajo (2 %). El dataset no tiene visitas de enero ni abril."
    )

    c5, c6 = st.columns(2, gap="large")
    with c5:
        subhead("Los visitantes nuevos compran más")
        chart(charts.rate_bar_chart(ins["rate_by_visitor"], "categoria", "Tipo de visitante",
                                    horizontal=True, labels=VISITOR_LABELS))
        explain(
            "Los nuevos compran el 25 % de las veces y los recurrentes el 14 %. Muchos recurrentes "
            "vuelven a comparar o revisar sin intención de compra inmediata."
        )
    with c6:
        subhead("El fin de semana cambia poco")
        chart(charts.rate_bar_chart(ins["rate_by_weekend"], "categoria", "¿Fin de semana?",
                                    horizontal=True, labels=WEEKEND_LABELS))
        explain("La diferencia es pequeña (17 % frente a 15 %). Por eso esta variable pesa poco en el modelo.")

    section("Diccionario de variables", "Qué mide cada columna del dataset y cuáles usa el modelo.")
    rows = "".join(
        f"<tr><td><code>{name}</code></td><td>{desc}</td><td>{tipo}</td>"
        f'<td><span class="tag tag-{"yes" if uso == "Sí" else "no" if uso == "No" else "target"}">{uso}</span></td></tr>'
        for name, desc, tipo, uso in VARIABLE_DICTIONARY
    )
    st.markdown(
        '<table class="dict"><thead><tr><th>Columna</th><th>Qué mide</th><th>Tipo</th>'
        f"<th>¿Entra al modelo?</th></tr></thead><tbody>{rows}</tbody></table>",
        unsafe_allow_html=True,
    )
    explain(
        "<b>¿Por qué se descartan cuatro variables?</b> Sistema operativo, navegador, región y fuente de "
        "tráfico vienen como códigos numéricos sin nombre (1, 2, 3…). Nadie podría llenarlos con sentido "
        "en la app, y tratarlos como números haría creer al modelo que el navegador 8 es \"mayor\" que el 2."
    )


# ---------------------------------------------------------------------------
# Pestaña: Modelo
# ---------------------------------------------------------------------------
def render_model_tab(artifact: dict) -> None:
    ins = artifact["insights"]
    m = artifact["metrics"]
    labels = artifact["feature_labels"]
    cm = m["confusion_matrix"]
    tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]

    section(
        "Cómo funciona el modelo",
        "Un random forest entrenado con 9.864 sesiones y evaluado con 2.466 sesiones que nunca vio.",
    )
    st.markdown(
        "Un **random forest** es un conjunto de 300 árboles de decisión. Cada árbol aprende reglas "
        "sencillas del tipo *\"si el valor de página es mayor que 5 y la tasa de salida es baja, "
        "probablemente compra\"*, usando una muestra distinta de los datos. Para una sesión nueva, "
        "cada árbol da su estimación y el modelo promedia las 300. Ese promedio es la probabilidad "
        "que ves en la pestaña de predicción."
    )

    subhead("Del dato crudo a la probabilidad")
    steps = [
        ("Datos de la sesión", "13 variables"),
        ("Rellenar faltantes", "mediana / moda"),
        ("Escala logarítmica", "duraciones y conteos"),
        ("Estandarizar", "media 0, desviación 1"),
        ("One-hot", "mes, visitante, fin de semana"),
        ("Random forest", "300 árboles"),
        ("Probabilidad", "0 % a 100 %"),
    ]
    flow = '<span class="flow-arrow">→</span>'.join(
        f'<div class="flow-step">{a}<small>{b}</small></div>' for a, b in steps
    )
    st.markdown(f'<div class="flow">{flow}</div>', unsafe_allow_html=True)
    explain(
        "Todos estos pasos viven dentro de un mismo <b>Pipeline</b> de scikit-learn guardado en "
        "<code>model.joblib</code>. Así, la app transforma cada caso nuevo exactamente igual que en el "
        "entrenamiento. El modelo usa <code>class_weight=\"balanced\"</code> para que las compras, "
        "aunque sean pocas, pesen lo mismo que las no compras."
    )

    section("¿Qué tan bien funciona?", "Resultados en las 2.466 sesiones de prueba, que el modelo nunca vio.")
    cols = st.columns(4)
    cards = [
        ("ROC-AUC", dec(m["roc_auc"], 3),
         "Si tomas un comprador y un no comprador al azar, el 93 % de las veces el modelo le da más probabilidad al comprador"),
        ("Recall de compra", pct(m["recall_compra"], 0),
         f"Detecta {num(tp)} de las {num(tp + fn)} sesiones que sí compraron"),
        ("Precisión de compra", pct(m["precision_compra"], 0),
         f"De {num(tp + fp)} sesiones que marcó como compra, {num(tp)} compraron"),
        ("F1 de compra", dec(m["f1_compra"]),
         "Balance entre recall y precisión, de 0 a 1"),
    ]
    for col, (label, value, note) in zip(cols, cards):
        col.markdown(kpi(label, value, note), unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1.15], gap="large")
    with c1:
        subhead("Matriz de confusión")
        chart(charts.confusion_chart(cm))
        explain(
            f"<b>Azul = aciertos, rosado = errores.</b> El modelo acertó {num(tn)} sesiones sin compra y "
            f"{num(tp)} con compra. Se le escaparon {num(fn)} compradores y dio {num(fp)} falsas alarmas. "
            "Para un incentivo de marketing, una falsa alarma cuesta poco (un cupón de más); "
            "perder a un comprador cuesta más. Por eso el modelo prioriza el recall."
        )
    with c2:
        subhead("¿Separa bien a compradores de no compradores?")
        chart(charts.proba_hist_chart(ins["proba_hist"]))
        explain(
            "Cada barra cuenta sesiones de prueba según la probabilidad que les dio el modelo. "
            "Las grises (no compraron) se amontonan cerca de 0 %; las azules (compraron) se reparten "
            "hacia la derecha. La línea punteada es el umbral de 50 %."
        )

    c3, c4 = st.columns(2, gap="large")
    with c3:
        subhead("Curva ROC")
        chart(charts.curve_chart(ins["roc_curve"], "Falsas alarmas (tasa de falsos positivos)",
                                 "Compradores detectados (recall)", diagonal=True))
        explain(
            "Muestra qué pasa al mover el umbral. Cuanto más se pega la curva a la esquina superior "
            "izquierda, mejor. La diagonal punteada es un modelo que adivina al azar. "
            f"El área bajo la curva es el ROC-AUC: {dec(m['roc_auc'], 3)}."
        )
    with c4:
        subhead("Curva precisión–recall")
        chart(charts.curve_chart(ins["pr_curve"], "Recall", "Precisión", diagonal=False,
                                 baseline=ins["positive_rate"]))
        explain(
            f"Es más exigente con clases desbalanceadas. La línea punteada ({pct(ins['positive_rate'])}) "
            "es la precisión de un modelo al azar. El área bajo la curva (PR-AUC) es "
            f"{dec(m['pr_auc'], 3)}, casi cinco veces esa línea base."
        )

    section("¿Qué variables usa más el modelo?")
    c5, c6 = st.columns([1.3, 1], gap="large")
    with c5:
        chart(charts.importance_chart(ins["permutation_importance"], labels))
    with c6:
        explain(
            "<b>Importancia por permutación:</b> se desordena una variable al azar en los datos de prueba "
            "y se mide cuánto empeora el ROC-AUC. Si el modelo empeora mucho, dependía de esa variable."
            "<br><br>El <b>valor de página</b> domina, seguido del <b>mes</b>. Sin el valor de página, el "
            f"ROC-AUC cae de {dec(m['roc_auc'])} a {dec(ins['roc_auc_without_pagevalues'])}. "
            "Se conserva porque Google Analytics lo calcula con el historial de toda la tienda y está "
            "disponible mientras la persona navega."
        )

    section("¿Por qué random forest?", "Se compararon dos modelos con validación cruzada de 5 pliegues.")
    c7, c8 = st.columns([1.3, 1], gap="large")
    with c7:
        chart(charts.model_comparison_chart(ins["model_comparison"], MODEL_NAMES))
    with c8:
        comp = ins["model_comparison"]
        explain(
            "La <b>regresión logística</b> suma el efecto de cada variable por separado. El "
            "<b>random forest</b> además capta combinaciones, como \"muchas páginas de producto <i>y</i> "
            "salida baja\"."
            "<br><br>En validación cruzada, el random forest obtuvo un F1 de "
            f"{dec(comp['random_forest']['cv_f1'], 3)} frente a {dec(comp['logistic_regression']['cv_f1'], 3)}. "
            "En prueba, los dos tienen recall y F1 casi iguales, pero el random forest ordena mejor las "
            f"sesiones: PR-AUC {dec(comp['random_forest']['pr_auc'])} frente a "
            f"{dec(comp['logistic_regression']['pr_auc'])}."
        )

    section("Limitaciones")
    st.markdown(
        "- Los datos vienen de **una sola tienda** durante un año; otra tienda podría comportarse distinto.\n"
        "- El modelo depende mucho del **valor de página**, que requiere tener Google Analytics configurado.\n"
        "- El umbral de 50 % es una elección: una tienda que quiera menos falsas alarmas podría subirlo.\n"
        "- La explicación de cada predicción es una aproximación (cambia una variable a la vez)."
    )


# ---------------------------------------------------------------------------
# Pestaña: Proyecto
# ---------------------------------------------------------------------------
def render_project_tab(artifact: dict) -> None:
    section(
        "Sobre el proyecto",
        "Reto de Machine Learning: del dataset al despliegue. El objetivo es construir una solución "
        "pequeña pero completa y que otra persona pueda reproducirla.",
    )

    subhead("¿Para qué le serviría a una tienda?")
    cols = st.columns(3)
    uses = [
        ("🎯 Incentivos a tiempo", "Mostrar un cupón o envío gratis solo a las visitas en zona de duda, "
                                  "en lugar de regalar descuentos a todos."),
        ("💬 Ayuda proactiva", "Abrir el chat de soporte cuando una sesión con alta probabilidad muestra "
                              "señales de abandono."),
        ("📊 Medir campañas", "Comparar la probabilidad promedio de las visitas que llegan desde cada "
                             "campaña para saber cuál atrae compradores reales."),
    ]
    for col, (title, text) in zip(cols, uses):
        col.markdown(
            f'<div class="card"><div style="font-weight:600;margin-bottom:.35rem">{title}</div>'
            f'<div class="kpi-note" style="font-size:.9rem">{text}</div></div>',
            unsafe_allow_html=True,
        )

    subhead("Cómo se construyó")
    steps = [
        ("Dataset", "CSV público"),
        ("Google Colab", "exploración"),
        ("train.py", "entrena y evalúa"),
        ("model.joblib", "modelo + metadatos"),
        ("app.py", "interfaz Streamlit"),
        ("GitHub", "código versionado"),
        ("Docker", "imagen reproducible"),
        ("Nube", "app pública"),
    ]
    flow = '<span class="flow-arrow">→</span>'.join(
        f'<div class="flow-step">{a}<small>{b}</small></div>' for a, b in steps
    )
    st.markdown(f'<div class="flow">{flow}</div>', unsafe_allow_html=True)
    explain(
        "<b>train.py</b> se ejecuta una vez y guarda el modelo entrenado. <b>app.py</b> solo carga ese "
        "archivo: nunca vuelve a entrenar. El <b>Dockerfile</b> empaqueta Python, las librerías con "
        "versiones fijas, la app y el modelo en una imagen que corre igual en cualquier computador."
    )

    subhead("Reproducirlo")
    st.code(
        f"git clone {REPO_URL}.git\n"
        "cd intencion-compra-streamlit\n"
        "docker build -t intencion-compra-app .\n"
        "docker run -p 8501:8501 intencion-compra-app\n"
        "# Abrir http://localhost:8501",
        language="bash",
    )
    explain(f'Código, notebook de Colab y guía paso a paso en <a href="{REPO_URL}" target="_blank">GitHub</a>.')


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

    st.markdown(
        '<div class="hero-eyebrow">Machine Learning · E-commerce</div>'
        '<div class="hero-title">¿Esta visita terminará en compra?</div>'
        '<div class="hero-sub">Describe cómo navega un visitante en una tienda online y un modelo '
        'entrenado con 12.330 sesiones reales estimará la probabilidad de que compre.</div>',
        unsafe_allow_html=True,
    )

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

    st.markdown(
        f'<div class="footer">Universidad Externado de Colombia · Ciencia de Datos · '
        f'<a href="{REPO_URL}" target="_blank">Código en GitHub</a></div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
