# ReviewIQ — Quick Start Guide

> **Customer Review Intelligence Platform**  
> 6-Agent LangGraph pipeline · Ollama llama3.1:8b · React + FastAPI · Glassmorphism SaaS UI

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   ReviewIQ LangGraph Pipeline                │
│                                                             │
│  [1] PreprocessingAgent                                     │
│       └─ Clean text, emoji→text, detect language            │
│                    ↓                                        │
│  [2] DeduplicationAgent                                     │
│       └─ Exact hash dedup + fuzzy near-duplicate            │
│       └─ Heuristic bot scoring (5 signals)                  │
│                    ↓                                        │
│  [3] SentimentAnalysisAgent  ← cloud LLMS/local(Ollama llama3.1:8b)          │
│       └─ Feature-level sentiment with confidence            │
│       └─ Sarcasm / ambiguity detection                      │
│                    ↓                                        │
│  [4] TrendDetectionAgent                                    │
│       └─ Sliding window analysis                            │
│       └─ Z-score anomaly detection                          │
│       └─ Systemic vs isolated issue classification          │
│                    ↓                                        │
│  [5] RecommendationsAgent    ← cloud LLMS/local(Ollama llama3.1:8b)            │
│       └─ LLM-generated prioritized action items             │
│                    ↓                                        │
│  [6] ReportSynthesisAgent                                   │
│       └─ Unified AnalysisReport with full agent trace       │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

| Tool        | Version | Purpose                     |
| ----------- | ------- | --------------------------- |
| Python      | 3.10+   | Backend runtime             |
| Node.js     | 18+     | Frontend build              |
| Ollama      | latest  | Local LLM                   |
| llama3.1:8b | pulled  | Sentiment + recommendations |

---

## Step 1 — Pull the LLM Model

```bash
# Make sure Ollama is running
ollama serve

# In another terminal, pull the model
ollama pull llama3.1:8b

# Verify it's available
ollama list
```

---

## Step 2 — Backend Setup

```bash
cd reviewiq/backend

# Create virtual environment
python -m venv venv

# Activate it
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Create .env file
cp .env.example .env
# Edit .env if your Ollama runs on a non-default port

# Start the backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend is now live at: **http://localhost:8000**  
API docs (Swagger UI): **http://localhost:8000/docs**

---

## Step 3 — Frontend Setup

```bash
cd reviewiq/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend is now live at: **http://localhost:5173**

---

## Step 4 — Run Your First Analysis

### Option A: Demo Dataset (Fastest — Recommended for Hackathon Demo)

1. Open **http://localhost:5173**
2. Click **"Start Analyzing"** → go to **Ingest Reviews**
3. Select **"Demo Dataset"** tab
4. Click **"Launch Analysis Pipeline"**
5. You'll be redirected to the Dashboard automatically

> ⚡ The demo has **247 reviews** across 3 categories with a **seeded packaging complaint trend** in Earphone reviews. The system will detect it.

### Option B: Upload Your Own CSV

Your CSV should have these columns (flexible naming):

```
review_text, rating, category, product_name, review_date
```

Or any of these aliases: `text`, `review`, `body`, `stars`, `score`

### Option C: Paste Raw Text

One review per line — great for quick testing.

---

## Docker Compose (One Command)

```bash
# From the project root
docker-compose up --build

# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
```

> **Note:** Docker setup proxies Ollama from `host.docker.internal:11434`.  
> Make sure Ollama is running on your host machine.

---

## Environment Variables

Create `backend/.env` to customize:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
MAX_REVIEWS_PER_BATCH=500
DEDUP_SIMILARITY_THRESHOLD=0.85
BOT_DETECTION_THRESHOLD=0.65
TREND_WINDOW_SIZE=50
ANOMALY_Z_SCORE_THRESHOLD=2.0
```

---

## API Reference

| Endpoint              | Method | Description                      |
| --------------------- | ------ | -------------------------------- |
| `/api/analyze/demo`   | POST   | Run built-in 247-review demo     |
| `/api/analyze/upload` | POST   | Upload CSV or JSON file          |
| `/api/analyze/paste`  | POST   | Submit reviews as JSON array     |
| `/api/analyze/text`   | POST   | Submit plain text (one per line) |
| `/api/jobs/{job_id}`  | GET    | Poll job status + get report     |
| `/api/demo/dataset`   | GET    | Download the synthetic dataset   |
| `/api/jobs`           | GET    | List all jobs                    |
| `/health`             | GET    | Health check                     |

---

## Project Structure

```
reviewiq/
├── backend/
│   ├── agents/
│   │   ├── preprocessing_agent.py   # Agent 1: Clean & normalize
│   │   ├── deduplication_agent.py   # Agent 2: Dedup + bot detection
│   │   ├── sentiment_agent.py       # Agent 3: LLM feature sentiment
│   │   ├── trend_agent.py           # Agent 4: Sliding window trends
│   │   ├── recommendations_agent.py # Agent 5: LLM recommendations
│   │   └── report_agent.py          # Agent 6: Synthesize report
│   ├── core/
│   │   ├── models.py                # Pydantic models + LangGraph state
│   │   ├── pipeline.py              # LangGraph graph definition
│   │   └── config.py                # Settings
│   ├── data/
│   │   └── synthetic_generator.py  # 247-review demo dataset
│   ├── main.py                      # FastAPI app + endpoints
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   │   ├── OverviewTab.jsx
│   │   │   │   ├── SentimentTab.jsx
│   │   │   │   ├── TrendsTab.jsx
│   │   │   │   ├── RecommendationsTab.jsx
│   │   │   │   └── ReviewsTab.jsx
│   │   │   └── shared/
│   │   │       └── Layout.jsx
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── UploadPage.jsx
│   │   │   └── DashboardPage.jsx
│   │   ├── store/
│   │   │   └── reviewStore.js       # Zustand global state
│   │   └── styles/
│   │       └── globals.css
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── QUICKSTART.md
```

---

## Demo Script (For Judges)

1. **Show the Landing Page** — explain the 6-agent pipeline diagram
2. **Go to Ingest Reviews** — select Demo Dataset, explain the seeded packaging complaint
3. **Click Launch Pipeline** — show the agent animation on the sidebar
4. **Dashboard → Overview** — highlight the critical alert banner, agent trace
5. **Sentiment Analysis tab** — click a feature card (try "packaging") to see drill-down
6. **Trend Detection tab** — switch to "packaging" feature in the chart, show the spike
7. **Recommendations tab** — show how P1 recommendations are data-driven
8. **All Reviews tab** — filter by `bot_suspected` to show detection

---

## Hackathon Checklist

| Requirement                                    | Status                      |
| ---------------------------------------------- | --------------------------- |
| CSV/JSON/text upload                           | ✅                          |
| Noise handling (typos, emojis, mixed language) | ✅                          |
| Deduplication + near-duplicate clustering      | ✅                          |
| Bot/spam detection (flagged separately)        | ✅                          |
| Feature-level sentiment with confidence scores | ✅                          |
| Sarcasm/ambiguity flagging                     | ✅                          |
| Trend detection with sliding windows           | ✅                          |
| Z-score anomaly detection                      | ✅                          |
| Systemic vs isolated issue classification      | ✅                          |
| Seeded complaint trend detectable              | ✅ (packaging in earphones) |
| 200+ reviews across 3 categories               | ✅ (247 reviews)            |
| Hindi/Hinglish language support                | ✅                          |
| Visual dashboard                               | ✅                          |
| Agentic AI / multi-agent system                | ✅ (6 LangGraph agents)     |
| Prioritized recommendations                    | ✅                          |

---

## Troubleshooting

**Ollama not connecting?**

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

**`langdetect` errors?**

```bash
pip install langdetect --break-system-packages
```

**Frontend can't reach backend?**

- Make sure backend is on port 8000
- Vite proxy in `vite.config.js` forwards `/api` to `localhost:8000`

**Analysis taking too long?**

- llama3.1:8b processes ~3-5 reviews/minute on CPU
- For demo, use ≤50 reviews for faster turnaround
- The pipeline processes all 247 demo reviews; expect ~8-15 min on CPU

---

_Built for Hack Malenadu '26 · Consumer & Retail Track_
