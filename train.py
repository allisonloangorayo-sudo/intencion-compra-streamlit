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
from sklearn.inspection import permutation_importance
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
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


def _downsample_curve(xs, ys, n: int = 120) -> list[dict]:
    idx = np.unique(np.linspace(0, len(xs) - 1, n).astype(int))
    return [{"x": round(float(xs[i]), 4), "y": round(float(ys[i]), 4)} for i in idx]


def _rate_by_bins(df: pd.DataFrame, col: str, bins: list[float], labels: list[str]) -> list[dict]:
    groups = pd.cut(df[col], bins=bins, labels=labels, include_lowest=True)
    out = df.groupby(groups, observed=False)[TARGET].agg(["mean", "size"]).reset_index()
    return [
        {"rango": str(r[col]), "tasa": round(float(r["mean"]), 4), "sesiones": int(r["size"])}
        for _, r in out.iterrows()
    ]


def build_insights(
    df: pd.DataFrame,
    model: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    comparison: dict,
) -> dict:
    """Resúmenes precalculados para las gráficas de la app.

    La app no necesita leer el CSV: todo lo que muestra de los datos y del modelo
    se guarda aquí, dentro de model.joblib.
    """
    proba = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, proba)
    prec, rec, _ = precision_recall_curve(y_test, proba)

    # Importancia por permutación: cuánto cae el ROC-AUC si se desordena cada variable
    perm = permutation_importance(
        model, X_test, y_test, scoring="roc_auc", n_repeats=5,
        random_state=RANDOM_STATE, n_jobs=-1,
    )
    importance = sorted(
        [
            {"variable": f, "importancia": round(float(m), 4), "desv": round(float(sd), 4)}
            for f, m, sd in zip(FEATURES, perm.importances_mean, perm.importances_std)
        ],
        key=lambda d: d["importancia"],
        reverse=True,
    )

    # Distribución de probabilidades predichas en prueba, por clase real
    proba_hist = []
    edges = np.linspace(0, 1, 21)
    for cls, name in [(0, "No compra"), (1, "Compra")]:
        counts, _ = np.histogram(proba[y_test.values == cls], bins=edges)
        proba_hist += [
            {"desde": round(float(edges[i]), 2), "hasta": round(float(edges[i + 1]), 2),
             "clase_real": name, "sesiones": int(c)}
            for i, c in enumerate(counts)
        ]

    by_month = (
        df.groupby("Month")[TARGET].agg(["mean", "size"])
        .reindex([m for m in MONTH_ORDER if m in set(df["Month"])])
        .reset_index()
    )
    by_visitor = df.groupby("VisitorType")[TARGET].agg(["mean", "size"]).reset_index()
    by_weekend = df.groupby("Weekend")[TARGET].agg(["mean", "size"]).reset_index()

    def records(frame: pd.DataFrame, key: str) -> list[dict]:
        return [
            {"categoria": str(r[key]), "tasa": round(float(r["mean"]), 4), "sesiones": int(r["size"])}
            for _, r in frame.iterrows()
        ]

    medians_by_class = (
        df.groupby(TARGET)[NUMERIC_FEATURES].median().T
        .rename(columns={0: "no_compra", 1: "compra"})
    )

    return {
        "n_rows": int(len(df)),
        "n_cols": int(df.shape[1]),
        "positive_rate": round(float(df[TARGET].mean()), 4),
        "class_counts": {
            "No compra": int((df[TARGET] == 0).sum()),
            "Compra": int((df[TARGET] == 1).sum()),
        },
        "missing_values": int(df.isna().sum().sum()),
        "rate_by_month": records(by_month, "Month"),
        "rate_by_visitor": records(by_visitor, "VisitorType"),
        "rate_by_weekend": records(by_weekend, "Weekend"),
        "rate_by_pagevalues": _rate_by_bins(
            df, "PageValues", [-0.1, 0, 10, 25, 50, 1e9],
            ["0", "0 – 10", "10 – 25", "25 – 50", "Más de 50"],
        ),
        "rate_by_exitrates": _rate_by_bins(
            df, "ExitRates", [-0.1, 0.01, 0.02, 0.04, 0.08, 1],
            ["Menos de 1 %", "1 – 2 %", "2 – 4 %", "4 – 8 %", "Más de 8 %"],
        ),
        "rate_by_productrelated": _rate_by_bins(
            df, "ProductRelated", [-1, 5, 15, 30, 60, 1e9],
            ["0 – 5", "6 – 15", "16 – 30", "31 – 60", "Más de 60"],
        ),
        "medians_by_class": {
            f: {"no_compra": round(float(r["no_compra"]), 4), "compra": round(float(r["compra"]), 4)}
            for f, r in medians_by_class.iterrows()
        },
        "roc_curve": _downsample_curve(fpr, tpr),
        "pr_curve": _downsample_curve(rec[::-1], prec[::-1]),
        "proba_hist": proba_hist,
        "permutation_importance": importance,
        "model_comparison": comparison,
        "train_size": int(len(df) - len(X_test)),
        "test_size": int(len(X_test)),
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

    # Comparación en prueba de ambos candidatos (solo informativa: la elección ya se hizo con CV)
    comparison = {}
    for name, pipe in candidate_models().items():
        fitted = model if name == best_name else pipe.fit(X_train, y_train)
        m = evaluate(fitted, X_test, y_test)
        comparison[name] = {
            "cv_f1": cv_scores[name],
            **{k: v for k, v in m.items() if k != "confusion_matrix"},
        }

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

    # Valores de referencia ("sesión típica") para explicar cada predicción en la app
    reference_values = {
        **{col: float(df[col].median()) for col in NUMERIC_FEATURES},
        **{col: str(df[col].mode().iloc[0]) for col in CATEGORICAL_FEATURES},
    }

    insights = build_insights(df, model, X_test, y_test, comparison)
    insights["roc_auc_without_pagevalues"] = round(float(sens_auc), 4)

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
        "reference_values": reference_values,
        "insights": insights,
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
        "test_metrics_by_model": comparison,
        "permutation_importance_roc_auc": insights["permutation_importance"],
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
