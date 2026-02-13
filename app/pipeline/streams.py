import pathway as pw
from .schemas import InflowSchema, OutflowSchema, EMISchema, BalanceSchema

def read_streams():
    # Helper to read and parse ts
    def read_and_parse(path, schema):
        table = pw.io.csv.read(
            path=path,
            schema=schema,
            mode="streaming"
        )
        # Parse ISO timestamp string to DateTimeNaive
        return table.with_columns(ts=pw.this.ts.dt.strptime("%Y-%m-%dT%H:%M:%S"))

    inflow = read_and_parse("./data/streams/inflow.csv", InflowSchema)
    outflow = read_and_parse("./data/streams/outflow.csv", OutflowSchema)
    emi = read_and_parse("./data/streams/emi.csv", EMISchema)
    balance = read_and_parse("./data/streams/balance.csv", BalanceSchema)
    
    return inflow, outflow, emi, balance
