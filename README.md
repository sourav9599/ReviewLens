<div align="center">

# 🧠 ReviewIQ
### Agentic AI A Multi Agent Customer Review Intelligence System

**Hack Malenadu '26 · Consumer & Retail Track**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![LangGraph](https://img.shields.io/badge/LangGraph-9--Agent_Pipeline-FF6B6B?style=flat-square)](https://langchain-ai.github.io/langgraph)
[![Ollama](https://img.shields.io/badge/Ollama-LLaMA_3.1_8B-black?style=flat-square)](https://ollama.ai)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

*A fully offline, production-grade AI platform that transforms raw customer reviews into granular sentiment insights, emerging trend alerts, emoji signal analysis, cross-product comparisons, and prioritized business recommendations — powered by a **9-agent LangGraph pipeline** running LLaMA 3.1 locally via Ollama.*

</div>

---

## 📸 Overview

ReviewIQ goes far beyond basic summarization. It ingests noisy, multilingual reviews at scale and routes them through a specialized 9-agent pipeline — each agent handling one precise job. The result: feature-level sentiment, sarcasm detection, emoji signal extraction, cross-product comparison, automated report generation, and actionable recommendations — all through a beautiful real-time dashboard built for non-technical product and marketing teams.

---

## ✨ Key Features

- **🤖 9-Agent LangGraph Pipeline** — Fully orchestrated multi-agent system where each agent is independently specialized, coordinated by a central Orchestrator Agent
- **🔬 Feature-Level Sentiment** — Per-attribute analysis with confidence scores (battery life, packaging, delivery, taste, effectiveness, and 12+ more)
- **😂 Emoji Signal Analysis** — Dedicated agent that reads emoji patterns as independent sentiment signals
- **🔁 Cross-Product Comparison** — Compare sentiment, features, and trends across multiple products simultaneously
- **📈 Trend Detection** — Catches emerging complaint spikes (e.g. "packaging complaints jumped from 8% → 38% in the last 50 reviews")
- **🛡️ Deduplication Agent** — Standalone agent for exact and near-duplicate clustering (85%+ similarity)
- **📄 Report Generation** — Dedicated report agent that auto-generates structured downloadable reports
- **🌐 Multilingual** — English, Hindi (हिन्दी), and Kannada (ಕನ್ನಡ) reviews handled natively
- **💯 100% Free & Offline** — No API keys, no cloud, no cost. Runs entirely on your machine.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ReviewIQ Platform                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   React Frontend  (Vite · Tailwind · Framer Motion · Recharts)          │
│   ┌──────────┐   ┌───────────────┐   ┌──────────────────────────────┐  │
│   │  Upload  │   │  Live Pipeline│   │   Dashboard (5 Tabs)          │  │
│   │  Page    │   │  Viewer       │   │   Overview · Trends · Recs    │  │
│   └──────────┘   └───────────────┘   └──────────────────────────────┘  │
│                          │  REST + SSE Streaming                        │
├──────────────────────────│──────────────────────────────────────────────┤
│                          ▼                                              │
│   FastAPI Backend                                                       │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                LangGraph 9-Agent Pipeline                       │   │
│   │                                                                 │   │
│   │              ┌──────────────────────┐                           │   │
│   │              │  Orchestrator Agent  │  ← coordinates all agents │   │
│   │              └──────────┬───────────┘                           │   │
│   │                         │                                       │   │
│   │         ┌───────────────┼───────────────┐                       │   │
│   │         ▼               ▼               ▼                       │   │
│   │     [Agent 1]       [Agent 2]       [Agent 3]                   │   │
│   │    Preprocessor   Deduplication   Emoji Analysis                │   │
│   │         └───────────────┼───────────────┘                       │   │
│   │                         ▼                                       │   │
│   │                   [Agent 4]                                     │   │
│   │                  Sentiment AI                                   │   │
│   │                         │                                       │   │
│   │         ┌───────────────┼───────────────┐                       │   │
│   │         ▼               ▼               ▼                       │   │
│   │     [Agent 5]       [Agent 6]       [Agent 7]                   │   │
│   │  Trend Detector  Cross-Comparison  Recommendations              │   │
│   │                         │                                       │   │
│   │                         ▼                                       │   │
│   │                   [Agent 8]                                     │   │
│   │                 Report Generator                                │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                          │                                              │
│              Ollama  (LLaMA 3.1 · 8B · fully local)                     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 The 9-Agent Pipeline

| # | Agent | File | Responsibility |
|---|-------|------|---------------|
| 🎯 | **Orchestrator** | `orchestrator_agent.py` | Coordinates all agents, manages pipeline state and routing |
| 1 | **Preprocessor** | `preprocessing_agent.py` | Cleans noisy text, handles typos, emojis, mixed language, normalizes inputs |
| 2 | **Deduplicator** | `deduplication_agent.py` | Detects exact and near-duplicate reviews, clusters spam/bot entries |
| 3 | **Emoji Analyst** | `emoji_agent.py` | Extracts sentiment signals from emoji patterns as independent features |
| 4 | **Sentiment AI** | `sentiment_agent.py` | Feature-level sentiment with confidence scores, sarcasm & ambiguity detection |
| 5 | **Trend Detector** | `trend_agent.py` | Sliding window pattern detection, anomaly spotting, systemic vs isolated classification |
| 6 | **Cross-Comparison** | `cross_comparison_agent.py` | Compares sentiment and feature scores across multiple products/categories |
| 7 | **Recommender** | `recommendations_agent.py` | Synthesizes all signals into prioritized, actionable business recommendations |
| 8 | **Report Generator** | `report_agent.py` | Auto-generates structured downloadable reports from the complete analysis |

---

## 🗂️ Project Structure

```
final/
├── backend/
│   ├── agents/
│   │   ├── orchestrator_agent.py       # Central coordinator
│   │   ├── preprocessing_agent.py      # Text cleaning & normalization
│   │   ├── deduplication_agent.py      # Spam & duplicate detection
│   │   ├── emoji_agent.py              # Emoji sentiment signals
│   │   ├── sentiment_agent.py          # Feature-level sentiment + sarcasm
│   │   ├── trend_agent.py              # Trend & anomaly detection
│   │   ├── cross_comparison_agent.py   # Multi-product comparison
│   │   ├── recommendations_agent.py    # Priority recommendations
│   │   └── report_agent.py             # Report generation
│   ├── core/                           # LangGraph pipeline, state, LLM client
│   ├── data/
│   │   └── synthetic_generator.py      # 260+ review dataset generator
│   ├── scrapers/                       # Data ingestion utilities
│   ├── .env
│   └── .env.example
├── frontend/
│   └── src/
│       ├── pages/                      # Upload · Pipeline · Dashboard
│       ├── components/                 # Charts, Trends, Recs, Reviews
│       └── store/                      # Zustand global state
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.10+ | [python.org](https://python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| Ollama | Latest | [ollama.ai](https://ollama.ai) |

### Step 1 — Pull the LLM model
```bash
ollama pull llama3.1:8b
```
> One-time ~5GB download. Runs well on 8GB+ RAM.

### Step 2 — Configure environment
```bash
cd backend
cp .env.example .env
# Edit .env if needed — default Ollama URL is http://localhost:11434
```

### Step 3 — Backend
```bash
cd backend
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Step 4 — Frontend
```bash
cd frontend
npm install
npm run dev
```

### Step 5 — Generate Demo Data
```bash
python backend/data/synthetic_generator.py
# Creates 260+ reviews across 3 product categories
```

### Step 6 — Open the app
Visit **[http://localhost:5173](http://localhost:5173)**, upload your reviews file, and click **Launch AI Analysis**.

---

## 🎬 Demo Walkthrough

> Follow this sequence to demo in under 3 minutes.

| Step | Page | What to Show |
|------|------|-------------|
| 1 | **Ingest** | Drag & drop the generated JSON file |
| 2 | **Pipeline** | All 9 agents running live with streaming log |
| 3 | **Dashboard → Overview** | Sentiment donut + Feature heatmap |
| 4 | **Dashboard → Trends** | Packaging complaint spike (8% → 38%+) |
| 5 | **Dashboard → Cross-Comparison** | Side-by-side product sentiment comparison |
| 6 | **Dashboard → Recommendations** | AI-ranked actions with timeline & impact |
| 7 | **Dashboard → Reviews** | Filter by sarcastic/ambiguous/language |
| 8 | **Dashboard → Data Quality** | Spam + duplicates caught by dedup agent |
| 9 | **Export** | Download auto-generated report |

---

## 📊 Seeded Trends in Demo Data

The synthetic dataset has **deliberately seeded complaint trends** that the Trend Agent will catch — directly matching the hackathon problem statement example:

| Product | Feature | Trigger Point | Expected Detection |
|---------|---------|--------------|-------------------|
| boAt Bassheads 900 | `packaging` | After review #150 | Complaint rate: ~8% → 38%+ |
| Himalaya Face Wash | `effectiveness` | After review #180 | Negative spike detected |

> *"Packaging complaints have appeared in 38% of reviews in the last 50 entries, up from 8% in the previous 50"* — this is exactly what the Trend Agent surfaces.

---

## 📁 Supported Input Formats

**CSV**
```csv
text,product,category,date,rating
"Great battery life!","boAt Bassheads 900","electronics","2024-03-15",5
"बहुत अच्छा है!","Nescafe Classic","food_beverage","2024-03-16",4
```

**JSON**
```json
[
  {
    "text": "Packaging was crushed. Product fine but box terrible 😡",
    "product": "boAt Bassheads 900",
    "category": "electronics",
    "date": "2024-04-01",
    "rating": 2
  }
]
```

**Plain Text** — Paste reviews directly, one per line or paragraph.

---

## 🔧 Configuration

`backend/.env`:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

To swap models:
```bash
ollama pull mistral:7b
# Set OLLAMA_MODEL=mistral:7b in .env
```

---

## 🏆 Hackathon Requirements — Compliance

| Requirement | Minimum Bar | Status |
|-------------|-------------|--------|
| Review ingestion | CSV/text upload | ✅ CSV + JSON + plain text |
| Noise handling | Typos, emojis, mixed lang | ✅ Preprocessing Agent |
| Spam/bot detection | Flagged separately | ✅ Deduplication Agent |
| Deduplication | Near-duplicate clustering | ✅ 85%+ similarity threshold |
| Sentiment granularity | Overall + 3 features | ✅ 12+ features with confidence scores |
| Sarcasm/ambiguity | Separate category | ✅ Sentiment Agent |
| Emoji analysis | — | ✅ Dedicated Emoji Agent |
| Trend detection | Batch-level patterns | ✅ Sliding window + time-series |
| Anomaly detection | Sudden sentiment drops | ✅ Trend Agent |
| Systemic vs isolated | Classification | ✅ Trend Agent |
| Cross-product comparison | Multiple products | ✅ Cross-Comparison Agent |
| Recommendations | Prioritized output | ✅ Recommendations Agent |
| Report generation | Downloadable | ✅ Report Agent |
| Seeded complaint trend | Judges will verify | ✅ Packaging + Effectiveness seeded |
| Visual dashboard | Charts + filters | ✅ React dashboard |
| English + Indian language | At least one | ✅ Hindi + Kannada |
| Multi-product | 3+ categories | ✅ Electronics, Food, Personal Care |
| Multi-agent architecture | — | ✅ **9 specialized agents via LangGraph** |

---

## 🛠️ Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com) — REST API + Server-Sent Events
- [LangGraph](https://langchain-ai.github.io/langgraph) — 9-agent orchestration
- [Ollama](https://ollama.ai) — Local LLM inference (LLaMA 3.1 8B)
- [FuzzyWuzzy](https://github.com/seatgeek/fuzzywuzzy) — Near-duplicate detection
- [Pandas / NumPy](https://pandas.pydata.org) — Data processing

**Frontend**
- [React 18](https://react.dev) + [Vite](https://vitejs.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Framer Motion](https://www.framer.com/motion) — Animations
- [Recharts](https://recharts.org) — Data visualization
- [Zustand](https://zustand-demo.pmnd.rs) — State management

---

## 👨‍💻 Built by

**wanderer's guild** · Hack Malenadu '26 · Consumer & Retail Track

---

<div align="center">

*Built with ❤️*

</div>
