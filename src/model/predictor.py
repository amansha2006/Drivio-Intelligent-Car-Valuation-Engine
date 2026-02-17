# src/model/predictor.py

import joblib
import pandas as pd
import os


# Load artifacts only once
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")

MODEL_PATH = os.path.join(ARTIFACTS_DIR, "xgb_car_price_model.pkl")
FEATURES_PATH = os.path.join(ARTIFACTS_DIR, "model_features.pkl")

model = joblib.load(MODEL_PATH)
model_features = joblib.load(FEATURES_PATH)


def predict_price(input_df: pd.DataFrame) -> float:
    """
    Predict used car price from raw input features.

    Parameters:
        input_df (pd.DataFrame): raw input with original feature columns

    Returns:
        float: predicted price in INR
    """

    # One-hot encode input
    X = pd.get_dummies(input_df)

    # Align with training features
    X = X.reindex(columns=model_features, fill_value=0)

    # Ensure numeric
    X = X.astype(float)

    # Predict
    prediction = model.predict(X)[0]

    return float(prediction)
