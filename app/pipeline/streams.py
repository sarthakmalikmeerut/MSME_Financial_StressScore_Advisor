import pathway as pw
from .schemas import InflowSchema, OutflowSchema, EMISchema, BalanceSchema

def read_streams():
    # Helper to read and parse ts
    def read_and_parse(path, schema):
        table = pw.demo.replay_csv(
            path=path,
            schema=schema,
            input_rate=1.0
        )
        # Parse ISO timestamp string to DateTimeNaive
        # Using .dt.strptime if available, or a robust workaround
        return table.with_columns(ts=pw.this.ts.dt.strptime("%Y-%m-%dT%H:%M:%S"))

    inflow = read_and_parse("./data/streams/inflow.csv", InflowSchema)
    outflow = read_and_parse("./data/streams/outflow.csv", OutflowSchema)
    emi = read_and_parse("./data/streams/emi.csv", EMISchema)
    balance = read_and_parse("./data/streams/balance.csv", BalanceSchema)
    
    return inflow, outflow, emi, balance
