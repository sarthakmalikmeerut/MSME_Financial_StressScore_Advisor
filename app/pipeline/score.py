import pathway as pw

def score_table(feats, w_expense=0.7, w_net=0.3):
    scored = feats.with_columns(
        stress_score   = w_expense*pw.this.norm_expense + w_net*pw.this.norm_net,
        driver_expense = w_expense*pw.this.norm_expense,
        driver_net     = w_net*pw.this.norm_net,
    )
    scored = scored.with_columns(
        top_drivers    = pw.if_else(
            pw.this.driver_expense > pw.this.driver_net, "expense_pressure", "net_cashflow"
        ),
    )
    return scored.select(
        pw.this.msme_id,
        pw.this.inflow_24h,
        pw.this.outflow_24h,
        pw.this.stress_score,
        pw.this.top_drivers,
    )
