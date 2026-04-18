"""
SQLite Database Layer for Prediction History & Analytics.

Logs every prediction with inputs, outputs, SHAP factors, and timestamps.
Supports trend analysis and cohort-level queries.
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import DB_PATH


def init_db():
    """Create the database and tables if they don't exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                input_data TEXT NOT NULL,
                risk_score REAL NOT NULL,
                risk_tier TEXT NOT NULL,
                simulated_risk_score REAL,
                improvement_potential REAL,
                top_risk_factors TEXT,
                top_protective_factors TEXT,
                prediction_type TEXT DEFAULT 'single',
                session_id TEXT
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON predictions(timestamp)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_risk_tier ON predictions(risk_tier)
        """)
        conn.commit()


@contextmanager
def get_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def log_prediction(
    input_data: dict,
    risk_score: float,
    risk_tier: str,
    simulated_risk_score: float = None,
    improvement_potential: float = None,
    top_risk_factors: list = None,
    top_protective_factors: list = None,
    prediction_type: str = "single",
    session_id: str = None,
) -> int:
    """Log a prediction to the database. Returns the prediction ID."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO predictions (
                timestamp, input_data, risk_score, risk_tier,
                simulated_risk_score, improvement_potential,
                top_risk_factors, top_protective_factors,
                prediction_type, session_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(),
                json.dumps(input_data),
                risk_score,
                risk_tier,
                simulated_risk_score,
                improvement_potential,
                json.dumps(top_risk_factors) if top_risk_factors else None,
                json.dumps(top_protective_factors) if top_protective_factors else None,
                prediction_type,
                session_id,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def get_prediction_history(
    limit: int = 100, risk_tier: str = None, prediction_type: str = None
) -> list[dict]:
    """Retrieve prediction history with optional filters."""
    query = "SELECT * FROM predictions WHERE 1=1"
    params = []

    if risk_tier:
        query += " AND risk_tier = ?"
        params.append(risk_tier)
    if prediction_type:
        query += " AND prediction_type = ?"
        params.append(prediction_type)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_analytics_summary() -> dict:
    """Get aggregate analytics from prediction history."""
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
        if total == 0:
            return {"total_predictions": 0, "tier_distribution": {}, "avg_risk_score": 0}

        avg_risk = conn.execute("SELECT AVG(risk_score) FROM predictions").fetchone()[0]

        tier_rows = conn.execute(
            "SELECT risk_tier, COUNT(*) as count FROM predictions GROUP BY risk_tier"
        ).fetchall()
        tier_dist = {row["risk_tier"]: row["count"] for row in tier_rows}

        recent = conn.execute(
            "SELECT AVG(risk_score) as avg_risk, timestamp FROM predictions "
            "ORDER BY timestamp DESC LIMIT 50"
        ).fetchone()

        return {
            "total_predictions": total,
            "avg_risk_score": round(float(avg_risk), 4),
            "tier_distribution": tier_dist,
            "recent_avg_risk": round(float(recent["avg_risk"]), 4) if recent else 0,
        }


# Initialize database on import
init_db()
