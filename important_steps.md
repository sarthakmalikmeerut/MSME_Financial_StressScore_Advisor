# MSME Financial Stress Score Advisor - Quick Start Guide

Follow these steps to set up the environment and run the application.

### 1. Prerequisites
This project is designed to run in **WSL (Windows Subsystem for Linux)**.

### 2. Set Up Virtual Environment
Create and activate a Python virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
Install Pathway and other required packages:
```bash
pip install pathway
# If you have further dependencies, run:
# pip install -r requirements.txt
```

### 4. Configure Python Path
Set the `PYTHONPATH` so the `app` module is correctly recognized:
```bash
export PYTHONPATH=$(pwd)
```

### 5. Start the Program
Run the main pipeline script from the root directory:
```bash
python -m app.main
```

### 6. Monitor and See Live Changes
To see the streaming pipeline in action:
1. **Keep the program running** in your first terminal window. You will see the initial processing of existing data.
2. **Open another terminal window** and navigate to same project directory.
3. **Append new data** to the inflow stream. Use timestamps **later** than the original data (which ends at 10:02:00 on Feb 10) to trigger the output:
   ```bash
   # Add transactions for MSME A1 at 10:15 and 10:20
   printf '\n4,A1,30000,2026-02-10T10:15:00' >> data/streams/inflow.csv
   printf '\n5,A1,28000,2026-02-10T10:20:00' >> data/streams/inflow.csv
   ```
4. **Watch the first terminal:** You will now see JSON lines appearing for `A1`. Because we set the window to 5 minutes, adding a transaction at `10:15:00` forces the previous windows to calculate and print!
