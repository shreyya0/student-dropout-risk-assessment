"""
API Integration Tests — Test all endpoints with valid/invalid inputs.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from api.main import app

client = TestClient(app)


# ──────────────────────────────────────────────
# Sample Data
# ──────────────────────────────────────────────

VALID_STUDENT = {
    "marital_status": 1,
    "application_mode": 1,
    "application_order": 1,
    "course": 33,
    "attendance": 1,
    "prev_qualification": 1,
    "prev_qualification_grade": 122.0,
    "nationality": 1,
    "mothers_qualification": 19,
    "fathers_qualification": 12,
    "mothers_occupation": 5,
    "fathers_occupation": 10,
    "admission_grade": 127.3,
    "displaced": 1,
    "special_needs": 0,
    "debtor": 0,
    "tuition_up_to_date": 1,
    "gender": 1,
    "scholarship_holder": 0,
    "age_at_enrollment": 20,
    "international": 0,
    "s1_credited": 0,
    "s1_enrolled": 6,
    "s1_evaluations": 6,
    "s1_approved": 6,
    "s1_grade": 13.67,
    "s1_without_evaluations": 0,
    "s2_credited": 0,
    "s2_enrolled": 6,
    "s2_evaluations": 6,
    "s2_approved": 5,
    "s2_grade": 12.4,
    "s2_without_evaluations": 0,
    "unemployment_rate": 10.8,
    "inflation_rate": 1.4,
    "gdp": 1.74,
}

HIGH_RISK_STUDENT = {
    **VALID_STUDENT,
    "tuition_up_to_date": 0,
    "debtor": 1,
    "s1_approved": 0,
    "s1_grade": 0.0,
    "s2_approved": 0,
    "s2_grade": 0.0,
}


# ──────────────────────────────────────────────
# Root
# ──────────────────────────────────────────────

class TestRoot:
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Student Dropout Risk Assessment API"
        assert "endpoints" in data


# ──────────────────────────────────────────────
# Predictions
# ──────────────────────────────────────────────

class TestPredictions:
    def test_single_prediction(self):
        response = client.post("/predict/", json=VALID_STUDENT)
        assert response.status_code == 200
        data = response.json()
        assert 0 <= data["risk_score"] <= 1
        assert data["risk_tier"]["tier"] in ["Low", "Medium", "High", "Critical"]
        assert data["prediction_id"] is not None

    def test_high_risk_student(self):
        response = client.post("/predict/", json=HIGH_RISK_STUDENT)
        assert response.status_code == 200
        data = response.json()
        assert data["risk_score"] > 0.3  # Should be elevated

    def test_prediction_with_defaults(self):
        """Test prediction with minimal input (using defaults)."""
        response = client.post("/predict/", json={})
        assert response.status_code == 200

    def test_batch_prediction(self):
        response = client.post(
            "/predict/batch",
            json={"students": [VALID_STUDENT, HIGH_RISK_STUDENT]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["predictions"]) == 2
        assert "summary" in data
        assert "avg_risk" in data["summary"]

    def test_batch_empty_fails(self):
        response = client.post("/predict/batch", json={"students": []})
        assert response.status_code == 422  # Validation error


# ──────────────────────────────────────────────
# Explanations
# ──────────────────────────────────────────────

class TestExplanations:
    def test_explain_prediction(self):
        response = client.post("/explain/", json=VALID_STUDENT)
        assert response.status_code == 200
        data = response.json()
        assert "risk_factors" in data
        assert "protective_factors" in data
        assert "natural_language_summary" in data
        assert len(data["risk_factors"]) > 0

    def test_global_importance(self):
        response = client.get("/explain/global-importance")
        assert response.status_code == 200
        data = response.json()
        assert "feature_importance" in data
        assert len(data["feature_importance"]) > 0


# ──────────────────────────────────────────────
# Simulation
# ──────────────────────────────────────────────

class TestSimulation:
    def test_whatif_simulation(self):
        payload = {
            "student": VALID_STUDENT,
            "modifications": {"tuition_up_to_date": 1, "s2_approved": 8},
        }
        response = client.post("/simulate/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "current_risk_score" in data
        assert "simulated_risk_score" in data
        assert "improvement_potential" in data

    def test_scenario_presets(self):
        response = client.get("/simulate/presets")
        assert response.status_code == 200
        data = response.json()
        assert "presets" in data
        assert len(data["presets"]) > 0

    def test_sensitivity_analysis(self):
        response = client.post("/simulate/sensitivity", json=VALID_STUDENT)
        assert response.status_code == 200
        data = response.json()
        assert "current_risk" in data
        assert "sensitivity_results" in data
        assert len(data["sensitivity_results"]) > 0


# ──────────────────────────────────────────────
# Analytics
# ──────────────────────────────────────────────

class TestAnalytics:
    def test_health_check(self):
        response = client.get("/analytics/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert data["model_loaded"] is True

    def test_model_info(self):
        response = client.get("/analytics/model-info")
        assert response.status_code == 200
        data = response.json()
        assert data["n_features"] > 0
        assert len(data["feature_names"]) > 0

    def test_prediction_history(self):
        response = client.get("/analytics/history")
        assert response.status_code == 200

    def test_analytics_summary(self):
        response = client.get("/analytics/summary")
        assert response.status_code == 200
