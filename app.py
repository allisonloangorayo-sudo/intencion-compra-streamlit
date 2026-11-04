"""
Aplicación Streamlit: ¿esta sesión terminará en compra?

Carga model.joblib (generado por train.py) y NO vuelve a entrenar.
Ejecutar:
    streamlit run app.py
"""

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

MODEL_PATH = Path(__file__).resolve().parent / "model.joblib"

# Casos de ejemplo para probar la app rápidamente
PRESETS = {
    "Valores típicos (mediana)": None,  # se llena con las medianas del entrenamiento
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

VISITOR_LABELS = {
    "New_Visitor": "Nuevo",
    "Returning_Visitor": "Recurrente",
    "Other": "Otro",
}
MONTH_LABELS = {
    "Feb": "Febrero", "Mar": "Marzo", "May": "Mayo", "June": "Junio", "Jul": "Julio",
    "Aug": "Agosto", "Sep": "Septiembre", "Oct": "Octubre", "Nov": "Noviembre", "Dec": "Diciembre",
}
WEEKEND_LABELS = {"True": "Sí", "False": "No"}
DISPLAY = {"Month": MONTH_LABELS, "VisitorType": VISITOR_LABELS, "Weekend": WEEKEND_LABELS}

INTEGER_FEATURES = {"Administrative", "Informational", "ProductRelated"}
RATE_FEATURES = {"BounceRates", "ExitRates", "SpecialDay"}


@st.cache_resource
def load_artifact(path: Path) -> dict:
    return joblib.load(path)


def numeric_input(feature: str, label: str, rng: dict):
    # El valor inicial viene de st.session_state (lo fija el caso de ejemplo elegido)
    if feature in INTEGER_FEATURES:
        return st.number_input(
            label, min_value=0, max_value=int(rng["max"]), step=1,
            key=feature,
        )
    if feature in RATE_FEATURES:
        return st.slider(
            label, min_value=0.0, max_value=float(rng["max"]),
            step=0.001 if feature != "SpecialDay" else 0.2, key=feature,
        )
    return st.number_input(
        label, min_value=0.0, max_value=float(rng["max"]), step=10.0,
        key=feature,
    )


def main() -> None:
    st.set_page_config(page_title="Intención de compra", page_icon="🛒", layout="centered")

    if not MODEL_PATH.exists():
        st.error("No se encontró model.joblib. Ejecute primero: python train.py")
        st.stop()

    artifact = load_artifact(MODEL_PATH)
    model = artifact["model"]
    features = artifact["features"]
    numeric_features = artifact["numeric_features"]
    categorical_features = artifact["categorical_features"]
    options = artifact["category_options"]
    ranges = artifact["numeric_ranges"]
    labels = artifact["feature_labels"]
    threshold = artifact.get("threshold", 0.5)

    st.title("¿Esta sesión terminará en compra?")
    st.write(
        "Describa una sesión de navegación en una tienda online y el modelo estimará "
        "la probabilidad de que el visitante compre."
    )

    preset_name = st.selectbox("Cargar un caso de ejemplo", list(PRESETS))
    preset = PRESETS[preset_name] or {
        **{f: ranges[f]["median"] for f in numeric_features},
        "Month": "May", "VisitorType": "Returning_Visitor", "Weekend": "False",
    }
    # Al cambiar de ejemplo, actualizar los valores de los widgets
    if st.session_state.get("_preset") != preset_name:
        for k, v in preset.items():
            st.session_state[k] = int(v) if k in INTEGER_FEATURES else (
                float(v) if isinstance(v, (int, float)) else v
            )
        st.session_state["_preset"] = preset_name

    values = {}
    with st.form("sesion"):
        st.subheader("Navegación")
        c1, c2 = st.columns(2)
        pairs = [
            ("Administrative", "Administrative_Duration"),
            ("Informational", "Informational_Duration"),
            ("ProductRelated", "ProductRelated_Duration"),
        ]
        for count_f, dur_f in pairs:
            with c1:
                values[count_f] = numeric_input(count_f, labels[count_f], ranges[count_f])
            with c2:
                values[dur_f] = numeric_input(dur_f, labels[dur_f], ranges[dur_f])

        st.subheader("Métricas de la sesión")
        for f in ["BounceRates", "ExitRates", "PageValues"]:
            values[f] = numeric_input(f, labels[f], ranges[f])

        st.subheader("Contexto")
        values["SpecialDay"] = numeric_input("SpecialDay", labels["SpecialDay"], ranges["SpecialDay"])
        c3, c4, c5 = st.columns(3)
        for col, f in zip([c3, c4, c5], categorical_features):
            with col:
                values[f] = st.selectbox(
                    labels[f], options[f],
                    format_func=lambda x, f=f: DISPLAY.get(f, {}).get(x, x),
                    key=f,
                )

        submitted = st.form_submit_button("Ejecutar modelo", type="primary", use_container_width=True)

    if submitted:
        X_new = pd.DataFrame([values], columns=features)
        proba = float(model.predict_proba(X_new)[0, 1])
        pred = int(proba >= threshold)
        label = artifact["class_labels"][pred]

        st.divider()
        m1, m2 = st.columns(2)
        m1.metric("Clase predicha", label)
        m2.metric("Probabilidad de compra", f"{proba:.1%}")
        st.progress(proba)

        if pred == 1:
            st.success(
                f"La probabilidad supera el umbral de {threshold:.0%}: el modelo clasifica "
                "la sesión como **compra**."
            )
        else:
            st.info(
                f"La probabilidad está por debajo del umbral de {threshold:.0%}: el modelo "
                "clasifica la sesión como **no compra**."
            )

        with st.expander("Datos enviados al modelo"):
            st.dataframe(X_new.T.rename(columns={0: "valor"}).astype(str))

    with st.expander("Sobre el modelo"):
        m = artifact["metrics"]
        st.write(f"Modelo: `{artifact['model_name']}` dentro de un Pipeline de scikit-learn.")
        st.write(
            f"En el conjunto de prueba: ROC-AUC **{m['roc_auc']:.3f}**, "
            f"recall de compra **{m['recall_compra']:.1%}**, "
            f"precisión de compra **{m['precision_compra']:.1%}**, "
            f"F1 de compra **{m['f1_compra']:.3f}**."
        )
        st.caption(
            "Datos: Online Shoppers Purchasing Intention (Sakar et al., 2019, UCI). "
            "Cada fila es una sesión de navegación en una tienda online."
        )


if __name__ == "__main__":
    main()
