# 📊 MSME Financial Stress Score Advisor & RAG System

A premium, intelligent platform designed to help Micro, Small, and Medium Enterprises (MSMEs) monitor their financial health and receive expert advice on stress management using state-of-the-art AI.

## 🌟 Overview

This project combines a **Real-time Data Pipeline** for calculating financial stress scores with an **AI-powered RAG (Retrieval-Augmented Generation) Advisor**. It empowers MSME owners with data-driven insights and instant access to financial guidelines, schemes, and recovery strategies.

---

## 🚀 Key Features

### 1. Intelligent RAG Advisor (`rag_app.py`)
- **Expert Financial Guidance**: Uses **LangChain** and **Hugging Face (Mistral-7B)** to provide professional advice based on indexed documents.
- **Dynamic Knowledge Base**: Automatically indexes local documentation (`doc/`) and curated internet-sourced guidelines (`internet_docs/`).
- **Persistent Vector Store**: Uses **FAISS** to store embeddings locally, ensuring blazing-fast startup and offline retrieval capabilities.
- **Premium Chat Interface**: A modern, dark-themed Flask UI with real-time feedback and smooth interactions.

### 2. MSME Stress Score Pipeline (`app/main.py`)
- **Data-Driven Analysis**: Processes inflow, outflow, and EMI data to calculate real-time financial stress levels.
- **Powered by Pathway**: Leverages the **Pathway** engine for high-performance stream processing.
- **Automated Reporting**: Outputs detailed stress score metrics to `output.jsonl`.

---

## 🛠️ Technology Stack

- **Frameworks**: Flask (Web UI), LangChain (AI Orchestration), Pathway (Data Pipeline)
- **AI Models**: 
  - **LLM**: `Mistral-7B-Instruct-v0.2` (via Hugging Face Inference API)
  - **Embeddings**: `all-MiniLM-L6-v2` (Sentence Transformers)
- **Vector Database**: FAISS (Facebook AI Similarity Search)
- **Data Formats**: Markdown (Knowledge Base), JSONL (Data Streams)

---

## ⚙️ Setup & Installation

### 1. Requirements
Ensure you have Python 3.10+ installed. Install the dependencies:
```powershell
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the root directory and add your Hugging Face API Key:
```env
HUGGINGFACE_API_KEY=your_huggingface_api_token_here
```

---

## 📖 How to Use

### Run the AI Advisor
To launch the interactive chat interface:
```powershell
python rag_app.py
```
Then visit: `http://localhost:5000`

### Run the Stress Score Pipeline
To process financial data and generate stress scores:
```powershell
python -m app.main
```
Results will be generated in `output.jsonl`.

---

## 📂 Project Structure

```text
├── app/                  # Financial stress score calculation logic
│   └── main.py          # Entry point for the data pipeline
├── doc/                  # Local user-provided documentation
├── internet_docs/        # Curated MSME guidelines (RBI, SIDBI, Budget 2025)
├── faiss_index_store/    # Persistent vector database (auto-generated)
├── rag_app.py            # Main Flask application & RAG Pipeline
├── requirements.txt      # Project dependencies
└── .env                  # Secrets and API configurations
```

---

## ⚖️ License
This project is designed for MSME empowerment and financial literacy.

*Built with ❤️ for the MSME Ecosystem.*
