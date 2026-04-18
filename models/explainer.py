"""
SHAP Explainability Engine for Student Dropout Risk Assessment.

Provides per-prediction explanations, global feature importance,
and natural language summaries of risk factors.

This module wraps SHAP's TreeExplainer for production use,
with caching, error handling, and human-readable output.
"""

import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import (
    EXPLAINER_PATH,
    FEATURE_DISPLAY_NAMES,
    MODEL_PATH,
)


class RiskExplainer:
    """SHAP-based explainability engine for the student risk model."""

    def __init__(self):
        """Load model and SHAP explainer from saved artifacts."""
        self.model = joblib.load(MODEL_PATH)
        try:
            self.explainer = joblib.load(EXPLAINER_PATH)
        except FileNotFoundError:
            print("⚠️  SHAP explainer not found, building from model...")
            self.explainer = shap.TreeExplainer(self.model)
            joblib.dump(self.explainer, EXPLAINER_PATH)

    def explain(self, input_df: pd.DataFrame, top_n: int = 5) -> dict:
        """
        Generate SHAP explanation for a single prediction.

        Args:
            input_df: DataFrame with one row matching model features.
            top_n: Number of top factors to return.

        Returns:
            dict with risk_factors, protective_factors, shap_values, base_value,
            feature_contributions, and natural_language_summary.
        """
        shap_values = self.explainer.shap_values(input_df)

        # For binary classification, take class 1 (dropout) SHAP values
        if isinstance(shap_values, list):
            sv = shap_values[1][0]  # Class 1, first (only) sample
        else:
            sv = shap_values[0]

        base_value = self.explainer.expected_value
        if isinstance(base_value, (list, np.ndarray)):
            base_value = base_value[1]  # Class 1

        feature_names = input_df.columns.tolist()
        feature_values = input_df.iloc[0].values

        # Build sorted contributions
        contributions = []
        for i, (name, shap_val, feat_val) in enumerate(
            zip(feature_names, sv, feature_values)
        ):
            display_name = FEATURE_DISPLAY_NAMES.get(name, name)
            contributions.append(
                {
                    "feature": name,
                    "display_name": display_name,
                    "shap_value": float(shap_val),
                    "feature_value": float(feat_val),
                    "direction": "risk" if shap_val > 0 else "protective",
                    "abs_impact": abs(float(shap_val)),
                }
            )

        # Sort by absolute SHAP impact
        contributions.sort(key=lambda x: x["abs_impact"], reverse=True)

        risk_factors = [c for c in contributions if c["direction"] == "risk"][:top_n]
        protective_factors = [c for c in contributions if c["direction"] == "protective"][:top_n]

        # Natural language summary
        summary = self._generate_summary(risk_factors, protective_factors)

        return {
            "base_value": float(base_value),
            "shap_values": sv.tolist(),
            "feature_names": feature_names,
            "feature_values": feature_values.tolist(),
            "risk_factors": risk_factors,
            "protective_factors": protective_factors,
            "all_contributions": contributions[:15],  # Top 15
            "natural_language_summary": summary,
        }

    def global_importance(self, X_sample: pd.DataFrame = None) -> list[dict]:
        """
        Compute global feature importance from SHAP values.

        Args:
            X_sample: Sample of data to compute SHAP values over.
                     If None, uses model's feature_importances_.

        Returns:
            Sorted list of {feature, display_name, importance} dicts.
        """
        if X_sample is not None and len(X_sample) > 0:
            shap_values = self.explainer.shap_values(X_sample)
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
            importances = np.abs(shap_values).mean(axis=0)
            feature_names = X_sample.columns.tolist()
        else:
            importances = self.model.feature_importances_
            feature_names = list(FEATURE_DISPLAY_NAMES.keys())
            if len(feature_names) != len(importances):
                feature_names = [f"Feature {i}" for i in range(len(importances))]

        result = []
        for name, imp in zip(feature_names, importances):
            display_name = FEATURE_DISPLAY_NAMES.get(name, name)
            result.append(
                {
                    "feature": name,
                    "display_name": display_name,
                    "importance": float(imp),
                }
            )

        result.sort(key=lambda x: x["importance"], reverse=True)
        return result

    def _generate_summary(
        self, risk_factors: list[dict], protective_factors: list[dict]
    ) -> str:
        """Generate a natural language explanation from SHAP factors."""
        parts = []

        if risk_factors:
            risk_desc = ", ".join(
                [
                    f"{f['display_name']} (impact: {f['abs_impact']:.3f})"
                    for f in risk_factors[:3]
                ]
            )
            parts.append(f"Primary risk drivers: {risk_desc}.")

        if protective_factors:
            prot_desc = ", ".join(
                [
                    f"{f['display_name']} (impact: {f['abs_impact']:.3f})"
                    for f in protective_factors[:3]
                ]
            )
            parts.append(f"Protective factors: {prot_desc}.")

        if not parts:
            return "No significant risk factors identified."

        return " ".join(parts)
