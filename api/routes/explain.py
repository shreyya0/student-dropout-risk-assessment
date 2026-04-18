"""
Explanation Routes — SHAP-based explainability for predictions.
"""

import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config.settings import get_risk_tier
from api.schemas import ExplanationResponse, RiskTierInfo, StudentInput
from api.routes.predict import model, student_to_dataframe
from models.explainer import RiskExplainer

router = APIRouter(prefix="/explain", tags=["Explainability"])

# Initialize explainer (lazy load)
_explainer = None


def get_explainer():
    global _explainer
    if _explainer is None:
        _explainer = RiskExplainer()
    return _explainer


@router.post("/", response_model=ExplanationResponse)
async def explain_prediction(student: StudentInput, top_n: int = 5):
    """
    Get SHAP-based explanation for a student's risk prediction.

    Returns risk factors, protective factors, SHAP values, and a
    natural language summary explaining why the student is at risk.
    """
    try:
        explainer = get_explainer()
        input_df = student_to_dataframe(student)

        # Get prediction
        prob = float(model.predict_proba(input_df)[0][1])
        tier = get_risk_tier(prob)
        tier_info = RiskTierInfo(**{k: v for k, v in tier.items() if k != "min" and k != "max"})

        # Get SHAP explanation
        explanation = explainer.explain(input_df, top_n=top_n)

        return ExplanationResponse(
            risk_score=round(prob, 4),
            risk_tier=tier_info,
            base_value=explanation["base_value"],
            risk_factors=explanation["risk_factors"],
            protective_factors=explanation["protective_factors"],
            natural_language_summary=explanation["natural_language_summary"],
            all_contributions=explanation["all_contributions"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")


@router.get("/global-importance")
async def global_feature_importance():
    """
    Get global feature importance ranking based on SHAP values.

    Returns features sorted by their average absolute SHAP impact.
    """
    try:
        explainer = get_explainer()
        importance = explainer.global_importance()
        return {"feature_importance": importance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature importance failed: {str(e)}")
