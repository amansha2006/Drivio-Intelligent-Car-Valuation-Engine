# src/explainability/shap_agent.py

import joblib
import shap
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")

MODEL_PATH = os.path.join(ARTIFACTS_DIR, "xgb_car_price_model.pkl")

model = joblib.load(MODEL_PATH)
explainer = shap.TreeExplainer(model)


def explain_prediction(X_row: pd.DataFrame, top_k: int = 5) -> list:
    """
    Generate human-readable SHAP explanations for a single prediction.
    """

    # ✅ Sanitize column names for XGBoost compatibility
    X_safe = X_row.copy()
    X_safe.columns = (
        X_safe.columns
        .str.replace("[", "", regex=False)
        .str.replace("]", "", regex=False)
        .str.replace("<", "", regex=False)
        .str.replace(">", "", regex=False)
    )

    shap_values = explainer.shap_values(X_safe)

    contributions = list(zip(X_safe.columns, shap_values[0]))
    contributions = sorted(contributions, key=lambda x: abs(x[1]), reverse=True)[:top_k]

    explanations = []
    for feature, value in contributions:
        if value > 0:
            explanations.append(f"{feature} increased the price by ₹{int(value):,}")
        else:
            explanations.append(f"{feature} decreased the price by ₹{abs(int(value)):,}")

    return explanations
