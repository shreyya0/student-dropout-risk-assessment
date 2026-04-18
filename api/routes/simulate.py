"""
Simulation Routes — What-If scenario analysis.
"""

import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config.settings import FEATURE_MAP, SCENARIO_PRESETS, get_risk_tier
from api.schemas import (
    RiskTierInfo,
    SimulationRequest,
    SimulationResponse,
    StudentInput,
)
from api.routes.predict import model, student_to_dataframe
from api.database import log_prediction

router = APIRouter(prefix="/simulate", tags=["Simulation"])


@router.post("/", response_model=SimulationResponse)
async def simulate_whatif(request: SimulationRequest):
    """
    Run a what-if simulation.

    Accepts a base student profile and a dict of modifications.
    Modifications can be absolute values or relative changes ('+3', '-2.5').
    Returns current vs simulated risk comparison.
    """
    try:
        # Current prediction
        current_df = student_to_dataframe(request.student)
        current_prob = float(model.predict_proba(current_df)[0][1])
        current_tier = get_risk_tier(current_prob)

        # Apply modifications to create simulated student
        sim_data = request.student.model_dump()
        applied_mods = {}

        for field, value in request.modifications.items():
            if field not in sim_data:
                continue

            if isinstance(value, str) and (value.startswith("+") or value.startswith("-")):
                # Relative change
                delta = float(value)
                sim_data[field] = sim_data[field] + delta
                applied_mods[field] = f"{sim_data[field] - delta} → {sim_data[field]} ({value})"
            else:
                # Absolute value
                old_val = sim_data[field]
                sim_data[field] = value
                applied_mods[field] = f"{old_val} → {value}"

        sim_student = StudentInput(**sim_data)
        sim_df = student_to_dataframe(sim_student)
        sim_prob = float(model.predict_proba(sim_df)[0][1])
        sim_tier = get_risk_tier(sim_prob)

        improvement = current_prob - sim_prob

        # Log simulation
        log_prediction(
            input_data=sim_data,
            risk_score=sim_prob,
            risk_tier=sim_tier["tier"],
            simulated_risk_score=sim_prob,
            improvement_potential=improvement,
            prediction_type="simulation",
        )

        current_tier_info = RiskTierInfo(**{k: v for k, v in current_tier.items() if k not in ("min", "max")})
        sim_tier_info = RiskTierInfo(**{k: v for k, v in sim_tier.items() if k not in ("min", "max")})

        return SimulationResponse(
            current_risk_score=round(current_prob, 4),
            current_risk_tier=current_tier_info,
            simulated_risk_score=round(sim_prob, 4),
            simulated_risk_tier=sim_tier_info,
            improvement_potential=round(improvement, 4),
            modifications_applied=applied_mods,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.get("/presets")
async def get_scenario_presets():
    """Get available what-if scenario presets."""
    return {"presets": SCENARIO_PRESETS}


@router.post("/sensitivity")
async def sensitivity_analysis(student: StudentInput):
    """
    Run sensitivity analysis: test each modifiable feature independently
    to find which single change would reduce risk the most.
    """
    try:
        # Current prediction
        current_df = student_to_dataframe(student)
        current_prob = float(model.predict_proba(current_df)[0][1])

        # Test modifications for key features
        sensitivity_tests = {
            "tuition_up_to_date": {"values": [0, 1], "label": "Pay Tuition"},
            "scholarship_holder": {"values": [0, 1], "label": "Get Scholarship"},
            "s2_approved": {"values": ["+1", "+2", "+3", "+5"], "label": "More S2 Approved Units"},
            "s2_grade": {"values": ["+1.0", "+2.0", "+3.0", "+5.0"], "label": "Higher S2 Grade"},
            "s1_approved": {"values": ["+1", "+2", "+3"], "label": "More S1 Approved Units"},
            "s1_grade": {"values": ["+1.0", "+2.0", "+3.0"], "label": "Higher S1 Grade"},
            "debtor": {"values": [0], "label": "Clear Debt"},
        }

        results = []
        base_data = student.model_dump()

        for field, config in sensitivity_tests.items():
            for value in config["values"]:
                sim_data = base_data.copy()
                if isinstance(value, str):
                    sim_data[field] = sim_data[field] + float(value)
                    change_desc = f"{field} {value}"
                else:
                    change_desc = f"{field} = {value}"
                    sim_data[field] = value

                try:
                    sim_student = StudentInput(**sim_data)
                    sim_df = student_to_dataframe(sim_student)
                    sim_prob = float(model.predict_proba(sim_df)[0][1])

                    results.append({
                        "change": change_desc,
                        "label": config["label"],
                        "simulated_risk": round(sim_prob, 4),
                        "improvement": round(current_prob - sim_prob, 4),
                        "improvement_pct": round((current_prob - sim_prob) / max(current_prob, 0.001) * 100, 1),
                    })
                except Exception:
                    continue

        # Sort by improvement (biggest first)
        results.sort(key=lambda x: x["improvement"], reverse=True)

        return {
            "current_risk": round(current_prob, 4),
            "sensitivity_results": results,
            "best_single_action": results[0] if results else None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sensitivity analysis failed: {str(e)}")
