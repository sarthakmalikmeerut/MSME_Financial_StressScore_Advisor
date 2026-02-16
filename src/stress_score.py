"""
Stress Score Computation Module
Score range: 0.0 (healthy) to 1.0 (critical stress)
"""


def compute_stress_score(
    total_inflow: float,
    total_outflow: float,
    fixed_expense_ratio: float,
    txn_count: int,
) -> dict:
    """
    Compute a financial stress score for an MSME.

    Args:
        total_inflow: Sum of all inflows
        total_outflow: Sum of all outflows (positive number)
        fixed_expense_ratio: Fraction of outflow that is fixed (rent, salary)
        txn_count: Number of transactions in the window

    Returns:
        dict with score, drivers, and recommendation
    """
    # --- Cashflow pressure (0-1) ---
    if total_inflow == 0:
        cashflow_pressure = 1.0
    else:
        net = total_inflow - total_outflow
        cashflow_pressure = max(0.0, min(1.0, -net / max(total_inflow, 1)))

    # --- Expense rigidity (0-1) ---
    expense_rigidity = min(1.0, fixed_expense_ratio)

    # --- Activity signal (0-1): fewer txns = more stress ---
    activity_signal = max(0.0, min(1.0, 1.0 - (txn_count / 20.0)))

    # --- Weighted combination ---
    W_CASH = 0.50
    W_EXPENSE = 0.30
    W_ACTIVITY = 0.20

    score = round(
        W_CASH * cashflow_pressure
        + W_EXPENSE * expense_rigidity
        + W_ACTIVITY * activity_signal,
        4,
    )
    score = max(0.0, min(1.0, score))

    # --- Explainable drivers ---
    drivers = []
    if cashflow_pressure > 0.5:
        drivers.append(f"Negative net cashflow (pressure={cashflow_pressure:.2f})")
    if expense_rigidity > 0.6:
        drivers.append(f"High fixed expenses (rigidity={expense_rigidity:.2f})")
    if activity_signal > 0.5:
        drivers.append(f"Low transaction activity (signal={activity_signal:.2f})")
    if not drivers:
        drivers.append("All indicators within healthy range")

    # --- Recommendation ---
    if score >= 0.7:
        recommendation = "CRITICAL: Immediate intervention needed. Consider emergency credit line."
    elif score >= 0.4:
        recommendation = "WARNING: Monitor closely. Review fixed expenses and diversify revenue."
    else:
        recommendation = "HEALTHY: Continue current operations. Build cash reserves."

    return {
        "stress_score": score,
        "cashflow_pressure": round(cashflow_pressure, 4),
        "expense_rigidity": round(expense_rigidity, 4),
        "activity_signal": round(activity_signal, 4),
        "drivers": drivers,
        "recommendation": recommendation,
    }
