# TruthLayer: AI-Powered Fact-Checking Agent 🛡️

TruthLayer is a sophisticated fact-checking platform designed to automate the verification of factual claims within documents. Built for the **GEO Product Assessment 2025**, it acts as a "Truth Layer" for marketing content, whitepapers, and financial reports.

## 🚀 Key Features
- **Intelligent Claim Extraction**: Uses Gemini 2.5/1.5 Flash to identify verifiable facts (statistics, dates, financial figures).
- **Live Web Cross-Referencing**: Integrates with Tavily Search API to verify claims against real-time, high-authority web data.
- **Detailed Truth Reports**: Automatically categorizes claims as **Verified**, **Inaccurate**, **False**, or **Unverifiable**.
- **Automated Corrections**: Provides the "Real Fact" when an inaccuracy is detected.
- **Rate-Limit Resilient**: Features a custom token-bucket rate limiter and exponential backoff to handle free-tier API quotas gracefully.

## 🛠️ Tech Stack
- **Frontend**: React, TypeScript, Framer Motion (for premium UI/UX).
- **Backend**: FastAPI (Python 3.13), Uvicorn.
- **AI Models**: Google Gemini (GenAI SDK).
- **Search Engine**: Tavily AI.
- **PDF Processing**: PyMuPDF.

## 📦 Installation & Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- [Google AI Studio API Key](https://aistudio.google.com/)
- [Tavily API Key](https://tavily.com/)

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```
Create a `.env` file in the `backend` folder:
```env
GOOGLE_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
FRONTEND_URL=http://localhost:5173
```
Run the server:
```bash
python -m uvicorn main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🛡️ Evaluation "Trap" PDF Handling
TruthLayer is specifically optimized for "Trap Documents":
1. **Context-Aware Search**: The system automatically identifies the "Subject" of the document to ensure web searches are relevant (e.g., distinguishing Tesla's revenue from a random tax report).
2. **Deep Verification**: Instead of simple keyword matching, the AI analyzes the *source content* to confirm if numbers refer to the correct metric.

---
Built for the **GEO Assessment 2025**.
