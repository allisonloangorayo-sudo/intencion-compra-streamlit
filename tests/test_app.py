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


@pytest.mark.parametrize("preset", [
    "Valores típicos (mediana)", "Sesión con alta intención", "Sesión de rebote rápido",
])
def test_app_runs_each_preset(preset):
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception
    at.selectbox[0].select(preset).run()
    at.button[0].click().run()
    assert not at.exception
    assert len(at.metric) == 2
    print(preset, "->", at.metric[0].value, at.metric[1].value)
