from datetime import timedelta
import pathway as pw

def build_features(inflow, outflow, emi, balance):
    # Short windows (5 min) for testing/dev so they emit immediately
    test_window = pw.temporal.sliding(duration=timedelta(minutes=5), hop=timedelta(minutes=1))

    inflow_5m = (
        inflow.windowby(
            pw.this.ts,
            window=test_window,
            instance=pw.this.msme_id
        ).reduce(msme_id=pw.reducers.any(pw.this.msme_id), inflow_24h=pw.reducers.sum(pw.this.amount))
    )

    outflow_5m = (
        outflow.windowby(
            pw.this.ts,
            window=test_window,
            instance=pw.this.msme_id
        ).reduce(msme_id=pw.reducers.any(pw.this.msme_id), outflow_24h=pw.reducers.sum(pw.this.amount))
    )

    fixed_out_5m = (
        outflow.filter(pw.this.fixed_flag == 1)
        .windowby(
            pw.this.ts,
            window=test_window,
            instance=pw.this.msme_id
        ).reduce(msme_id=pw.reducers.any(pw.this.msme_id), fixed_out_7d=pw.reducers.sum(pw.this.amount))
    )

    inflow_5m_avg = (
        inflow.windowby(
            pw.this.ts,
            window=test_window,
            instance=pw.this.msme_id
        ).reduce(msme_id=pw.reducers.any(pw.this.msme_id), inflow_7d_avg=pw.reducers.avg(pw.this.amount))
    )

    # Join results - Pathway joins windowed tables on both instance AND window alignment
    feats = (
        inflow_5m
          .join_outer(outflow_5m, pw.this.msme_id == pw.right.msme_id)
          .select(
              msme_id = pw.coalesce(pw.this.msme_id, pw.right.msme_id),
              inflow_24h = pw.coalesce(pw.this.inflow_24h, 0.0),
              outflow_24h = pw.coalesce(pw.right.outflow_24h, 0.0)
          )
          .join_outer(fixed_out_5m, pw.this.msme_id == pw.right.msme_id)
          .select(
              msme_id = pw.coalesce(pw.this.msme_id, pw.right.msme_id),
              inflow_24h = pw.coalesce(pw.this.inflow_24h, 0.0),
              outflow_24h = pw.coalesce(pw.this.outflow_24h, 0.0),
              fixed_out_7d = pw.coalesce(pw.right.fixed_out_7d, 0.0)
          )
          .join_outer(inflow_5m_avg, pw.this.msme_id == pw.right.msme_id)
          .select(
              msme_id = pw.coalesce(pw.this.msme_id, pw.right.msme_id),
              inflow_24h = pw.coalesce(pw.this.inflow_24h, 0.0),
              outflow_24h = pw.coalesce(pw.this.outflow_24h, 0.0),
              fixed_out_7d = pw.coalesce(pw.this.fixed_out_7d, 0.0),
              inflow_7d_avg = pw.coalesce(pw.right.inflow_7d_avg, 0.0)
          )
    )

    # Raw drivers - Now guaranteed to be non-nullable
    feats = feats.with_columns(
        expense_pressure = (pw.this.fixed_out_7d / (pw.this.inflow_7d_avg + 1e-6)),
        net_cf_24h       = pw.this.inflow_24h - pw.this.outflow_24h
    )

    # Normalized drivers
    feats = feats.with_columns(
        norm_expense = pw.this.expense_pressure / (1 + pw.this.expense_pressure),
        norm_net     = pw.if_else(pw.this.net_cf_24h > 0, 0.0, 1.0)
    )

    return feats
