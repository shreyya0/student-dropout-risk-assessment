from fastapi import FastAPI
from pydantic import BaseModel, Field # Added Field for validation
import joblib
import pandas as pd
import numpy as np

app = FastAPI(title="Proactive Student Risk API")

model = joblib.load('student_risk_model.pkl')
feature_names = joblib.load('feature_names.pkl')

# ENHANCED: Pydantic Schema with strict validation
class StudentData(BaseModel):
    tuition_up_to_date: int = Field(..., ge=0, le=1, description="Must be 0 or 1")
    scholarship_holder: int = Field(..., ge=0, le=1)
    age_at_enrollment: int = Field(..., ge=15, le=100)
    s1_approved: int = Field(..., ge=0, le=30)
    s1_grade: float = Field(..., ge=0, le=20)
    s2_approved: int = Field(..., ge=0, le=30)
    s2_grade: float = Field(..., ge=0, le=20)

@app.post("/predict")
def predict_risk(data: StudentData):
    input_df = pd.DataFrame(np.zeros((1, len(feature_names))), columns=feature_names)
    
    # Current State
    input_df['Tuition fees up to date'] = data.tuition_up_to_date
    input_df['Scholarship holder'] = data.scholarship_holder
    input_df['Age at enrollment'] = data.age_at_enrollment
    input_df['Curricular units 1st sem (approved)'] = data.s1_approved
    input_df['Curricular units 1st sem (grade)'] = data.s1_grade
    input_df['Curricular units 2nd sem (approved)'] = data.s2_approved
    input_df['Curricular units 2nd sem (grade)'] = data.s2_grade
    
    prob = model.predict_proba(input_df)[0][1]
    
    # NEW SIMULATION: "Total Academic Recovery"
    # We simulate +2 units AND a +5 point grade increase
    input_df_sim = input_df.copy()
    input_df_sim['Curricular units 2nd sem (approved)'] += 2
    input_df_sim['Curricular units 2nd sem (grade)'] = min(20, input_df_sim['Curricular units 2nd sem (grade)'] + 5)
    
    sim_prob = model.predict_proba(input_df_sim)[0][1]
    
    return {
        "risk_score": float(prob),
        "simulated_risk_score": float(sim_prob),
        "improvement_potential": float(prob - sim_prob)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)