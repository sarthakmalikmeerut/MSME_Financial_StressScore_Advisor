import pathway as pw
from app.pipeline.streams import read_streams
from app.pipeline.features import build_features
from app.pipeline.score import score_table

def build():
    inflow, outflow, emi, balance = read_streams()
    feats = build_features(inflow, outflow, emi, balance)
    scored = score_table(feats)
    
    # Write to local file for easy checking
    pw.io.jsonlines.write(scored, "output.jsonl")
    # Also write to stdout (this often creates a file named 'stdout' in the root)
    pw.io.jsonlines.write(scored, "stdout") 

if __name__ == "__main__":
    print("🚀 MSME Stress Score Pipeline Starting...")
    print("📈 Monitoring data/streams/ for changes...")
    print("📝 Results will appear in 'output.jsonl' and 'stdout' file.")
    build()
    pw.run()
