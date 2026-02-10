# Live MSME Financial Stress Detector — 5-Day Plan

## Day 1 — Setup & Streams
- Setup WSL2 + Ubuntu + Python venv
- Install Pathway + dependencies
- Create folder structure
- Seed CSVs & replay as live streams
- Verify live prints

## Day 2 — Features
- Build rolling windows (24h, 7d)
- Compute inflow, outflow, fixed expenses
- Derive net cashflow & expense pressure

## Day 3 — Stress Score
- Implement stress score (0–1)
- Add explainable drivers (why score changed)
- Tune weights & test via CSV appends

## Day 4 — API / RAG (Optional)
- Add FastAPI endpoint or live stream
- (Optional) Add RAG for “Why now?” explanation

## Day 5 — Polish & Demo
- Script live demo (stress spike)
- Add README + architecture slide
- Final testing & cleanup
