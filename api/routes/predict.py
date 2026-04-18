"""
Prediction Routes — Single and Batch student risk predictions.
"""

import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config.settings import FEATURE_MAP, FEATURE_NAMES_PATH, MODEL_PATH, get_risk_tier
from api.schemas import (
    BatchInput,
    BatchPredictionItem,
    BatchResponse,
    PredictionResponse,
    RiskTierInfo,
    StudentInput,
)
from api.database import log_prediction

router = APIRouter(prefix="/predict", tags=["Predictions"])

# Load model artifacts at startup
model = joblib.load(MODEL_PATH)
feature_names = joblib.load(FEATURE_NAMES_PATH)


def student_to_dataframe(student: StudentInput) -> pd.DataFrame:
    """Convert a StudentInput to a model-ready DataFrame with all features."""
    # Start with zeros for all features
    input_df = pd.DataFrame(np.zeros((1, len(feature_names))), columns=feature_names)

    # Map API fields to model features
    data = student.model_dump()
    for api_field, model_feature in FEATURE_MAP.items():
        if api_field in data and model_feature in feature_names:
            input_df[model_feature] = data[api_field]

    # Add engineered features if they exist in the model
    if "grade_trend" in feature_names:
        input_df["grade_trend"] = data["s2_grade"] - data["s1_grade"]
    if "s1_approval_rate" in feature_names:
        s1_enrolled = max(data["s1_enrolled"], 1)
        input_df["s1_approval_rate"] = data["s1_approved"] / s1_enrolled
    if "s2_approval_rate" in feature_names:
        s2_enrolled = max(data["s2_enrolled"], 1)
        input_df["s2_approval_rate"] = data["s2_approved"] / s2_enrolled
    if "approval_momentum" in feature_names:
        s1_enrolled = max(data["s1_enrolled"], 1)
        s2_enrolled = max(data["s2_enrolled"], 1)
        s1_rate = data["s1_approved"] / s1_enrolled
        s2_rate = data["s2_approved"] / s2_enrolled
        input_df["approval_momentum"] = s2_rate - s1_rate
    if "total_approved" in feature_names:
        input_df["total_approved"] = data["s1_approved"] + data["s2_approved"]
    if "avg_grade" in feature_names:
        input_df["avg_grade"] = (data["s1_grade"] + data["s2_grade"]) / 2
    if "eval_to_approval_ratio" in feature_names:
        total_eval = max(data["s1_evaluations"] + data["s2_evaluations"], 1)
        total_approved = data["s1_approved"] + data["s2_approved"]
        input_df["eval_to_approval_ratio"] = total_approved / total_eval

    return input_df


@router.post("/", response_model=PredictionResponse)
async def predict_single(student: StudentInput):
    """
    Predict dropout risk for a single student.

    Returns risk score (0-1), risk tier classification, and logs to database.
    """
    try:
        input_df = student_to_dataframe(student)
        prob = float(model.predict_proba(input_df)[0][1])
        tier = get_risk_tier(prob)
        tier_info = RiskTierInfo(**{k: v for k, v in tier.items() if k != "min" and k != "max"})

        # Log to database
        pred_id = log_prediction(
            input_data=student.model_dump(),
            risk_score=prob,
            risk_tier=tier["tier"],
        )

        return PredictionResponse(
            risk_score=round(prob, 4),
            risk_tier=tier_info,
            prediction_id=pred_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/batch", response_model=BatchResponse)
async def predict_batch(batch: BatchInput):
    """
    Predict dropout risk for a batch of students (up to 500).

    Returns individual predictions and aggregate summary.
    """
    try:
        predictions = []
        risk_scores = []

        for i, student in enumerate(batch.students):
            input_df = student_to_dataframe(student)
            prob = float(model.predict_proba(input_df)[0][1])
            tier = get_risk_tier(prob)
            tier_info = RiskTierInfo(**{k: v for k, v in tier.items() if k != "min" and k != "max"})

            predictions.append(
                BatchPredictionItem(index=i, risk_score=round(prob, 4), risk_tier=tier_info)
            )
            risk_scores.append(prob)

            # Log each prediction
            log_prediction(
                input_data=student.model_dump(),
                risk_score=prob,
                risk_tier=tier["tier"],
                prediction_type="batch",
            )

        # Summary statistics
        risk_arr = np.array(risk_scores)
        tier_counts = {}
        for p in predictions:
            t = p.risk_tier.tier
            tier_counts[t] = tier_counts.get(t, 0) + 1

        summary = {
            "avg_risk": round(float(risk_arr.mean()), 4),
            "median_risk": round(float(np.median(risk_arr)), 4),
            "std_risk": round(float(risk_arr.std()), 4),
            "min_risk": round(float(risk_arr.min()), 4),
            "max_risk": round(float(risk_arr.max()), 4),
            "tier_distribution": tier_counts,
            "pct_high_risk": round(float((risk_arr > 0.5).mean()), 4),
        }

        return BatchResponse(total=len(predictions), predictions=predictions, summary=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")
