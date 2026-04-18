"""
Centralized Configuration for Student Dropout Risk Assessment.

All constants, thresholds, paths, and feature mappings are defined here
to ensure consistency across the ML pipeline, API, and dashboard.
"""

import os
from pathlib import Path

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models" / "artifacts"
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "data" / "predictions.db"

MODEL_PATH = MODELS_DIR / "student_risk_model.pkl"
FEATURE_NAMES_PATH = MODELS_DIR / "feature_names.pkl"
EXPLAINER_PATH = MODELS_DIR / "shap_explainer.pkl"
TRAINING_METRICS_PATH = MODELS_DIR / "training_metrics.json"
MODEL_COMPARISON_PATH = MODELS_DIR / "model_comparison.json"

# ──────────────────────────────────────────────
# UCI Dataset
# ──────────────────────────────────────────────
UCI_DATASET_ID = 697  # "Predict students' dropout and academic success"

# ──────────────────────────────────────────────
# Risk Tier Thresholds
# ──────────────────────────────────────────────
RISK_TIERS = {
    "Critical": {"threshold": 0.75, "tier": "Critical", "emoji": "warning", "action": "Immediate 1-on-1 counseling required."},
    "High": {"threshold": 0.50, "tier": "High", "emoji": "priority_high", "action": "Assign academic advisor & setup tutoring."},
    "Medium": {"threshold": 0.25, "tier": "Medium", "emoji": "info", "action": "Send early warning email & study resources."},
    "Low": {"threshold": 0.0, "tier": "Low", "emoji": "check_circle", "action": "Monitor progress; student is on track."},
}

def get_risk_tier(probability: float) -> dict:
    """Return the risk tier dict for a given dropout probability."""
    if probability >= RISK_TIERS["Critical"]["threshold"]:
        return RISK_TIERS["Critical"]
    elif probability >= RISK_TIERS["High"]["threshold"]:
        return RISK_TIERS["High"]
    elif probability >= RISK_TIERS["Medium"]["threshold"]:
        return RISK_TIERS["Medium"]
    else:
        return RISK_TIERS["Low"]

# ──────────────────────────────────────────────
# Feature Mappings (API field name → model feature name)
# ──────────────────────────────────────────────
FEATURE_MAP = {
    "marital_status": "Marital Status",
    "application_mode": "Application mode",
    "application_order": "Application order",
    "course": "Course",
    "attendance": "Daytime/evening attendance",
    "prev_qualification": "Previous qualification",
    "prev_qualification_grade": "Previous qualification (grade)",
    "nationality": "Nacionality",
    "mothers_qualification": "Mother's qualification",
    "fathers_qualification": "Father's qualification",
    "mothers_occupation": "Mother's occupation",
    "fathers_occupation": "Father's occupation",
    "admission_grade": "Admission grade",
    "displaced": "Displaced",
    "special_needs": "Educational special needs",
    "debtor": "Debtor",
    "tuition_up_to_date": "Tuition fees up to date",
    "gender": "Gender",
    "scholarship_holder": "Scholarship holder",
    "age_at_enrollment": "Age at enrollment",
    "international": "International",
    "s1_credited": "Curricular units 1st sem (credited)",
    "s1_enrolled": "Curricular units 1st sem (enrolled)",
    "s1_evaluations": "Curricular units 1st sem (evaluations)",
    "s1_approved": "Curricular units 1st sem (approved)",
    "s1_grade": "Curricular units 1st sem (grade)",
    "s1_without_evaluations": "Curricular units 1st sem (without evaluations)",
    "s2_credited": "Curricular units 2nd sem (credited)",
    "s2_enrolled": "Curricular units 2nd sem (enrolled)",
    "s2_evaluations": "Curricular units 2nd sem (evaluations)",
    "s2_approved": "Curricular units 2nd sem (approved)",
    "s2_grade": "Curricular units 2nd sem (grade)",
    "s2_without_evaluations": "Curricular units 2nd sem (without evaluations)",
    "unemployment_rate": "Unemployment rate",
    "inflation_rate": "Inflation rate",
    "gdp": "GDP",
}

# Reverse mapping for SHAP explanations (model feature → human-readable)
FEATURE_DISPLAY_NAMES = {
    "Marital Status": "Marital Status",
    "Application mode": "Application Mode",
    "Application order": "Application Order",
    "Course": "Course Program",
    "Daytime/evening attendance": "Attendance Type",
    "Previous qualification": "Previous Qualification",
    "Previous qualification (grade)": "Previous Qualification Grade",
    "Nacionality": "Nationality",
    "Mother's qualification": "Mother's Education",
    "Father's qualification": "Father's Education",
    "Mother's occupation": "Mother's Occupation",
    "Father's occupation": "Father's Occupation",
    "Admission grade": "Admission Grade",
    "Displaced": "Displaced Student",
    "Educational special needs": "Special Needs",
    "Debtor": "Has Debt",
    "Tuition fees up to date": "Tuition Paid",
    "Gender": "Gender",
    "Scholarship holder": "Scholarship Holder",
    "Age at enrollment": "Age at Enrollment",
    "International": "International Student",
    "Curricular units 1st sem (credited)": "S1 Credited Units",
    "Curricular units 1st sem (enrolled)": "S1 Enrolled Units",
    "Curricular units 1st sem (evaluations)": "S1 Evaluations",
    "Curricular units 1st sem (approved)": "S1 Approved Units",
    "Curricular units 1st sem (grade)": "S1 Grade",
    "Curricular units 1st sem (without evaluations)": "S1 Without Evaluations",
    "Curricular units 2nd sem (credited)": "S2 Credited Units",
    "Curricular units 2nd sem (enrolled)": "S2 Enrolled Units",
    "Curricular units 2nd sem (evaluations)": "S2 Evaluations",
    "Curricular units 2nd sem (approved)": "S2 Approved Units",
    "Curricular units 2nd sem (grade)": "S2 Grade",
    "Curricular units 2nd sem (without evaluations)": "S2 Without Evaluations",
    "Unemployment rate": "Unemployment Rate",
    "Inflation rate": "Inflation Rate",
    "GDP": "GDP",
    # Engineered features
    "grade_trend": "Grade Trend (S2 − S1)",
    "s1_approval_rate": "S1 Approval Rate",
    "s2_approval_rate": "S2 Approval Rate",
    "approval_momentum": "Approval Momentum",
    "total_approved": "Total Approved Units",
    "avg_grade": "Average Grade",
    "eval_to_approval_ratio": "Evaluation-to-Approval Ratio",
}

# ──────────────────────────────────────────────
# What-If Scenario Presets
# ──────────────────────────────────────────────
SCENARIO_PRESETS = {
    "Pay Tuition": {"tuition_up_to_date": 1},
    "Get Scholarship": {"scholarship_holder": 1, "tuition_up_to_date": 1},
    "Academic Recovery (S2)": {"s2_approved": "+3", "s2_grade": "+3.0"},
    "Full Recovery": {"s2_approved": "+5", "s2_grade": "+5.0", "tuition_up_to_date": 1},
}

# ──────────────────────────────────────────────
# API Settings
# ──────────────────────────────────────────────
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# ──────────────────────────────────────────────
# Dashboard Settings
# ──────────────────────────────────────────────
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8501"))

# ──────────────────────────────────────────────
# Training Settings
# ──────────────────────────────────────────────
TEST_SIZE = 0.2
CV_FOLDS = 5
RANDOM_STATE = 42
N_ITER_SEARCH = 50  # RandomizedSearchCV iterations
