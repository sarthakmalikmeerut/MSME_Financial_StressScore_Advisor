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
python app/main.py
```

### 6. Monitor Processing
The application will begin streaming data from `./data/streams/`. You will see the processed results printed to the console as they occur.
