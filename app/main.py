import pathway as pw
from app.pipeline.streams import read_stream

def build():
    inflow = read_stream()
    pw.io.jsonlines.write(inflow, "stdout")

if __name__ == "__main__":
    build()
    pw.run()
