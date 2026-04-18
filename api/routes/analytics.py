"""
Analytics Routes — Model info, prediction history, and aggregate stats.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config.settings import MODEL_PATH, TRAINING_METRICS_PATH, MODEL_COMPARISON_PATH, FEATURE_NAMES_PATH
from api.schemas import HealthResponse, ModelInfoResponse
from api.database import get_analytics_summary, get_prediction_history

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint — verifies all components are operational."""
    import joblib
    from config.settings import EXPLAINER_PATH, DB_PATH

    model_ok = MODEL_PATH.exists()
    explainer_ok = EXPLAINER_PATH.exists()
    db_ok = DB_PATH.exists()

    return HealthResponse(
        status="healthy" if all([model_ok, explainer_ok, db_ok]) else "degraded",
        model_loaded=model_ok,
        explainer_loaded=explainer_ok,
        database_connected=db_ok,
        timestamp=datetime.now().isoformat(),
    )


@router.get("/model-info", response_model=ModelInfoResponse)
async def get_model_info():
    """Get model metadata, performance metrics, and comparison results."""
    import joblib

    try:
        model = joblib.load(MODEL_PATH)
        feature_names = joblib.load(FEATURE_NAMES_PATH)

        training_metrics = None
        if TRAINING_METRICS_PATH.exists():
            with open(TRAINING_METRICS_PATH) as f:
                training_metrics = json.load(f)

        model_comparison = None
        if MODEL_COMPARISON_PATH.exists():
            with open(MODEL_COMPARISON_PATH) as f:
                model_comparison = json.load(f)

        return ModelInfoResponse(
            model_type=type(model).__name__,
            n_features=len(feature_names),
            feature_names=feature_names,
            training_metrics=training_metrics,
            model_comparison=model_comparison,
            trained_at=training_metrics.get("trained_at") if training_metrics else None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model info failed: {str(e)}")


@router.get("/history")
async def prediction_history(
    limit: int = Query(default=100, le=1000),
    risk_tier: str = Query(default=None, description="Filter by risk tier"),
    prediction_type: str = Query(default=None, description="Filter: single, batch, simulation"),
):
    """Retrieve prediction history with optional filters."""
    try:
        history = get_prediction_history(
            limit=limit, risk_tier=risk_tier, prediction_type=prediction_type
        )
        return {"total": len(history), "predictions": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")


@router.get("/summary")
async def analytics_summary():
    """Get aggregate analytics from all predictions."""
    try:
        summary = get_analytics_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")
