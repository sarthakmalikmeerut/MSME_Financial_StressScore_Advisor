import pathway as pw
from .schemas import InflowSchema

def read_stream():
    return pw.io.csv.read(
        "./data/streams",
        schema=InflowSchema,
        mode="streaming"
    )
