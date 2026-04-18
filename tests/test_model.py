"""
Model Validation Tests — Ensure model artifacts are valid and predictions are sane.
"""

import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import FEATURE_NAMES_PATH, MODEL_PATH


class TestModelArtifacts:
    """Tests for model file integrity."""

    def test_model_exists(self):
        assert MODEL_PATH.exists(), f"Model not found at {MODEL_PATH}"

    def test_feature_names_exist(self):
        assert FEATURE_NAMES_PATH.exists(), f"Feature names not found at {FEATURE_NAMES_PATH}"

    def test_model_loads(self):
        model = joblib.load(MODEL_PATH)
        assert model is not None
        assert hasattr(model, "predict")
        assert hasattr(model, "predict_proba")

    def test_feature_names_loads(self):
        feature_names = joblib.load(FEATURE_NAMES_PATH)
        assert isinstance(feature_names, list)
        assert len(feature_names) > 0

    def test_feature_count_matches(self):
        model = joblib.load(MODEL_PATH)
        feature_names = joblib.load(FEATURE_NAMES_PATH)
        assert model.n_features_in_ == len(feature_names)


class TestModelPredictions:
    """Tests for prediction quality and sanity."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.model = joblib.load(MODEL_PATH)
        self.feature_names = joblib.load(FEATURE_NAMES_PATH)

    def _make_input(self, **overrides) -> pd.DataFrame:
        """Create a test input DataFrame with zeros and optional overrides."""
        df = pd.DataFrame(np.zeros((1, len(self.feature_names))), columns=self.feature_names)
        for col, val in overrides.items():
            if col in df.columns:
                df[col] = val
        return df

    def test_prediction_shape(self):
        input_df = self._make_input()
        pred = self.model.predict(input_df)
        assert pred.shape == (1,)
        assert pred[0] in [0, 1]

    def test_prediction_proba_shape(self):
        input_df = self._make_input()
        proba = self.model.predict_proba(input_df)
        assert proba.shape == (1, 2)
        assert 0 <= proba[0][0] <= 1
        assert 0 <= proba[0][1] <= 1
        assert abs(proba[0][0] + proba[0][1] - 1.0) < 1e-6

    def test_proba_range(self):
        """Probabilities should always be between 0 and 1."""
        for _ in range(10):
            input_df = pd.DataFrame(
                np.random.rand(1, len(self.feature_names)) * 20,
                columns=self.feature_names,
            )
            proba = self.model.predict_proba(input_df)
            assert 0 <= proba[0][1] <= 1

    def test_high_risk_pattern(self):
        """Student with no approvals and no tuition should have elevated risk."""
        input_df = self._make_input(
            **{
                "Tuition fees up to date": 0,
                "Curricular units 1st sem (approved)": 0,
                "Curricular units 1st sem (grade)": 0,
                "Curricular units 2nd sem (approved)": 0,
                "Curricular units 2nd sem (grade)": 0,
            }
        )
        proba = self.model.predict_proba(input_df)[0][1]
        assert proba > 0.3, f"Expected elevated risk, got {proba}"

    def test_low_risk_pattern(self):
        """Student with good grades and tuition paid should have lower risk."""
        input_df = self._make_input(
            **{
                "Tuition fees up to date": 1,
                "Scholarship holder": 1,
                "Curricular units 1st sem (approved)": 6,
                "Curricular units 1st sem (grade)": 14,
                "Curricular units 2nd sem (approved)": 6,
                "Curricular units 2nd sem (grade)": 14,
            }
        )
        proba = self.model.predict_proba(input_df)[0][1]
        assert proba < 0.7, f"Expected lower risk, got {proba}"

    def test_batch_prediction(self):
        """Model should handle batch predictions."""
        n_samples = 50
        input_df = pd.DataFrame(
            np.random.rand(n_samples, len(self.feature_names)) * 10,
            columns=self.feature_names,
        )
        preds = self.model.predict(input_df)
        assert len(preds) == n_samples
        assert all(p in [0, 1] for p in preds)
