# Student Dropout Risk Assessment

An **AI-powered early warning system** that predicts student dropout risk using machine learning, provides SHAP-based explainability, and offers what-if simulation for intervention planning.

> **Built with:** Python · FastAPI · Streamlit · XGBoost · SHAP · Plotly · SQLite · Docker

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Model ML Pipeline** | Compares RandomForest, XGBoost, and GradientBoosting with hyperparameter tuning |
| **SHAP Explainability** | Per-prediction explanations — know *why* a student is at risk |
| **What-If Simulator** | Test intervention scenarios: "What if they pay tuition?" |
| **Batch Cohort Analysis** | Upload a CSV, analyze an entire class at once |
| **Sensitivity Analysis** | Find the single best action to help each student |
| **Prediction History** | SQLite-backed logging with trend analysis |
| **REST API** | 11 production-grade endpoints with auto-generated docs |
| **Premium Dashboard** | 4-page Streamlit UI with Plotly charts and dark theme |
| **Docker Deployment** | One-command deployment with Docker Compose |

---

## Architecture

```
├── config/settings.py          # Centralized configuration
├── models/
│   ├── train_pipeline.py       # Multi-model training with SMOTE & CV
│   ├── explainer.py            # SHAP explainability engine
│   └── artifacts/              # Saved models & metrics
├── api/
│   ├── main.py                 # FastAPI application
│   ├── schemas.py              # Pydantic request/response models
│   ├── database.py             # SQLite prediction logging
│   └── routes/
│       ├── predict.py          # Single & batch predictions
│       ├── explain.py          # SHAP explanations
│       ├── simulate.py         # What-if & sensitivity analysis
│       └── analytics.py        # Model info & prediction history
├── dashboard/
│   ├── app.py                  # Main Streamlit dashboard
│   ├── pages/                  # Multi-page navigation
│   │   ├── 1_Individual_Risk.py
│   │   ├── 2_Batch_Analysis.py
│   │   ├── 3_What_If.py
│   │   └── 4_Model_Insights.py
│   └── components/             # Reusable UI components
│       ├── risk_gauge.py       # Plotly animated gauge
│       ├── shap_chart.py       # SHAP waterfall charts
│       └── theme.py            # Premium dark theme CSS
├── tests/                      # Pytest test suite
├── docker-compose.yml          # Container orchestration
└── requirements.txt            # Dependencies
```

---

##  Quick Start

### Prerequisites
- Python 3.10+
- pip

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Train the Model
```bash
python -m models.train_pipeline
```
This will:
- Fetch the UCI dataset (ID 697)
- Engineer 7 derived features
- Compare 3 models with hyperparameter tuning
- Apply SMOTE for class balance
- Save the best model + SHAP explainer + metrics

### 3. Start the API
```bash
python -m api.main
```
API runs at `http://localhost:8000` — interactive docs at `/docs`

### 4. Start the Dashboard
```bash
streamlit run dashboard/app.py
```
Dashboard runs at `http://localhost:8501`

### 5. Run Tests
```bash
pytest tests/ -v
```

---

##  Docker Deployment

```bash
docker-compose up --build
```

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Dashboard | http://localhost:8501 |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/predict/` | Single student risk prediction |
| `POST` | `/predict/batch` | Batch predictions (up to 500) |
| `POST` | `/explain/` | SHAP-based explanation |
| `GET` | `/explain/global-importance` | Global feature importance |
| `POST` | `/simulate/` | What-if scenario simulation |
| `GET` | `/simulate/presets` | Available scenario presets |
| `POST` | `/simulate/sensitivity` | Automated sensitivity analysis |
| `GET` | `/analytics/health` | System health check |
| `GET` | `/analytics/model-info` | Model metadata & metrics |
| `GET` | `/analytics/history` | Prediction history |
| `GET` | `/analytics/summary` | Aggregate analytics |

---

## ML Pipeline Details

### Dataset
- **Source**: [UCI ML Repository — Predict Students' Dropout and Academic Success](https://archive.ics.uci.edu/dataset/697)
- **Size**: 4,424 students × 36 features
- **Target**: Binary (Dropout vs. Graduate/Enrolled)
- **Class Balance**: ~32% dropout (addressed with SMOTE)

### Feature Engineering
| Feature | Formula | Rationale |
|---------|---------|-----------|
| `grade_trend` | S2 Grade − S1 Grade | Captures academic trajectory |
| `s1_approval_rate` | S1 Approved / S1 Enrolled | Semester 1 success rate |
| `s2_approval_rate` | S2 Approved / S2 Enrolled | Semester 2 success rate |
| `approval_momentum` | S2 Rate − S1 Rate | Direction of change |
| `total_approved` | S1 + S2 Approved | Overall academic output |
| `avg_grade` | (S1 + S2 Grade) / 2 | Average performance |
| `eval_to_approval_ratio` | Total Approved / Total Evaluations | Effort vs. outcome |

### Model Comparison
Models are compared using:
- **Stratified 5-Fold Cross-Validation**
- **RandomizedSearchCV** for hyperparameter tuning
- **F1 Score** as the primary metric (handles class imbalance)
- **SMOTE** applied to training set only

---

## Dashboard Pages

### 1. Individual Risk Assessment
- Animated Plotly risk gauge
- SHAP waterfall chart (top contributing factors)
- Risk tier badge with recommended actions
- Natural language AI explanation

### 2. Batch Cohort Analysis
- CSV upload for entire class analysis
- Risk distribution histogram with box plot
- Interactive scatter plot (risk vs. grade)
- Downloadable results

### 3. What-If Simulator
- Custom scenario builder with sliders
- Pre-built intervention presets
- Automated sensitivity analysis
- Side-by-side gauge comparison

### 4. Model Insights
- Multi-model comparison chart
- Cross-validation box plots
- Confusion matrix heatmap
- Classification report
- Prediction history & analytics

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| ML | scikit-learn, XGBoost, SHAP | Model training & explainability |
| API | FastAPI, Pydantic, Uvicorn | REST API with validation |
| UI | Streamlit, Plotly | Interactive dashboard |
| DB | SQLite | Prediction history |
| Infra | Docker, Docker Compose | Containerized deployment |
| Testing | pytest, httpx | Automated test suite |

---

## License

This project is for educational and portfolio purposes.

---

## References

1. Realinho, V., Machado, J., Baptista, L., & Martins, M.V. (2022). Predicting Student Dropout and Academic Success. *Data*, 7(11), 146.
2. Lundberg, S.M. & Lee, S.I. (2017). A Unified Approach to Interpreting Model Predictions. *NeurIPS*.
3. UCI Machine Learning Repository — Dataset ID 697.
