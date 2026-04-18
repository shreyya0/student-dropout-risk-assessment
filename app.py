import streamlit as st
import requests

st.set_page_config(page_title="AI Risk Optimizer", layout="wide")
st.title("🚀 Student Success Optimizer")

with st.sidebar:
    st.header("Input Parameters")
    tuition = st.selectbox("Tuition Paid?", [0, 1])
    scholarship = st.selectbox("Scholarship?", [0, 1])
    age = st.slider("Age", 18, 60, 20)
    s1_app = st.number_input("S1 Approved Units", 0, 20, 5)
    s1_grd = st.number_input("S1 Grade", 0.0, 20.0, 10.0)
    s2_app = st.number_input("S2 Approved Units", 0, 20, 5)
    s2_grd = st.number_input("S2 Grade", 0.0, 20.0, 10.0)

if st.button("Run Full Diagnostic"):
    payload = {
        "tuition_up_to_date": tuition,
        "scholarship_holder": scholarship,
        "age_at_enrollment": age,
        "s1_approved": s1_app,
        "s1_grade": s1_grd,
        "s2_approved": s2_app,
        "s2_grade": s2_grd
    }
    
    res = requests.post("http://localhost:8000/predict", json=payload)
    
    if res.status_code == 200:
        data = res.json()
        current_risk = data['risk_score']
        sim_risk = data['simulated_risk_score']
        
        # Display Metrics
        col1, col2 = st.columns(2)
        col1.metric("Current Risk", f"{current_risk:.1%}", delta_color="inverse")
        col2.metric("Simulated Risk (+2 units)", f"{sim_risk:.1%}", 
                   delta=f"-{(current_risk - sim_risk):.1%}", delta_color="normal")
        
        st.subheader("💡 Prescriptive Recommendation")
        if current_risk > 0.5:
            st.error(f"Critical: If this student completes 2 additional units, their risk drops by {(current_risk - sim_risk):.1%}. Intervention recommended.")
        else:
            st.success("Student is on a stable path.")
    else:
        st.error(f"Validation Error: {res.text}")