from datetime import timedelta
import pathway as pw

def build_features(inflow, outflow, emi, balance):
    inflow_24h = (
        inflow.windowby(
            pw.this.ts,
            window=pw.temporal.sliding(duration=timedelta(hours=24), hop=timedelta(minutes=5)),
            instance=pw.this.msme_id
        ).reduce(msme_id=pw.reducers.any(pw.this.msme_id), inflow_24h=pw.reducers.sum(pw.this.amount))
    )

    outflow_24h = (
        outflow.windowby(
            pw.this.ts,
            window=pw.temporal.sliding(duration=timedelta(hours=24), hop=timedelta(minutes=5)),
            instance=pw.this.msme_id
        ).reduce(msme_id=pw.reducers.any(pw.this.msme_id), outflow_24h=pw.reducers.sum(pw.this.amount))
    )

    fixed_out_7d = (
        outflow.filter(pw.this.fixed_flag == 1)
        .windowby(
            pw.this.ts,
            window=pw.temporal.sliding(duration=timedelta(days=7), hop=timedelta(hours=1)),
            instance=pw.this.msme_id
        ).reduce(msme_id=pw.reducers.any(pw.this.msme_id), fixed_out_7d=pw.reducers.sum(pw.this.amount))
    )

    inflow_7d_avg = (
        inflow.windowby(
            pw.this.ts,
            window=pw.temporal.sliding(duration=timedelta(days=7), hop=timedelta(hours=1)),
            instance=pw.this.msme_id
        ).reduce(msme_id=pw.reducers.any(pw.this.msme_id), inflow_7d_avg=pw.reducers.avg(pw.this.amount))
    )

    # Join feature tables
    feats = (
        inflow_24h
          .join(outflow_24h, inflow_24h.msme_id == outflow_24h.msme_id)
          .select(
              pw.this.msme_id,
              pw.this.inflow_24h,
              outflow_24h = pw.right.outflow_24h
          )
          .join(fixed_out_7d, pw.this.msme_id == fixed_out_7d.msme_id)
          .select(
              pw.this.msme_id,
              pw.this.inflow_24h,
              pw.this.outflow_24h,
              fixed_out_7d = pw.right.fixed_out_7d
          )
          .join(inflow_7d_avg, pw.this.msme_id == inflow_7d_avg.msme_id)
          .select(
              msme_id       = pw.this.msme_id,
              inflow_24h    = pw.this.inflow_24h,
              outflow_24h   = pw.this.outflow_24h,
              fixed_out_7d  = pw.this.fixed_out_7d,
              inflow_7d_avg = pw.right.inflow_7d_avg
          )
    )

    # Raw drivers
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
