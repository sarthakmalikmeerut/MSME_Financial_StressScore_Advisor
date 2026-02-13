import pathway as pw

class InflowSchema(pw.Schema):
    txn_id: int
    msme_id: str
    amount: float
    ts: str

class OutflowSchema(pw.Schema):
    txn_id: int
    msme_id: str
    amount: float
    ts: str
    fixed_flag: int

class EMISchema(pw.Schema):
    txn_id: int
    msme_id: str
    amount: float
    ts: str

class BalanceSchema(pw.Schema):
    msme_id: str
    amount: float
    ts: str