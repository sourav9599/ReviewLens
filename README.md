<div align="center">

# ReviewLens
### AI-Powered Dynamic Review Categorization & Semantic Search for Marriott Properties

**Codefest 4.0 | BYOT Theme**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![LangGraph](https://img.shields.io/badge/LangGraph-12--Agent_Pipeline-FF6B6B?style=flat-square)](https://langchain-ai.github.io/langgraph)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas_Vector_Search-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://mongodb.com)

> **Enterprise KPIs Addressed:** Intent to Recommend · RevPAR · Digital Direct Share · Marriott Bonvoy Occupancy & Enrollments · EBITDA Growth

*An enterprise-grade AI platform that dynamically categorizes Marriott hotel reviews into fine-grained topics, enables semantic search, surfaces popular mentions, detects emerging operational trends, and delivers actionable insights to property managers — powered by a **12-agent LangGraph pipeline** with Google Gemini and MongoDB Atlas Vector Search.*

</div>

---

## 1. Hypothesis

### What Are We Addressing?

**A problem that exists and is compounding.**

Marriott currently surfaces guest reviews with a fixed, coarse set of categories — Cleanliness, Service, Location, Room Quality, Food & Beverage, and Check-in Experience. These six buckets were designed for star-rating aggregation, not discovery.

The result: a guest who wants to know *"Is the gym actually open at 5 AM?"* or *"How is the noise level on floors near the elevator?"* must read dozens of unstructured reviews to find the answer. A property manager who wants to understand *"What specifically is driving our declining Intent to Recommend score?"* gets a blended 4.1/5.0 with no actionable signal.

**ReviewLens solves this** by using a 12-agent AI pipeline to dynamically tag every review with fine-grained topics beyond the static six — enabling both guest-facing filtering and associate-facing operational intelligence.

### The Business Problem in Numbers

| Signal | Current State | Target with ReviewLens |
|---|---|---|
| Marriott KPI: Intent to Recommend (NPS) | Target ≥ 65 (Yellow zone: 55–64) | Actionable sub-topic alerts close gap faster |
| Guest review actionability | 6 static categories | 30–50 dynamic topic clusters per property |
| Time for property manager to identify top complaint theme | Manual review scan: ~45 min/day | Automated topic dashboard: <2 min |
| OTA vs. Direct review engagement | Guests visit OTAs for richer review filters | Richer direct channel experience reduces OTA dependency |

### Quantified Expected Business Value

| Value Driver | Impact |
|---|---|
| **Digital Direct Share** | 0.2% conversion lift → ~$30M incremental margin at full rollout |
| **Operational Efficiency** | ~35,000 manager-hours saved/day across 9,000 properties |
| **Intent to Recommend** | +4–8 point NPS improvement within 90 days |
| **Bonvoy Enrollments** | 0.5% lift in enrollment rate among first-time bookers |

---

## 2. Real-Time Scenario: How ReviewLens Helps Marriott

### JW Marriott Seattle — Week of May 12, 2026

**Monday 9 AM** — 87 new reviews arrive from TripAdvisor and Marriott.com post-weekend.

**ReviewLens Pipeline Executes (< 90 seconds):**

```
Reviews In (87) → Preprocessing → Emoji Analysis → Bot Detection (3 removed)
→ Sentiment Analysis → Trend Detection → Recommendations → Mentions → Embeddings → Export
```

**What the Property GM Sees on Dashboard:**

| Signal | Finding | KPI Impact |
|--------|---------|------------|
| Trend Alert | "Housekeeping" complaints jumped from 12% → 38% in last 50 reviews | RevPAR at risk |
| Popular Mention | "valet parking" appearing in 24 reviews (18 negative) | Intent to Recommend drops |
| Sentiment Shift | "Dining" sentiment flipped negative after new menu launch | Bonvoy retention risk |
| Recommendation | "Increase housekeeping staff on floors 4-8 during weekend peak" | +$12 RevPAR/night |

**What the Guest Sees on Marriott.com:**

- **Popular Mentions:** `rooftop bar` · `pike place market` · `corner suite` · `spa treatment` · `valet parking`
- **Category Ratings:** Cleanliness 4.1 · Location 4.7 · Amenities 3.3 · Dining 2.7 · Service 4.0 · Value 3.6
- **Semantic Search:** Guest types *"hotel with good gym near downtown"* → finds relevant reviews instantly

---

## 3. Enterprise KPI Alignment

| Marriott KPI | How ReviewLens Drives It |
|--------------|--------------------------|
| **Intent to Recommend** | Topic-level signals enable faster service recovery loops → NPS +4–8 pts |
| **RevPAR** | Identifies operational fixes that improve ratings → higher occupancy + ADR |
| **Digital Direct Share** | Richer review experience on Marriott.com keeps guests off OTAs |
| **EBITDA Growth** | Automates manual review triage (saves ~35K manager-hours/day globally) |
| **Marriott Bonvoy Occupancy** | Personalized review UX helps Bonvoy members validate property fit |
| **Non-RevPAR Affiliation Fees** | Review intelligence as franchise value-add strengthens affiliation |
| **Net Rooms Growth** | Data-driven property insights attract new franchise prospects |
| **Leadership Index** | Gives GMs clear, quantified action plans with full auditability |

---

## 4. Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ReviewLens Platform                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─── Guest App (B2C) ────┐    ┌─── Property Owner Dashboard (B2B) ────┐   │
│  │  Popular Mentions       │    │  Trend Alerts & Anomaly Detection     │   │
│  │  Semantic Search        │    │  Actionable Recommendations           │   │
│  │  Category Ratings       │    │  Cross-Property Comparison            │   │
│  │  Mention-Based Filter   │    │  Topic Heatmap                        │   │
│  └────────────┬────────────┘    └────────────────┬──────────────────────┘   │
│               │         REST + SSE Streaming      │                         │
├───────────────┼──────────────────────────────────┼─────────────────────────┤
│               ▼                                   ▼                         │
│   FastAPI Backend (Async, 26 endpoints)                                     │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │             LangGraph 12-Agent Hotel Pipeline                       │   │
│   │                                                                     │   │
│   │   [1] Preprocessing ──► [2] Emoji Analysis ──► [3] Orchestrator    │   │
│   │           │                                          │              │   │
│   │           ▼                                          ▼              │   │
│   │   [4] Deduplication ──► [5] Sentiment Analysis ──► [6] Trends     │   │
│   │           │                                          │              │   │
│   │           ▼                                          ▼              │   │
│   │   [7] Recommendations ──► [8] Cross-Compare ──► [9] Report        │   │
│   │                                                      │              │   │
│   │                         Hotel-Specific Stages:       ▼              │   │
│   │              [10] Mentions Extraction (Gemini LLM)                  │   │
│   │              [11] Embedding Generation (gemini-embedding-2)         │   │
│   │              [12] MongoDB Export (Vector Search Ready)              │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                          │                                                  │
│   Google Gemini 2.5 Flash  ·  MongoDB Atlas Vector Search                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. The 12-Agent Pipeline

| # | Agent | File | Responsibility | KPI Impact |
|---|-------|------|---------------|------------|
| 1 | **Preprocessor** | `preprocessing_agent.py` | Cleans text, extracts sub-ratings, normalizes structure | EBITDA Growth |
| 2 | **Emoji Analyst** | `emoji_agent.py` | Extracts emoji sentiment signals for confidence boosting | Intent to Recommend |
| 3 | **Orchestrator** | `orchestrator_agent.py` | Dynamic routing, feedback loops, quality gates | EBITDA Growth |
| 4 | **Deduplicator** | `deduplication_agent.py` | Bot detection, spam removal, duplicate clustering | Digital Direct Share |
| 5 | **Sentiment AI** | `sentiment_agent.py` | Aspect-based sentiment across 6 hotel categories | RevPAR |
| 6 | **Trend Detector** | `trend_agent.py` | Sliding window anomaly detection, systemic vs isolated | RevPAR |
| 7 | **Recommender** | `recommendations_agent.py` | LLM-powered prioritized action items for property GM | Leadership Index |
| 8 | **Cross-Compare** | `cross_comparison_agent.py` | Multi-property performance benchmarking | Net Rooms Growth |
| 9 | **Report Synthesis** | `report_agent.py` | Aggregates all outputs into unified report | EBITDA Growth |
| 10 | **Mentions Extractor** | `mentions_agent.py` | Gemini keyphrase extraction for Popular Mentions UI | Digital Direct Share |
| 11 | **Embedding Generator** | `embedding_agent.py` | gemini-embedding-2 vectors for semantic search | Digital Direct Share |
| 12 | **Hotel Exporter** | `export_agent.py` | MongoDB-ready document assembly with all enrichments | RevPAR |

---

## 6. Who Receives the Value?

| Persona | Primary Use | Value Type |
|---|---|---|
| **Prospective Guest (Leisure)** | Filter reviews by topic before booking | Functional, Emotional |
| **Prospective Guest (Business)** | Filter by "Wi-Fi," "Quiet floor," "Early check-in" | Functional |
| **Marriott Bonvoy Member** | Personalized review feed based on preference history | Lifecycle, Emotional |
| **Property General Manager** | Operational topic heatmap, trend alerts, action items | Functional, Economic |
| **Marriott Brand/Quality Team** | Cross-property topic benchmarking | Brand, Economic |
| **Digital Marketing / CRM Team** | Identify high-sentiment topics to amplify in campaigns | Brand, Economic |

---

## 7. Project Structure

```
ReviewLens/
├── backend/
│   ├── agents/
│   │   ├── orchestrator_agent.py       # Pipeline intelligence hub
│   │   ├── preprocessing_agent.py      # Text cleaning & sub-rating extraction
│   │   ├── deduplication_agent.py      # Bot detection & duplicate removal
│   │   ├── emoji_agent.py              # Emoji sentiment signal extraction
│   │   ├── sentiment_agent.py          # Hotel aspect-based sentiment
│   │   ├── trend_agent.py              # Trend & anomaly detection
│   │   ├── cross_comparison_agent.py   # Multi-property comparison
│   │   ├── recommendations_agent.py    # Actionable GM recommendations
│   │   ├── report_agent.py             # Report synthesis
│   │   ├── mentions_agent.py           # Popular mentions extraction (Gemini)
│   │   ├── embedding_agent.py          # Vector embedding generation
│   │   └── export_agent.py             # MongoDB document export
│   ├── core/
│   │   ├── hotel_pipeline.py           # LangGraph pipeline orchestration
│   │   ├── pipeline.py                 # Base pipeline definition
│   │   ├── config.py                   # Settings & environment
│   │   └── models.py                   # Pydantic state models
│   ├── data/
│   │   ├── synthetic_generator.py      # 213 hotel review dataset generator
│   │   └── hotel_reviews_processed.json # Processed output (MongoDB-ready)
│   └── main.py                         # FastAPI application (26 endpoints)
├── frontend/
│   └── src/
│       ├── pages/                      # Dashboard · Hotel Reviews · Landing
│       ├── components/                 # Charts, Mentions, Search, Pipeline
│       └── store/                      # Zustand state management
├── tripadvisor_hotel_reviews.csv       # 20,491 real hotel reviews (with sub-ratings)
├── ReviewLens.md                       # Detailed hypothesis & solution doc
└── README.md
```

---

## 8. Quick Start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend build |
| Google Gemini API Key | — | LLM & embeddings |

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

echo "GOOGLE_API_KEY=your_gemini_key_here" > .env
echo "GEMINI_MODEL=gemini-2.5-flash-lite" >> .env

uvicorn main:app --reload --port 5000
```

### Frontend
```bash
cd frontend
pnpm install && pnpm run dev
```

### Ingest Hotel Reviews
```bash
curl -X POST "http://localhost:5000/api/hotel-reviews/ingest" \
  -F "file=@tripadvisor_hotel_reviews.csv" \
  -F "hotel_id=jw_marriott_seattle" \
  -F "max_rows=50"
```

### View Pipeline Graph
Open **http://localhost:5000/api/hotel-reviews/graph** in your browser.

---

## 9. Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|---------|
| `POST` | `/api/hotel-reviews/ingest` | Ingest CSV through 12-agent pipeline |
| `GET` | `/api/hotel-reviews/jobs/{id}` | Poll pipeline job status |
| `GET` | `/api/hotel-reviews/mentions/popular` | Get ranked popular mentions |
| `GET` | `/api/hotel-reviews/search` | Filter reviews by mention/sentiment/rating |
| `GET` | `/api/hotel-reviews/stats` | Property statistics and sentiment breakdown |
| `GET` | `/api/hotel-reviews/graph` | Interactive pipeline visualization (Mermaid) |
| `POST` | `/api/analyze/demo` | Run pipeline on synthetic hotel dataset |

---

## 10. Seeded Trends in Demo Data

The synthetic dataset has **deliberately seeded complaint trends** that the Trend Agent catches:

| Hotel | Feature | Trigger Point | Expected Detection |
|-------|---------|--------------|-------------------|
| Grand Monaco Seattle | `cleanliness / housekeeping` | After review #100 | Complaint rate: ~12% → 40%+ |
| City Business Inn | `wifi / connectivity` | After review #45 | Negative spike in business travelers |

> *"Housekeeping complaints have appeared in 40% of reviews in the last 25 entries, up from 12% in the previous batch"* — this maps directly to the Intent to Recommend KPI, enabling proactive staffing decisions.

---

## 11. Path to Production

| Phase | Timeline | Scope |
|-------|----------|-------|
| **Phase 1 — MVP** | Hackathon (48 hrs) | Synthetic data, 12-agent pipeline, React dashboard, local deployment |
| **Phase 2 — Pilot** | < 4 weeks | 3 real properties, MongoDB Atlas, Gemini enterprise endpoint |
| **Phase 3 — Production** | Q3–Q4 2026 | 9,000 properties, Kafka streaming, Aurora PostgreSQL, CDN |

**ROI:** $180K–$250K infrastructure cost vs. $30M+ direct booking conversion lift = **>100x ROI in Year 1**

---

## 12. Tech Stack

**Backend:** FastAPI · LangGraph · Google Gemini 2.5 Flash · gemini-embedding-2 · MongoDB Atlas Vector Search · RapidFuzz

**Frontend:** React 18 · Vite · Tailwind CSS · shadcn/ui · Zustand · Mermaid.js

---

## Codefest Judging Alignment

| Criterion | Weight | ReviewLens Coverage |
|---|---|---|
| **Hypothesis** | 30% | Clear problem (static categories), measurable KPI impact (NPS +4–8pts, Direct Share +0.2%), 6 value types, 6 personas, revenue quantified ($30M+ opportunity) |
| **Solution Framework** | 25% | Full architecture, 12-agent pipeline, MongoDB Vector Search, integration with UXL/mHelp/MPAD |
| **Working POC** | 30% | 26 API endpoints, React dashboard, real TripAdvisor data (20,491 reviews), pipeline visualization, semantic search |
| **Path to Production** | 15% | 3-phase rollout, TCO breakdown, governance/compliance, integration roadmap |

---

<div align="center">

*ReviewLens — Turning guest voices into operational intelligence.*

**Codefest 4.0 · Marriott International**

</div>
