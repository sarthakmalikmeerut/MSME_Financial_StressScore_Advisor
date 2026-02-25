

import csv
import json
import os
import threading
import time
from src.stress_score import compute_stress_score
from collections import defaultdict


# ══════════════════════════════════════════════
# Shared store: FastAPI reads from here
# Key: msme_id  |  Value: stress result dict
# ══════════════════════════════════════════════
stress_store: dict[str, dict] = {}
_store_lock = threading.Lock()


def update_store(msme_id: str, result: dict):
    with _store_lock:
        stress_store[msme_id] = result


def get_store_snapshot() -> dict:
    with _store_lock:
        return dict(stress_store)


def get_msme_score(msme_id: str) -> dict | None:
    with _store_lock:
        return stress_store.get(msme_id)


# ══════════════════════════════════════════════
# Simple CSV-based Pipeline
# ══════════════════════════════════════════════
def compute_aggregates(csv_path: str) -> dict:
    """
    Read CSV and compute aggregates per MSME.
    Returns dict: msme_id -> {aggregates}
    """
    aggregates = defaultdict(
        lambda: {
            "total_inflow": 0.0,
            "total_outflow": 0.0,
            "total_fixed": 0.0,
            "txn_count": 0,
        }
    )

    fixed_categories = ["rent", "salary", "loan_emi", "insurance"]

    if not os.path.exists(csv_path):
        return dict(aggregates)

    try:
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row or not row.get("msme_id"):
                    continue

                msme_id = row["msme_id"].upper()
                try:
                    amount = float(row.get("amount", 0))
                except ValueError:
                    continue

                category = row.get("category", "").lower()
                aggregates[msme_id]["txn_count"] += 1

                if amount > 0:
                    aggregates[msme_id]["total_inflow"] += amount
                else:
                    outflow_abs = abs(amount)
                    aggregates[msme_id]["total_outflow"] += outflow_abs
                    if category in fixed_categories:
                        aggregates[msme_id]["total_fixed"] += outflow_abs

    except Exception as e:
        print(f"[Pipeline] Error reading CSV: {e}")

    return dict(aggregates)


def run_pipeline(data_dir: str, poll_interval: float = 2.0):
    """
    Poll CSV for changes and update stress scores.
    Runs indefinitely; designed to run in a background thread.
    """
    csv_path = os.path.join(data_dir, "transactions.csv")
    output_dir = os.path.join(os.path.dirname(data_dir), "output")
    os.makedirs(output_dir, exist_ok=True)

    last_mtime = 0
    print(f"[Pipeline] Watching {csv_path} for changes...")

    while True:
        try:
            if os.path.exists(csv_path):
                current_mtime = os.path.getmtime(csv_path)

                # Only recompute if file was modified
                if current_mtime > last_mtime:
                    last_mtime = current_mtime
                    aggregates = compute_aggregates(csv_path)

                    # Compute and store stress scores
                    for msme_id, agg in aggregates.items():
                        fixed_ratio = (
                            agg["total_fixed"] / max(agg["total_outflow"], 1.0)
                        )
                        stress_result = compute_stress_score(
                            agg["total_inflow"],
                            agg["total_outflow"],
                            fixed_ratio,
                            agg["txn_count"],
                        )
                        result = {
                            "msme_id": msme_id,
                            **stress_result,
                            "total_inflow": agg["total_inflow"],
                            "total_outflow": agg["total_outflow"],
                        }
                        update_store(msme_id, result)
                        print(
                            f"[Pipeline] Updated {msme_id}: "
                            f"score={result['stress_score']}"
                        )

                    # Write to output file
                    output_file = os.path.join(output_dir, "stress_scores.jsonl")
                    with open(output_file, "w") as f:
                        for msme_id, result in aggregates.items():
                            fixed_ratio = (
                                result["total_fixed"]
                                / max(result["total_outflow"], 1.0)
                            )
                            stress_result = compute_stress_score(
                                result["total_inflow"],
                                result["total_outflow"],
                                fixed_ratio,
                                result["txn_count"],
                            )
                            output_data = {
                                "msme_id": msme_id,
                                **stress_result,
                                "total_inflow": result["total_inflow"],
                                "total_outflow": result["total_outflow"],
                            }
                            f.write(json.dumps(output_data) + "\n")

            time.sleep(poll_interval)

        except Exception as e:
            print(f"[Pipeline] Error: {e}")
            time.sleep(poll_interval)
