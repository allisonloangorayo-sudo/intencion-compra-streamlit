"""Pruebas mínimas: el artefacto carga y la app responde a los casos de ejemplo.

Ejecutar desde la raíz del proyecto:
    python -m pytest -q
"""
from pathlib import Path

import joblib
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app.py")


def test_artifact_has_metadata():
    artifact = joblib.load(ROOT / "model.joblib")
    for key in ["model", "features", "numeric_features", "categorical_features",
                "category_options", "task"]:
        assert key in artifact
    assert artifact["task"] == "classification"


def test_model_predicts_probability():
    artifact = joblib.load(ROOT / "model.joblib")
    df = pd.read_csv(ROOT / "data" / "online_shoppers_intention.csv").head(5)
    for col in artifact["categorical_features"]:
        df[col] = df[col].astype(str)
    proba = artifact["model"].predict_proba(df[artifact["features"]])[:, 1]
    assert ((proba >= 0) & (proba <= 1)).all()


@pytest.mark.parametrize("preset, low, high", [
    ("Sesión típica", 0.0, 0.10),
    ("Sesión con alta intención", 0.80, 1.0),
    ("Sesión de rebote rápido", 0.0, 0.05),
])
def test_app_runs_each_preset(preset, low, high):
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    at.selectbox[0].select(preset).run()
    at.button[0].click().run()
    assert not at.exception
    proba = at.session_state["resultado"]["proba"]
    assert low <= proba <= high
    print(f"{preset} -> {proba:.3f}")


def test_all_tabs_render_without_errors():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    assert [t.label for t in at.tabs] == ["Predicción", "Los datos", "El modelo", "El proyecto"]
