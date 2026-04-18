"""
Pydantic Schemas for the Student Dropout Risk Assessment API.

Defines request/response models with strict validation,
field descriptions, and example values for auto-generated docs.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ──────────────────────────────────────────────
# Request Schemas
# ──────────────────────────────────────────────

class StudentInput(BaseModel):
    """Complete student profile input for risk prediction."""

    marital_status: int = Field(default=1, ge=1, le=6, description="1=Single, 2=Married, 3=Widowed, 4=Divorced, 5=Facto union, 6=Legally separated")
    application_mode: int = Field(default=1, ge=1, le=57, description="Application mode code")
    application_order: int = Field(default=1, ge=0, le=9, description="Application order (0=first choice)")
    course: int = Field(default=33, description="Course code")
    attendance: int = Field(default=1, ge=0, le=1, description="1=Daytime, 0=Evening")
    prev_qualification: int = Field(default=1, description="Previous qualification code")
    prev_qualification_grade: float = Field(default=120.0, ge=0, le=200, description="Previous qualification grade")
    nationality: int = Field(default=1, description="Nationality code")
    mothers_qualification: int = Field(default=1, description="Mother's qualification code")
    fathers_qualification: int = Field(default=1, description="Father's qualification code")
    mothers_occupation: int = Field(default=1, description="Mother's occupation code")
    fathers_occupation: int = Field(default=1, description="Father's occupation code")
    admission_grade: float = Field(default=120.0, ge=0, le=200, description="Admission grade (0-200)")
    displaced: int = Field(default=0, ge=0, le=1, description="1=Displaced, 0=Not displaced")
    special_needs: int = Field(default=0, ge=0, le=1, description="1=Has special needs")
    debtor: int = Field(default=0, ge=0, le=1, description="1=Has debt")
    tuition_up_to_date: int = Field(default=1, ge=0, le=1, description="1=Tuition paid, 0=Not paid")
    gender: int = Field(default=1, ge=0, le=1, description="1=Male, 0=Female")
    scholarship_holder: int = Field(default=0, ge=0, le=1, description="1=Has scholarship")
    age_at_enrollment: int = Field(default=20, ge=15, le=70, description="Age at enrollment")
    international: int = Field(default=0, ge=0, le=1, description="1=International student")
    s1_credited: int = Field(default=0, ge=0, le=30, description="S1 credited units")
    s1_enrolled: int = Field(default=6, ge=0, le=30, description="S1 enrolled units")
    s1_evaluations: int = Field(default=6, ge=0, le=50, description="S1 evaluation count")
    s1_approved: int = Field(default=5, ge=0, le=30, description="S1 approved units")
    s1_grade: float = Field(default=12.0, ge=0, le=20, description="S1 average grade (0-20)")
    s1_without_evaluations: int = Field(default=0, ge=0, le=20, description="S1 units without evaluations")
    s2_credited: int = Field(default=0, ge=0, le=30, description="S2 credited units")
    s2_enrolled: int = Field(default=6, ge=0, le=30, description="S2 enrolled units")
    s2_evaluations: int = Field(default=6, ge=0, le=50, description="S2 evaluation count")
    s2_approved: int = Field(default=5, ge=0, le=30, description="S2 approved units")
    s2_grade: float = Field(default=12.0, ge=0, le=20, description="S2 average grade (0-20)")
    s2_without_evaluations: int = Field(default=0, ge=0, le=20, description="S2 units without evaluations")
    unemployment_rate: float = Field(default=10.0, description="Regional unemployment rate")
    inflation_rate: float = Field(default=1.5, description="Regional inflation rate")
    gdp: float = Field(default=1.5, description="Regional GDP growth rate")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
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
            ]
        }
    }


class SimulationRequest(BaseModel):
    """Request for what-if simulation: base student + modifications."""

    student: StudentInput
    modifications: dict = Field(
        ...,
        description="Dict of field_name: new_value to simulate. Use '+N' or '-N' strings for relative changes.",
        examples=[{"tuition_up_to_date": 1, "s2_approved": "+3", "s2_grade": "+2.0"}],
    )


class BatchInput(BaseModel):
    """Batch prediction request."""

    students: list[StudentInput] = Field(..., min_length=1, max_length=500)


# ──────────────────────────────────────────────
# Response Schemas
# ──────────────────────────────────────────────

class RiskTierInfo(BaseModel):
    """Risk tier classification details."""

    tier: str
    color: str
    emoji: str
    action: str


class PredictionResponse(BaseModel):
    """Full prediction response with risk assessment."""

    risk_score: float
    risk_tier: RiskTierInfo
    prediction_id: Optional[int] = None


class ExplanationResponse(BaseModel):
    """SHAP-based explanation of a prediction."""

    risk_score: float
    risk_tier: RiskTierInfo
    base_value: float
    risk_factors: list[dict]
    protective_factors: list[dict]
    natural_language_summary: str
    all_contributions: list[dict]


class SimulationResponse(BaseModel):
    """What-if simulation result."""

    current_risk_score: float
    current_risk_tier: RiskTierInfo
    simulated_risk_score: float
    simulated_risk_tier: RiskTierInfo
    improvement_potential: float
    modifications_applied: dict


class BatchPredictionItem(BaseModel):
    """Single item in a batch prediction response."""

    index: int
    risk_score: float
    risk_tier: RiskTierInfo


class BatchResponse(BaseModel):
    """Batch prediction response."""

    total: int
    predictions: list[BatchPredictionItem]
    summary: dict


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model_loaded: bool
    explainer_loaded: bool
    database_connected: bool
    timestamp: str


class ModelInfoResponse(BaseModel):
    """Model metadata and performance info."""

    model_type: str
    n_features: int
    feature_names: list[str]
    training_metrics: Optional[dict] = None
    model_comparison: Optional[dict] = None
    trained_at: Optional[str] = None
