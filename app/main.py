import pathway as pw
from app.pipeline.streams import read_streams
from app.pipeline.features import build_features
from app.pipeline.score import score_table

def build():
    inflow, outflow, emi, balance = read_streams()
    feats = build_features(inflow, outflow, emi, balance)
    scored = score_table(feats)
    pw.io.jsonlines.write(scored, "stdout")  # see updates in terminal

if __name__ == "__main__":
    build()
    pw.run()
