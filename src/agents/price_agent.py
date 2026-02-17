import pandas as pd
import joblib
import os

from src.model.predictor import predict_price
from src.agents.negotiation_agent import negotiation_advice
from src.explainability.shap_agent import explain_prediction


# Resolve project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
FEATURES_PATH = os.path.join(ARTIFACTS_DIR, "model_features.pkl")


class CarPriceAgent:

    # -------------------------
    # Ownership Adjustment Layer
    # -------------------------
    def _ownership_adjustment(self, owners: int):
        if owners == 1:
            return 10000, "Single Owner (Premium Ownership)"
        elif owners == 2:
            return -15000, "Second Owner (Moderate Depreciation)"
        else:
            return -30000, "Multiple Owners (Higher Resale Risk)"

    # -------------------------
    # Uncertainty Band Logic
    # -------------------------
    def _uncertainty_band(self, price, confidence):
        if confidence == "Very High":
            pct = 0.03
        elif confidence == "High":
            pct = 0.05
        elif confidence == "Medium":
            pct = 0.08
        else:
            pct = 0.12

        lower = price * (1 - pct)
        upper = price * (1 + pct)

        return round(lower, 2), round(upper, 2)

    # -------------------------
    # Main Analysis Function
    # -------------------------
    def analyze(self, car_details: dict) -> dict:

        input_df = pd.DataFrame([car_details])

        # 1️⃣ Base ML Prediction
        base_price = predict_price(input_df)

        # 2️⃣ Prepare encoded input for SHAP
        feature_cols = joblib.load(FEATURES_PATH)

        X_encoded = pd.get_dummies(input_df)
        X_encoded = X_encoded.reindex(columns=feature_cols, fill_value=0)
        X_encoded = X_encoded.astype(float)

        # 3️⃣ SHAP Explanation
        shap_explanation = explain_prediction(X_encoded)

        # 4️⃣ Ownership Business Adjustment
        owners = car_details.get("number_of_owners", 1)
        adjustment_value, owner_label = self._ownership_adjustment(owners)

        adjusted_price = base_price + adjustment_value

        # Add ownership explanation explicitly
        if adjustment_value > 0:
            shap_explanation.append(
                f"Ownership Classification: {owner_label} Increased The Price By ₹{adjustment_value:,}"
            )
        else:
            shap_explanation.append(
                f"Ownership Classification: {owner_label} Decreased The Price By ₹{abs(adjustment_value):,}"
            )

        # 5️⃣ Confidence Logic
        confidence = "Very High" if adjusted_price > 800000 else "High"

        # 6️⃣ Uncertainty Range
        lower, upper = self._uncertainty_band(adjusted_price, confidence)

        # 7️⃣ Negotiation Advice (based on adjusted price)
        negotiation = negotiation_advice(adjusted_price)

        return {
            "predicted_price": round(adjusted_price, 2),
            "price_range": (lower, upper),
            "base_model_price": round(base_price, 2),
            "ownership_adjustment": adjustment_value,
            "confidence": confidence,
            "explanation": shap_explanation,
            "negotiation": negotiation
        }
