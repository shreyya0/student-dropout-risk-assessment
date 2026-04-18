"""
Advanced ML Training Pipeline for Student Dropout Risk Prediction.

This pipeline implements:
- Data fetching from UCI ML Repository (Dataset 697)
- Feature engineering (grade trends, approval rates, academic momentum)
- Multi-model comparison (RandomForest, XGBoost, GradientBoosting)
- Hyperparameter tuning via RandomizedSearchCV
- SMOTE for class imbalance handling
- Stratified K-Fold cross-validation
- SHAP explainability artifacts
- Comprehensive metrics export (JSON)

Usage:
    python -m models.train_pipeline
"""

import json
import time
import warnings
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
    cross_val_score,
    train_test_split,
)
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE

warnings.filterwarnings("ignore", category=UserWarning)

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import (
    CV_FOLDS,
    EXPLAINER_PATH,
    FEATURE_NAMES_PATH,
    MODEL_COMPARISON_PATH,
    MODEL_PATH,
    MODELS_DIR,
    N_ITER_SEARCH,
    RANDOM_STATE,
    TEST_SIZE,
    TRAINING_METRICS_PATH,
    UCI_DATASET_ID,
)


def fetch_dataset() -> tuple[pd.DataFrame, pd.Series]:
    """Fetch the UCI Student Dropout dataset and prepare binary target."""
    from ucimlrepo import fetch_ucirepo

    print("📡 Fetching dataset from UCI ML Repository (ID 697)...")
    dataset = fetch_ucirepo(id=UCI_DATASET_ID)
    X = dataset.data.features
    y = dataset.data.targets

    # Binary target: 1 = Dropout (at risk), 0 = Graduate/Enrolled (safe)
    y_binary = y["Target"].apply(lambda x: 1 if x == "Dropout" else 0)

    print(f"   ✅ Loaded {X.shape[0]} students, {X.shape[1]} features")
    print(f"   📊 Class distribution: {dict(y_binary.value_counts())}")
    print(f"   ⚖️  Dropout rate: {y_binary.mean():.1%}")

    return X, y_binary


def engineer_features(X: pd.DataFrame) -> pd.DataFrame:
    """Create derived features that capture academic trajectory and momentum."""
    X = X.copy()

    # Grade trend: improvement or decline between semesters
    X["grade_trend"] = (
        X["Curricular units 2nd sem (grade)"] - X["Curricular units 1st sem (grade)"]
    )

    # Approval rate per semester
    s1_enrolled = X["Curricular units 1st sem (enrolled)"].replace(0, 1)
    s2_enrolled = X["Curricular units 2nd sem (enrolled)"].replace(0, 1)
    X["s1_approval_rate"] = X["Curricular units 1st sem (approved)"] / s1_enrolled
    X["s2_approval_rate"] = X["Curricular units 2nd sem (approved)"] / s2_enrolled

    # Academic momentum: change in approval rate
    X["approval_momentum"] = X["s2_approval_rate"] - X["s1_approval_rate"]

    # Total units approved across both semesters
    X["total_approved"] = (
        X["Curricular units 1st sem (approved)"]
        + X["Curricular units 2nd sem (approved)"]
    )

    # Average grade across semesters
    X["avg_grade"] = (
        X["Curricular units 1st sem (grade)"] + X["Curricular units 2nd sem (grade)"]
    ) / 2

    # Evaluation-to-approval ratio (effort vs outcome)
    total_eval = (
        X["Curricular units 1st sem (evaluations)"]
        + X["Curricular units 2nd sem (evaluations)"]
    ).replace(0, 1)
    X["eval_to_approval_ratio"] = X["total_approved"] / total_eval

    print(f"   🔧 Engineered 7 new features → {X.shape[1]} total features")
    return X


def get_model_configs() -> dict:
    """Return model configurations with hyperparameter search spaces."""
    return {
        "RandomForest": {
            "model": RandomForestClassifier(random_state=RANDOM_STATE),
            "params": {
                "n_estimators": [100, 200, 300, 500],
                "max_depth": [10, 15, 20, 25, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
                "max_features": ["sqrt", "log2"],
            },
        },
        "XGBoost": {
            "model": XGBClassifier(
                random_state=RANDOM_STATE,
                eval_metric="logloss",
                use_label_encoder=False,
            ),
            "params": {
                "n_estimators": [100, 200, 300, 500],
                "max_depth": [3, 5, 7, 10],
                "learning_rate": [0.01, 0.05, 0.1, 0.2],
                "subsample": [0.7, 0.8, 0.9, 1.0],
                "colsample_bytree": [0.7, 0.8, 0.9, 1.0],
                "min_child_weight": [1, 3, 5],
                "gamma": [0, 0.1, 0.2],
            },
        },
        "GradientBoosting": {
            "model": GradientBoostingClassifier(random_state=RANDOM_STATE),
            "params": {
                "n_estimators": [100, 200, 300],
                "max_depth": [3, 5, 7],
                "learning_rate": [0.01, 0.05, 0.1, 0.2],
                "subsample": [0.7, 0.8, 0.9, 1.0],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
            },
        },
    }


def train_and_compare(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    """Train multiple models with hyperparameter tuning and compare performance."""
    configs = get_model_configs()
    results = {}
    best_score = 0
    best_model = None
    best_name = None

    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    for name, config in configs.items():
        print(f"\n{'='*60}")
        print(f"🏋️  Training {name}...")
        print(f"{'='*60}")

        start_time = time.time()

        # Randomized search with cross-validation
        search = RandomizedSearchCV(
            config["model"],
            config["params"],
            n_iter=min(N_ITER_SEARCH, 30),  # Cap for speed
            cv=cv,
            scoring="f1",
            random_state=RANDOM_STATE,
            n_jobs=-1,
            verbose=0,
        )
        search.fit(X_train, y_train)

        train_time = time.time() - start_time

        # Evaluate on test set
        model = search.best_estimator_
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        # Cross-validation scores on full training set
        cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="f1")

        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "f1_score": float(f1_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred)),
            "recall": float(recall_score(y_test, y_pred)),
            "roc_auc": float(roc_auc_score(y_test, y_prob)),
            "cv_f1_mean": float(cv_scores.mean()),
            "cv_f1_std": float(cv_scores.std()),
            "cv_scores": cv_scores.tolist(),
            "best_params": search.best_params_,
            "train_time_seconds": round(train_time, 2),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            "classification_report": classification_report(y_test, y_pred, output_dict=True),
        }

        results[name] = {"model": model, "metrics": metrics}

        print(f"   ⏱️  Training time: {train_time:.1f}s")
        print(f"   📊 Accuracy:  {metrics['accuracy']:.4f}")
        print(f"   📊 F1 Score:  {metrics['f1_score']:.4f}")
        print(f"   📊 ROC AUC:   {metrics['roc_auc']:.4f}")
        print(f"   📊 CV F1:     {metrics['cv_f1_mean']:.4f} ± {metrics['cv_f1_std']:.4f}")
        print(f"   🔧 Best params: {search.best_params_}")

        if metrics["f1_score"] > best_score:
            best_score = metrics["f1_score"]
            best_model = model
            best_name = name

    print(f"\n{'='*60}")
    print(f"🏆 Best Model: {best_name} (F1: {best_score:.4f})")
    print(f"{'='*60}")

    return results, best_model, best_name


def save_artifacts(
    model,
    best_name: str,
    feature_names: list,
    results: dict,
    X_train: pd.DataFrame,
):
    """Save model, feature names, SHAP explainer, and metrics."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Save model
    joblib.dump(model, MODEL_PATH)
    print(f"   💾 Model saved: {MODEL_PATH}")

    # Save feature names
    joblib.dump(feature_names, FEATURE_NAMES_PATH)
    print(f"   💾 Feature names saved: {FEATURE_NAMES_PATH}")

    # Save SHAP explainer
    try:
        import shap
        print("   🔍 Building SHAP explainer (this may take a moment)...")
        explainer = shap.TreeExplainer(model)
        joblib.dump(explainer, EXPLAINER_PATH)
        print(f"   💾 SHAP explainer saved: {EXPLAINER_PATH}")
    except Exception as e:
        print(f"   ⚠️  SHAP explainer failed: {e}")

    # Save training metrics
    metrics_export = {
        "best_model": best_name,
        "trained_at": datetime.now().isoformat(),
        "n_features": len(feature_names),
        "feature_names": feature_names,
    }
    for name, data in results.items():
        metrics_export[name] = data["metrics"]

    with open(TRAINING_METRICS_PATH, "w") as f:
        json.dump(metrics_export, f, indent=2, default=str)
    print(f"   💾 Metrics saved: {TRAINING_METRICS_PATH}")

    # Save model comparison summary
    comparison = {}
    for name, data in results.items():
        m = data["metrics"]
        comparison[name] = {
            "accuracy": m["accuracy"],
            "f1_score": m["f1_score"],
            "precision": m["precision"],
            "recall": m["recall"],
            "roc_auc": m["roc_auc"],
            "cv_f1_mean": m["cv_f1_mean"],
            "cv_f1_std": m["cv_f1_std"],
            "train_time_seconds": m["train_time_seconds"],
        }
    with open(MODEL_COMPARISON_PATH, "w") as f:
        json.dump(comparison, f, indent=2)
    print(f"   💾 Model comparison saved: {MODEL_COMPARISON_PATH}")


def main():
    """Execute the full training pipeline."""
    print("\n" + "=" * 60)
    print("🚀 STUDENT RISK PREDICTION — TRAINING PIPELINE")
    print("=" * 60)

    # Step 1: Fetch data
    X, y = fetch_dataset()

    # Step 2: Feature engineering
    print("\n📐 Engineering features...")
    X = engineer_features(X)

    # Step 3: Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"\n📂 Split: {len(X_train)} train / {len(X_test)} test")

    # Step 4: SMOTE oversampling on training set only
    print("\n⚖️  Applying SMOTE for class balance...")
    smote = SMOTE(random_state=RANDOM_STATE)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    print(f"   Before SMOTE: {dict(y_train.value_counts())}")
    print(f"   After SMOTE:  {dict(pd.Series(y_train_resampled).value_counts())}")

    # Step 5: Train and compare models
    results, best_model, best_name = train_and_compare(
        X_train_resampled, y_train_resampled, X_test, y_test
    )

    # Step 6: Save all artifacts
    print("\n💾 Saving artifacts...")
    feature_names = X.columns.tolist()
    save_artifacts(best_model, best_name, feature_names, results, X_train)

    # Step 7: Generate sample data for batch demo
    print("\n📋 Generating sample batch data...")
    sample = X_test.head(50).copy()
    sample.to_csv(Path(__file__).resolve().parent.parent / "data" / "sample_students.csv", index=False)
    print("   💾 Sample data saved: data/sample_students.csv")

    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
