"""
Entrenamiento reproducible del modelo de intención de compra.

Ruta A (supervisada): clasificación binaria.
Pregunta: ¿esta sesión de navegación en una tienda online terminará en compra?

Uso:
    python train.py

Salidas:
    model.joblib   -> artefacto con el pipeline entrenado y metadatos para la app
    metrics.json   -> métricas de evaluación en el conjunto de prueba
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "online_shoppers_intention.csv"
MODEL_PATH = ROOT / "model.joblib"
METRICS_PATH = ROOT / "metrics.json"

RANDOM_STATE = 42
TARGET = "Revenue"

# Variables de comportamiento de la sesión (conteos, duraciones y métricas web)
NUMERIC_FEATURES = [
    "Administrative",
    "Administrative_Duration",
    "Informational",
    "Informational_Duration",
    "ProductRelated",
    "ProductRelated_Duration",
    "BounceRates",
    "ExitRates",
    "PageValues",
    "SpecialDay",
]

# Variables de contexto de la visita
CATEGORICAL_FEATURES = [
    "Month",
    "VisitorType",
    "Weekend",
]

# Excluidas a propósito:
#   OperatingSystems, Browser, Region, TrafficType -> códigos enteros anónimos,
#   sin etiqueta interpretable; una persona no podría llenarlos en la app.
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# Descripciones en español para la interfaz
FEATURE_LABELS = {
    "Administrative": "Páginas administrativas visitadas",
    "Administrative_Duration": "Tiempo en páginas administrativas (s)",
    "Informational": "Páginas informativas visitadas",
    "Informational_Duration": "Tiempo en páginas informativas (s)",
    "ProductRelated": "Páginas de producto visitadas",
    "ProductRelated_Duration": "Tiempo en páginas de producto (s)",
    "BounceRates": "Tasa de rebote promedio de las páginas",
    "ExitRates": "Tasa de salida promedio de las páginas",
    "PageValues": "Valor de página promedio (Google Analytics)",
    "SpecialDay": "Cercanía a una fecha especial (0 a 1)",
    "Month": "Mes de la visita",
    "VisitorType": "Tipo de visitante",
    "Weekend": "¿Es fin de semana?",
}

MONTH_ORDER = ["Feb", "Mar", "May", "June", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------
def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Las categóricas se tratan como texto para que la app y el modelo coincidan
    for col in CATEGORICAL_FEATURES:
        df[col] = df[col].astype(str)
    df[TARGET] = df[TARGET].astype(int)
    return df


# ---------------------------------------------------------------------------
# Modelo
# ---------------------------------------------------------------------------
def build_preprocessor(numeric_features: list[str] = NUMERIC_FEATURES) -> ColumnTransformer:
    # Duraciones y conteos son muy asimétricos: log1p reduce el peso de valores extremos
    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("log1p", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("num", numeric_pipe, numeric_features),
        ("cat", categorical_pipe, CATEGORICAL_FEATURES),
    ])


def candidate_models(numeric_features: list[str] = NUMERIC_FEATURES) -> dict[str, Pipeline]:
    # class_weight="balanced" compensa que solo ~15 % de las sesiones compran
    return {
        "logistic_regression": Pipeline([
            ("preprocessor", build_preprocessor(numeric_features)),
            ("classifier", LogisticRegression(
                max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE
            )),
        ]),
        "random_forest": Pipeline([
            ("preprocessor", build_preprocessor(numeric_features)),
            ("classifier", RandomForestClassifier(
                n_estimators=300,
                min_samples_leaf=5,
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=-1,
            )),
        ]),
    }


def evaluate(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    return {
        "f1_compra": round(f1_score(y_test, pred), 4),
        "recall_compra": round(recall_score(y_test, pred), 4),
        "precision_compra": round(precision_score(y_test, pred), 4),
        "roc_auc": round(roc_auc_score(y_test, proba), 4),
        "pr_auc": round(average_precision_score(y_test, proba), 4),
        "f1_weighted": round(f1_score(y_test, pred, average="weighted"), 4),
        "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
    }


def train_model(df: pd.DataFrame) -> tuple[dict, dict]:
    X = df[FEATURES].copy()
    y = df[TARGET].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )

    # 1. Selección de modelo con validación cruzada SOLO sobre entrenamiento
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = {}
    for name, pipe in candidate_models().items():
        scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="f1", n_jobs=-1)
        cv_scores[name] = round(float(scores.mean()), 4)
        print(f"[CV] {name:<20} F1 (clase compra) = {scores.mean():.4f} ± {scores.std():.4f}")

    best_name = max(cv_scores, key=cv_scores.get)
    print(f"\nModelo elegido: {best_name}")

    # 2. Entrenamiento final y evaluación en prueba (datos nunca vistos)
    model = candidate_models()[best_name]
    model.fit(X_train, y_train)
    metrics = evaluate(model, X_test, y_test)

    print("\nMatriz de confusión (filas = real, columnas = predicho) [no compra, compra]:")
    print(np.array(metrics["confusion_matrix"]))
    print("\n" + classification_report(
        y_test, model.predict(X_test), target_names=["No compra", "Compra"]
    ))
    for k, v in metrics.items():
        if k != "confusion_matrix":
            print(f"{k:<18} {v}")

    # 3. Análisis de sensibilidad: ¿cuánto depende el modelo de PageValues?
    no_pv = [f for f in NUMERIC_FEATURES if f != "PageValues"]
    sens = candidate_models(no_pv)[best_name]
    sens.fit(X_train[[f for f in FEATURES if f != "PageValues"]], y_train)
    sens_auc = roc_auc_score(
        y_test, sens.predict_proba(X_test[[f for f in FEATURES if f != "PageValues"]])[:, 1]
    )
    print(f"\nSensibilidad: ROC-AUC sin PageValues = {sens_auc:.4f}")

    # 4. Metadatos que necesita la interfaz
    category_options = {
        col: sorted(df[col].dropna().astype(str).unique().tolist())
        for col in CATEGORICAL_FEATURES
    }
    category_options["Month"] = [m for m in MONTH_ORDER if m in category_options["Month"]]

    numeric_ranges = {
        col: {
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "median": float(df[col].median()),
            "p99": float(df[col].quantile(0.99)),
        }
        for col in NUMERIC_FEATURES
    }

    artifact = {
        "model": model,
        "model_name": best_name,
        "task": "classification",
        "target": TARGET,
        "class_labels": {0: "No compra", 1: "Compra"},
        "threshold": 0.5,
        "features": FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "category_options": category_options,
        "numeric_ranges": numeric_ranges,
        "feature_labels": FEATURE_LABELS,
        "metrics": metrics,
    }

    report = {
        "dataset": DATA_PATH.name,
        "n_rows": int(len(df)),
        "positive_rate": round(float(y.mean()), 4),
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "cv_f1_by_model": cv_scores,
        "selected_model": best_name,
        "test_metrics": metrics,
        "roc_auc_without_PageValues": round(float(sens_auc), 4),
    }
    return artifact, report


def main() -> None:
    df = load_data()
    print(f"Datos cargados: {df.shape[0]} sesiones, {df.shape[1]} columnas")
    print(f"Tasa de compra: {df[TARGET].mean():.2%}\n")

    artifact, report = train_model(df)

    joblib.dump(artifact, MODEL_PATH, compress=3)
    METRICS_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nModelo guardado en {MODEL_PATH.name}")
    print(f"Métricas guardadas en {METRICS_PATH.name}")


if __name__ == "__main__":
    main()
