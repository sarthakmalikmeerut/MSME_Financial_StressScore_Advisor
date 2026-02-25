

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from src.pipeline import get_store_snapshot, get_msme_score, stress_store
import csv
import os
from datetime import datetime

app = FastAPI(
    title="MSME Financial Stress Score Advisor",
    description=(
        "Real-time financial stress monitoring for MSMEs "
        "powered by Pathway streaming"
    ),
    version="1.0.0",
)

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
)


# ─────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "service": "MSME Financial Stress Score Advisor",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "active_msmes": len(stress_store),
    }


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "ok",
        "pipeline_active": len(stress_store) > 0,
    }


# ─────────────────────────────────────────────
# Get ALL MSME stress scores
# ─────────────────────────────────────────────
@app.get("/scores", tags=["Stress Scores"])
def get_all_scores():
    """Return stress scores for all MSMEs currently tracked."""
    snapshot = get_store_snapshot()
    if not snapshot:
        return JSONResponse(
            status_code=200,
            content={
                "message": (
                    "No scores available yet. "
                    "Pipeline may still be initializing."
                ),
                "scores": {},
            },
        )
    return {
        "count": len(snapshot),
        "scores": snapshot,
        "timestamp": datetime.now().isoformat(),
    }


# ─────────────────────────────────────────────
# Get stress score for a SPECIFIC MSME
# ─────────────────────────────────────────────
@app.get("/scores/{msme_id}", tags=["Stress Scores"])
def get_score(msme_id: str):
    """Return the stress score and details for a specific MSME."""
    result = get_msme_score(msme_id.upper())
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"MSME '{msme_id}' not found. "
                f"Available: {list(stress_store.keys())}"
            ),
        )
    return {
        "msme_id": msme_id.upper(),
        "data": result,
        "timestamp": datetime.now().isoformat(),
    }


# ─────────────────────────────────────────────
# Simulate a new transaction (append to CSV)
# ─────────────────────────────────────────────
@app.post("/transactions", tags=["Simulate"])
def add_transaction(
    msme_id: str,
    amount: float,
    type: str = "inflow",
    category: str = "sales",
):
    """
    Simulate a live transaction by appending a row to the CSV.
    Pathway will pick it up automatically.
    """
    csv_path = os.path.join(DATA_DIR, "transactions.csv")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [msme_id.upper(), timestamp, str(amount), type, category]

    file_exists = os.path.exists(csv_path)
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(
                ["msme_id", "timestamp", "amount", "type", "category"]
            )
        writer.writerow(row)

    return {
        "status": "transaction_added",
        "transaction": {
            "msme_id": msme_id.upper(),
            "timestamp": timestamp,
            "amount": amount,
            "type": type,
            "category": category,
        },
        "message": "Pathway will process this within ~1 second.",
    }


# ─────────────────────────────────────────────
# Get alerts (MSMEs above threshold)
# ─────────────────────────────────────────────
@app.get("/alerts", tags=["Alerts"])
def get_alerts(threshold: float = 0.4):
    """Return MSMEs whose stress score exceeds the threshold."""
    snapshot = get_store_snapshot()
    alerts = {
        k: v
        for k, v in snapshot.items()
        if v.get("stress_score", 0) >= threshold
    }
    return {
        "threshold": threshold,
        "alert_count": len(alerts),
        "alerts": alerts,
        "timestamp": datetime.now().isoformat(),
    }
