"""
FastAPI Application — Student Dropout Risk Assessment API.

A production-grade REST API for predicting student dropout risk,
with SHAP explainability, what-if simulation, batch processing,
prediction history, and comprehensive model analytics.

Endpoints:
    POST /predict/           — Single student risk prediction
    POST /predict/batch      — Batch predictions (up to 500)
    POST /explain/           — SHAP-based prediction explanation
    GET  /explain/global-importance — Global feature importance
    POST /simulate/          — What-if scenario simulation
    GET  /simulate/presets   — Available scenario presets
    POST /simulate/sensitivity — Automated sensitivity analysis
    GET  /analytics/health   — System health check
    GET  /analytics/model-info — Model metadata & metrics
    GET  /analytics/history  — Prediction history
    GET  /analytics/summary  — Aggregate analytics
"""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.routes import predict, explain, simulate, analytics

# ──────────────────────────────────────────────
# Application
# ──────────────────────────────────────────────

app = FastAPI(
    title="Student Dropout Risk Assessment API",
    description=(
        "An AI-powered early warning system for predicting student dropout risk. "
        "Uses XGBoost/RandomForest with SHAP explainability, what-if simulation, "
        "batch processing, and prediction analytics.\n\n"
        "**Dataset**: UCI ML Repository — Predict Students' Dropout and Academic Success (ID 697)\n\n"
        "**Key Features**:\n"
        "- Per-student risk prediction with confidence scoring\n"
        "- SHAP-based explainability (why is this student at risk?)\n"
        "- What-if simulation (what if we intervene?)\n"
        "- Batch cohort analysis (analyze entire class)\n"
        "- Prediction history & trend analysis\n"
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ──────────────────────────────────────────────
# CORS Middleware
# ──────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Register Routes
# ──────────────────────────────────────────────

app.include_router(predict.router)
app.include_router(explain.router)
app.include_router(simulate.router)
app.include_router(analytics.router)


@app.get("/", tags=["Root"])
async def root():
    """API root — welcome message and links."""
    return {
        "name": "Student Dropout Risk Assessment API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/analytics/health",
        "endpoints": {
            "predict": "/predict/",
            "batch_predict": "/predict/batch",
            "explain": "/explain/",
            "simulate": "/simulate/",
            "sensitivity": "/simulate/sensitivity",
            "model_info": "/analytics/model-info",
            "history": "/analytics/history",
        },
    }


if __name__ == "__main__":
    import uvicorn
    from config.settings import API_HOST, API_PORT

    uvicorn.run(app, host=API_HOST, port=API_PORT)
