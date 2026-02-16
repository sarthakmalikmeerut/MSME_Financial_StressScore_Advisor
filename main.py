"""
MSME Financial Stress Score Advisor — Main Entry Point
Runs Pathway pipeline + FastAPI server concurrently.
"""

import threading
import time
import os
import uvicorn


def main():
    # ── Paths ──
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")

    # Ensure data directory exists
    os.makedirs(data_dir, exist_ok=True)

    # Check if seed data exists
    csv_path = os.path.join(data_dir, "transactions.csv")
    if not os.path.exists(csv_path):
        print(f"[Main] WARNING: No transactions.csv found at {csv_path}")
        print("[Main] Creating seed data...")
        with open(csv_path, "w") as f:
            f.write("msme_id,timestamp,amount,type,category\n")
            f.write("MSME001,2026-02-14 08:00:00,50000,inflow,sales\n")
            f.write("MSME001,2026-02-14 09:00:00,-12000,outflow,rent\n")
            f.write("MSME001,2026-02-14 10:00:00,-8000,outflow,salary\n")
            f.write("MSME001,2026-02-14 11:00:00,15000,inflow,sales\n")
            f.write("MSME002,2026-02-14 08:30:00,30000,inflow,sales\n")
            f.write("MSME002,2026-02-14 09:30:00,-25000,outflow,inventory\n")
            f.write("MSME002,2026-02-14 10:30:00,-9000,outflow,rent\n")
            f.write("MSME002,2026-02-14 11:30:00,5000,inflow,sales\n")
        print("[Main] Seed data created.")

    # ── Start Pathway pipeline in background thread ──
    from src.pipeline import run_pipeline

    pipeline_thread = threading.Thread(
        target=run_pipeline,
        args=(data_dir,),
        daemon=True,
        name="PathwayPipeline",
    )
    pipeline_thread.start()
    print("[Main] Pipeline started in background thread.")

    # Give pipeline a moment to initialize
    time.sleep(3)

    # ── Start FastAPI server (blocks) ──
    print("[Main] Starting FastAPI server on http://localhost:8000")
    print("[Main] API docs at http://localhost:8000/docs")

    from src.api import app

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
