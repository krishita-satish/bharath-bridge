# BharatBridge 🇮🇳

**AI Execution Agent for Public Infrastructure**

BharatBridge is a multi-agent AI system designed to automate citizen access to government welfare, scholarships, and subsidies. It overcomes discovery, comprehension, and process barriers using:

- **Profiler Agent**: Extracts data from documents (simulated OCR).
- **Eligibility Agent**: Knowledge graph-based scheme discovery.
- **Document Agent**: Authenticity validation and PII redaction.
- **Adversarial Agent**: Predictive rejection analysis (simulated ML).
- **Execution Agent**: Automated submission tiers (API -> Web -> PDF).
- **Appeals Agent**: Generates legal appeal letters for rejections.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Start the Backend (API)

```bash
cd backend
# Install dependencies
pip install -r requirements.txt

# Run the server
python -m uvicorn main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000`.
API Documentation: `http://127.0.0.1:8000/docs`

### 2. Start the Frontend (Web App)

```bash
cd frontend
# Install dependencies
npm install

# Run the development server
npm run dev
```

Open `http://localhost:3000` in your browser.

## 🏗️ Architecture

- **Backend**: FastAPI, NetworkX (Graph), Pydantic
- **Frontend**: Next.js 14, Tailwind/CSS Modules (Premium UI)
- **AI/ML**: Simulated models for OCR (Textract), Rejection Prediction (XGBoost), and Knowledge Graph (Neptune).

## 🛡️ Key Features

- **Scheme Discovery**: Graph-based eligibility matching.
- **AI Pipeline**: Visualized multi-stage processing of applications.
- **Adversarial Validation**: Pre-submission risk checks.
- **Multi-language Appeals**: Auto-generated appeal letters in English/Hindi.
