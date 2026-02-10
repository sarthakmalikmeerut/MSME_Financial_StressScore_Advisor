import pathway as pw

class InflowSchema(pw.Schema):
    txn_id: int
    msme_id: str
    amount: float
    ts: str