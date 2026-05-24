<div align="center">

# ReviewLens
### AI-Powered Dynamic Review Categorization & Semantic Search for Marriott Properties

**Codefest 4.0 | BYOT Theme**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![LangGraph](https://img.shields.io/badge/LangGraph-12--Agent_Pipeline-FF6B6B?style=flat-square)](https://langchain-ai.github.io/langgraph)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev)
[![LiteLLM](https://img.shields.io/badge/LiteLLM-100+_Providers-orange?style=flat-square)](https://litellm.ai)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas_Vector_Search-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://mongodb.com)

> **Enterprise KPIs Addressed:** Intent to Recommend · RevPAR · Digital Direct Share · Marriott Bonvoy Occupancy & Enrollments · EBITDA Growth

*An enterprise-grade AI platform that dynamically categorizes Marriott hotel reviews into fine-grained topics, enables semantic search, surfaces popular mentions, detects emerging operational trends, and delivers actionable insights to property managers — powered by a **12-agent LangGraph pipeline** with multi-provider LLM support (Gemini, Vertex AI, LiteLLM), Map-Reduce summarization, and in-memory vector search.*

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

### Courtyard New York Manhattan/Fifth Avenue — Week of May 19, 2026

**Monday 9 AM** — 87 new reviews arrive from TripAdvisor and Marriott.com post-weekend.

**ReviewLens Pipeline Executes (< 90 seconds):**

```
Reviews In (87) → Preprocessing → Emoji Analysis → Bot Detection (3 removed)
→ Sentiment Analysis → Trend Detection → Recommendations → Mentions → Embeddings
→ Export → Summary Digest
```

**What the Property GM Sees on Dashboard (`/dashboard/NYCES`):**

| Signal | Finding | KPI Impact |
|--------|---------|------------|
| Trend Alert | "Bathroom maintenance" complaints jumped from 12% → 38% in last 50 reviews | RevPAR at risk |
| Popular Mention | "shower pressure" appearing in 14 reviews (12 negative) | Intent to Recommend drops |
| Sentiment Shift | "Dining" sentiment flipped negative after new menu launch | Bonvoy retention risk |
| AI Summary | Natural editorial summary highlighting strengths & areas to improve | Digital Direct Share |
| Executive Brief | C-suite ready brief with confidence score and priority actions | Leadership Index |
| Recommendation | "Address bathroom caulk mold and tub stopper on floors 3–8" | +$12 RevPAR/night |

**What the Guest Sees on Marriott.com:**

- **Popular Mentions:** `friendly staff` · `shower pressure` · `fifth avenue location` · `room size` · `breakfast`
- **Category Ratings:** Cleanliness 4.0 · Location 4.0 · Amenities 2.0 · Dining 2.0 · Service 5.0 · Value 3.0
- **Semantic Search:** Guest types *"hotel with good staff near downtown"* → finds relevant reviews instantly
- **AI Review Summary:** TripAdvisor-style narrative paragraph (no raw stats, natural editorial tone)

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
│  │  AI Review Summary      │    │  Executive Brief (LLM-powered)        │   │
│  │  Mention-Based Filter   │    │  Property Selector Dropdown           │   │
│  └────────────┬────────────┘    └────────────────┬──────────────────────┘   │
│               │         REST + SSE Streaming      │                         │
├───────────────┼──────────────────────────────────┼─────────────────────────┤
│               ▼                                   ▼                         │
│   FastAPI Backend (Async, 30+ endpoints)                                    │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │           LangGraph 12-Agent Hotel Pipeline                         │   │
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
│   │              [10] Mentions Extraction (LLM)                         │   │
│   │              [11] Embedding Generation (3072-dim)                   │   │
│   │              [12] Export + Summary Digest                           │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                          │                                                  │
│   ┌─────── LLM Layer (Switchable) ──────┐                                  │
│   │  Gemini API  │  Vertex AI (ADC)  │  LiteLLM (100+ providers)   │       │
│   └──────────────────────────────────────┘                                  │
│                          │                                                  │
│   InMemoryVectorStore (LangChain) · MongoDB Atlas Vector Search (Planned)   │
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
| 5 | **Sentiment AI** | `sentiment_agent.py` | Aspect-based sentiment across 13 hotel categories | RevPAR |
| 6 | **Trend Detector** | `trend_agent.py` | Sliding window anomaly detection, systemic vs isolated | RevPAR |
| 7 | **Recommender** | `recommendations_agent.py` | LLM-powered SMART action items for property GM | Leadership Index |
| 8 | **Cross-Compare** | `cross_comparison_agent.py` | Multi-property performance benchmarking | Net Rooms Growth |
| 9 | **Report Synthesis** | `report_agent.py` | Aggregates all outputs into unified report | EBITDA Growth |
| 10 | **Mentions Extractor** | `mentions_agent.py` | Aspect-based keyphrase extraction for Popular Mentions UI | Digital Direct Share |
| 11 | **Embedding Generator** | `embedding_agent.py` | 3072-dim vectors for semantic search (cosine similarity) | Digital Direct Share |
| 12 | **Hotel Exporter** | `export_agent.py` | MongoDB-ready document assembly + summary digest trigger | RevPAR |

### Summary Agent (Map-Reduce)

| Component | File | Purpose |
|-----------|------|---------|
| **Batch Digest (Map)** | `summary_agent.py` | Extracts compact statistics per ingestion batch without re-reading all reviews |
| **Aggregate Summary (Reduce)** | `summary_agent.py` | LLM aggregates digests into TripAdvisor-style editorial narrative |
| **Cache Layer** | `summary_cache.json` | Serves cached summaries; invalidated on new ingestion |

---

## 6. Key Features

### Multi-Provider LLM Support

ReviewLens supports switching between LLM providers via a single `.env` variable:

| Provider | Config Value | Use Case |
|----------|--------------|----------|
| **Gemini API** | `LLM_PROVIDER=gemini` | Default — fast, cost-effective with API key auth |
| **Vertex AI (ADC)** | `LLM_PROVIDER=googleADC` | Enterprise — uses Application Default Credentials |
| **LiteLLM** | `LLM_PROVIDER=litellm` | Flexibility — route to OpenAI, Anthropic, Azure, or any of 100+ providers |

### Semantic Search (In-Memory Vector Store)

- Pre-computed 3072-dimensional embeddings loaded at startup (no re-embedding)
- Cosine similarity search via LangChain `InMemoryVectorStore`
- Metadata filtering by `hotel_id`, `sentiment`, and `tag`
- Planned upgrade path to MongoDB Atlas Vector Search for production scale

### Per-Property Analysis & Caching

- Navigate to `/dashboard/{propertyCode}` to trigger analysis for a specific property
- Results cached in `property_analysis_cache.json` — subsequent visits served instantly
- Same pipeline powers both per-property and demo analysis

### Executive Brief

- LLM-generated C-suite summary with situation analysis, business impact, and priority actions
- Downloadable as PDF
- Confidence scoring (0–100)

---

## 7. Who Receives the Value?

| Persona | Primary Use | Value Type |
|---|---|---|
| **Prospective Guest (Leisure)** | Filter reviews by topic before booking | Functional, Emotional |
| **Prospective Guest (Business)** | Filter by "Wi-Fi," "Quiet floor," "Early check-in" | Functional |
| **Marriott Bonvoy Member** | Personalized review feed based on preference history | Lifecycle, Emotional |
| **Property General Manager** | Operational topic heatmap, trend alerts, action items | Functional, Economic |
| **Marriott Brand/Quality Team** | Cross-property topic benchmarking | Brand, Economic |
| **Digital Marketing / CRM Team** | Identify high-sentiment topics to amplify in campaigns | Brand, Economic |

---

## 8. Project Structure

```
ReviewLens/
├── backend/
│   ├── agents/
│   │   ├── orchestrator_agent.py       # Pipeline intelligence hub
│   │   ├── preprocessing_agent.py      # Text cleaning & sub-rating extraction
│   │   ├── deduplication_agent.py      # Bot detection & duplicate removal
│   │   ├── emoji_agent.py              # Emoji sentiment signal extraction
│   │   ├── sentiment_agent.py          # Hotel aspect-based sentiment (13 aspects)
│   │   ├── trend_agent.py              # Trend & anomaly detection
│   │   ├── cross_comparison_agent.py   # Multi-property comparison
│   │   ├── recommendations_agent.py    # Actionable GM recommendations (SMART)
│   │   ├── report_agent.py             # Report synthesis
│   │   ├── mentions_agent.py           # Popular mentions extraction (LLM)
│   │   ├── embedding_agent.py          # Vector embedding generation (3072-dim)
│   │   ├── export_agent.py             # MongoDB document export
│   │   └── summary_agent.py            # Map-Reduce narrative summary
│   ├── core/
│   │   ├── hotel_pipeline.py           # LangGraph hotel pipeline orchestration
│   │   ├── pipeline.py                 # Generic analysis pipeline
│   │   ├── llm_factory.py             # Multi-provider LLM factory (Gemini/ADC/LiteLLM)
│   │   ├── config.py                   # Settings & environment
│   │   └── models.py                   # Pydantic state models
│   ├── data/
│   │   ├── synthetic_generator.py      # 213 hotel review dataset generator
│   │   ├── hotel_reviews_processed.json # Processed output (MongoDB-ready)
│   │   ├── batch_digests.json          # Map-phase summary digests
│   │   ├── summary_cache.json          # Cached narrative summaries
│   │   └── property_analysis_cache.json # Per-property analysis cache
│   ├── scrapers/
│   │   ├── amazon_scraper.py           # Amazon review scraper
│   │   ├── flipkart_scraper.py         # Flipkart review scraper
│   │   └── mock_data.py                # Mock data generator for scrapers
│   └── main.py                         # FastAPI application (30+ endpoints)
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── DashboardPage.jsx       # Generic analysis dashboard (10 tabs)
│       │   ├── PropertyDashboardPage.jsx # Per-property analysis view
│       │   ├── HotelDashboardPage.jsx  # Hotel-specific analytics
│       │   ├── ReviewPage.jsx          # Guest-facing review browser
│       │   └── UploadPage.jsx          # CSV upload & ingestion
│       ├── components/
│       │   └── dashboard/
│       │       ├── OverviewTab.jsx           # KPI summary cards
│       │       ├── SentimentTab.jsx          # Aspect-based sentiment charts
│       │       ├── TrendsTab.jsx             # Trend alerts & anomaly graphs
│       │       ├── RecommendationsTab.jsx    # Priority action items
│       │       ├── ExecutiveBriefTab.jsx     # AI-generated C-suite brief
│       │       ├── ReviewsTab.jsx            # Paginated review explorer
│       │       ├── CrossComparisonTab.jsx    # Multi-property benchmarks
│       │       ├── EmojiAnalysisTab.jsx      # Emoji sentiment breakdown
│       │       ├── AgentOrchestrationTab.jsx # Pipeline trace viewer
│       │       └── LiveFeedTicker.jsx        # Real-time review feed
│       └── store/
│           ├── reviewStore.js          # Zustand store (analysis state)
│           └── hotelStore.js           # Zustand store (hotel data)
├── hotel_reviews.csv                   # Raw hotel reviews dataset
├── tripadvisor_hotel_reviews.csv       # TripAdvisor reviews (with sub-ratings)
├── ReviewLens.md                       # Detailed hypothesis & solution doc
├── QUICKSTART.md                       # Legacy quick start guide
└── README.md
```

---

## 9. Quick Start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend build |
| Google Gemini API Key | — | LLM & embeddings (default provider) |

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Minimal .env configuration
cat > .env << 'EOF'
GOOGLE_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-2.5-flash-lite
LLM_PROVIDER=gemini
EOF

uvicorn main:app --reload --port 5000
```

### Frontend

```bash
cd frontend
pnpm install && pnpm run dev
```

### LLM Provider Configuration

```bash
# Option 1: Gemini API (default)
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_key

# Option 2: Google Vertex AI with ADC
LLM_PROVIDER=googleADC
GCP_PROJECT=your-project-id
GCP_LOCATION=us-central1

# Option 3: LiteLLM (OpenAI, Anthropic, Azure, etc.)
LLM_PROVIDER=litellm
LITELLM_MODEL=gpt-4o
LITELLM_API_KEY=your_openai_key
```

### Ingest Hotel Reviews

```bash
# Ingest from CSV (batched at 100 reviews, rate-limit safe)
curl -X POST "http://localhost:5000/api/hotel-reviews/ingest?hotel_id=NYCES&max_rows=50" \
  -F "file=@hotel_reviews.csv"
```

### View Pipeline Graph

Open **http://localhost:5000/api/hotel-reviews/graph** in your browser (renders Mermaid diagram client-side).

### Access Property Dashboard

Navigate to **http://localhost:5173/dashboard/NYCES** to view property-specific analysis.

---

## 10. Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/hotel-reviews/ingest` | Ingest CSV through 12-agent pipeline (batched) |
| `GET` | `/api/hotel-reviews/jobs/{id}` | Poll pipeline job status |
| `GET` | `/api/hotel-reviews/mentions/popular` | Get ranked popular mentions |
| `GET` | `/api/hotel-reviews/search` | Filter reviews by mention/sentiment/rating |
| `GET` | `/api/hotel-reviews/semantic-search` | Cosine similarity search with metadata filters |
| `GET` | `/api/hotel-reviews/stats` | Property statistics and sentiment breakdown |
| `GET` | `/api/hotel-reviews/{hotel_id}/summary` | AI narrative summary (Map-Reduce) |
| `GET` | `/api/hotel-reviews/data` | Paginated processed reviews (raw JSON) |
| `GET` | `/api/hotel-reviews/properties` | List all available properties |
| `GET` | `/api/hotel-reviews/graph` | Interactive pipeline visualization (Mermaid) |
| `POST` | `/api/hotel-reviews/vector-store/reload` | Reload in-memory vector store |
| `POST` | `/api/analyze/demo` | Run full pipeline on processed dataset |
| `GET` | `/api/analyze/property/{code}` | Get cached property analysis |
| `POST` | `/api/analyze/property/{code}` | Trigger property-specific analysis |
| `POST` | `/api/brief` | Generate LLM executive brief |
| `GET` | `/api/brief/download/pdf` | Download executive brief as PDF |
| `POST` | `/chat` | AI Q&A chatbot over hotel reviews |

---

## 11. Frontend Dashboard Tabs

| Tab | What It Shows |
|-----|---------------|
| **Overview** | KPI cards, rating distribution, sentiment pie chart, live feed |
| **Sentiment** | Aspect-level sentiment heatmap across 13 hotel features |
| **Trends** | Time-series anomaly graphs, systemic vs isolated alerts |
| **Recommendations** | Prioritized SMART actions with estimated impact |
| **Executive Brief** | AI-generated C-suite report with PDF export |
| **Reviews** | Searchable, filterable review explorer with sentiment badges |
| **Cross-Comparison** | Multi-property benchmarking charts |
| **Emoji Analysis** | Emoji usage patterns and sentiment correlation |
| **Agent Orchestration** | Pipeline execution trace and agent decisions |

---

## 12. Seeded Trends in Demo Data

The synthetic dataset has **deliberately seeded complaint trends** that the Trend Agent catches:

| Hotel | Feature | Trigger Point | Expected Detection |
|-------|---------|--------------|-------------------|
| Grand Monaco Seattle | `cleanliness / housekeeping` | After review #100 | Complaint rate: ~12% → 40%+ |
| City Business Inn | `wifi / connectivity` | After review #45 | Negative spike in business travelers |

> *"Housekeeping complaints have appeared in 40% of reviews in the last 25 entries, up from 12% in the previous batch"* — this maps directly to the Intent to Recommend KPI, enabling proactive staffing decisions.

---

## 13. Path to Production

| Phase | Timeline | Scope |
|-------|----------|-------|
| **Phase 1 — MVP** | Hackathon (48 hrs) | Real hotel data, 12-agent pipeline, React dashboard, multi-LLM support, per-property analysis |
| **Phase 2 — Pilot** | < 4 weeks | 3 real properties, MongoDB Atlas Vector Search, Gemini enterprise endpoint, Kafka ingestion |
| **Phase 3 — Production** | Q3–Q4 2026 | 9,000 properties, Kafka streaming, Aurora PostgreSQL, CDN, real-time ingestion |

**ROI:** $180K–$250K infrastructure cost vs. $30M+ direct booking conversion lift = **>100x ROI in Year 1**

---

## 14. Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | FastAPI · LangGraph · Google Gemini 2.5 Flash · LiteLLM · Vertex AI (ADC) · LangChain InMemoryVectorStore · RapidFuzz |
| **Frontend** | React 18 · Vite · Tailwind CSS · Framer Motion · Zustand · Recharts · Mermaid.js |
| **AI/ML** | gemini-embedding-2 (3072-dim) · Aspect-Based Sentiment · Map-Reduce Summarization · Cosine Similarity Search |
| **Data** | MongoDB Atlas (planned) · JSON file store (current) · CSV ingestion · Batch processing |

---

## Codefest Judging Alignment

| Criterion | Weight | ReviewLens Coverage |
|---|---|---|
| **Hypothesis** | 30% | Clear problem (static categories), measurable KPI impact (NPS +4–8pts, Direct Share +0.2%), 6 value types, 6 personas, revenue quantified ($30M+ opportunity) |
| **Solution Framework** | 25% | Full architecture, 12-agent pipeline, multi-provider LLM, Map-Reduce summarization, per-property caching, executive brief generation |
| **Working POC** | 30% | 30+ API endpoints, 10-tab React dashboard, real hotel data (568K+ lines processed), pipeline visualization, semantic search, property selector, PDF export |
| **Path to Production** | 15% | 3-phase rollout, TCO breakdown, MongoDB Atlas upgrade path, multi-region LLM failover via LiteLLM |

---

<div align="center">

*ReviewLens — Turning guest voices into operational intelligence.*

**Codefest 4.0 · Marriott International**

</div>
