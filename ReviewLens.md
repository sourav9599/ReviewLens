# ReviewLens
### AI-Powered Dynamic Review Categorization & Filtering for Marriott Properties

> **Codefest 4.0 | BYOT Theme**
> **Enterprise KPIs Addressed:** Intent to Recommend · RevPAR · Digital Direct Share · Marriott Bonvoy Occupancy & Enrollments

---

## 1. Hypothesis
**Weightage: 30% | Score Range: 0–4**

---

### What Are We Addressing?

**A Problem that exists and is compounding.**

Marriott currently surfaces guest reviews with a fixed, coarse set of categories — Cleanliness, Service, Location, Room Quality, Food & Beverage, and Check-in Experience. These six buckets were designed for star-rating aggregation, not discovery.

The result: a guest who wants to know *"Is the gym actually open at 5 AM?"* or *"How is the noise level on floors near the elevator?"* must read dozens of unstructured text reviews to find the answer. A property manager who wants to understand *"What specifically is driving our declining Intent to Recommend score?"* gets a blended 4.1/5.0 with no actionable signal.

**This is a New Opportunity — Technology + Functional.**

Large Language Models can now classify, extract, and cluster unstructured review text into an unlimited taxonomy of meaningful sub-topics in near real-time. ReviewLens uses this capability to dynamically tag every review sentence with fine-grained categories beyond the static six — enabling both guest-facing filtering and associate-facing operational intelligence.

---

### The Business Problem in Numbers

| Signal | Current State | Target with ReviewLens |
|---|---|---|
| Marriott KPI: Intent to Recommend (NPS) | Target ≥ 65 (Yellow zone: 55–64) | Actionable sub-topic alerts close gap faster |
| Guest review actionability | 6 static categories | 30–50 dynamic topic clusters per property |
| Time for property manager to identify top complaint theme | Manual review scan: ~45 min/day | Automated topic dashboard: <2 min |
| OTA vs. Direct review engagement | Guests visit OTAs for richer review filters | Richer direct channel experience reduces OTA dependency |
| Review response SLA | Target: 90% responded within 48 hrs | AI-generated response drafts tied to topic clusters |

---

### What Value Will ReviewLens Deliver?

**Functional Value**
- Guests searching on marriott.com can filter reviews by granular topics: *"Pool," "Gym equipment," "Pillow quality," "Valet wait time," "Late checkout flexibility"* — topics that emerge organically from real reviews, not a pre-set dropdown.
- Property managers get a ranked topic heatmap: *"Noise (elevator): 23 mentions, sentiment 2.1/5 — trending negative over last 30 days."*

**Lifecycle Value**
- First-time bookers gain confidence from specific, relevant review content → increases conversion.
- Repeat guests (Bonvoy members) see reviews tagged to their preference profile (*"Business Traveler: quiet floor, fast Wi-Fi"*) → strengthens loyalty engagement at the discovery stage.

**Emotional Value**
- Guests feel heard when their specific feedback (even buried in a paragraph) is surfaced and visible. Transparent, granular reviews signal that Marriott takes feedback seriously.
- Associates feel equipped: instead of a vague "service score dropped," they receive *"Check-in wait time: 18 negative mentions this week."*

**Brand Value**
- Positions Marriott's direct digital channel as offering a *superior* review browsing experience vs. TripAdvisor and Booking.com — both of which still rely on static category filters.
- Differentiates the Marriott Bonvoy app as the authoritative source of richer property intelligence.

**Economic Value**
- See quantified estimates below.

---

### Who Is the Recipient of This Value?

| Persona | Primary Use | Value Type |
|---|---|---|
| **Prospective Guest (Leisure)** | Filter reviews by topic before booking | Functional, Emotional |
| **Prospective Guest (Business Traveler)** | Filter by "Wi-Fi," "Quiet floor," "Early check-in" | Functional |
| **Marriott Bonvoy Member** | Personalized review feed based on preference history | Lifecycle, Emotional |
| **Property General Manager** | Operational topic heatmap, SLA dashboard | Functional, Economic |
| **Marriott Brand/Quality Team** | Cross-property topic benchmarking | Brand, Economic |
| **Digital Marketing / CRM Team** | Identify high-sentiment topics to amplify in campaigns | Brand, Economic |

---

### Quantified Expected Business Value

**1. Incremental Direct Revenue (Digital Direct Share KPI)**

> Marriott's KPI health metric flags Direct Booking Share at 35–44% (Yellow zone; target ≥ 45%).
> Industry research (Phocuswire, 2024) shows that richer review content on hotel brand websites increases direct booking conversion by **3–7%** relative to OTA-equivalent pages.
> At Marriott's scale (~$15B room revenue), a 1% shift from OTA to direct = ~$150M in commission savings annually.
> ReviewLens targets a conservative **0.2% conversion lift** in the 48-hour MVP scope → **~$30M incremental margin opportunity** at full rollout.

**2. Operational Efficiency (EBITDA Growth KPI)**

> Property managers currently spend an estimated 30–45 minutes per day manually scanning reviews to identify service recovery priorities.
> With ReviewLens topic dashboards, this shrinks to <5 minutes.
> Across ~9,000 Marriott properties globally, that is **~35,000 manager-hours saved per day** — recoverable as associate-facing service time.

**3. Intent to Recommend Score Improvement**

> Marriott's KPI target: NPS ≥ 65 (Green). Current benchmark is in the 55–64 Yellow zone.
> Hotels that implement structured service-recovery loops driven by review topic intelligence have shown **4–8 point NPS improvement** within 90 days (Cornell Hospitality Quarterly, 2023).
> ReviewLens provides the topic-level signal that makes that loop actionable.

**4. Bonvoy Enrollment Conversion (Enrollments KPI)**

> Personalized, preference-matched review feeds are a tangible Bonvoy benefit — increasing the perceived value of membership during the booking discovery phase.
> Estimated **0.5% lift in Bonvoy enrollment rate** among first-time bookers who engage with topic-filtered reviews.

---

## 2. Solution Framework / Modeling
**Weightage: 25% | Score Range: 0–3**

---

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA INGESTION LAYER                      │
│  Mock Review Dataset (synthetic, structured like Marriott data)  │
│  [property_id, review_text, star_rating, stay_date, source]      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI CATEGORIZATION ENGINE                      │
│                                                                  │
│   TIP.ai / Claude Sonnet 4.5 (Anthropic)                        │
│                                                                  │
│   Prompt strategy:                                               │
│   • Zero-shot sentence-level topic extraction                    │
│   • Dynamic taxonomy: no pre-defined category list              │
│   • Output: [{sentence, topic, sentiment_score, confidence}]     │
│                                                                  │
│   Fallback: keyword clustering (TF-IDF) for offline demo         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   STRUCTURED REVIEW STORE                        │
│   SQLite (demo) → PostgreSQL (production)                        │
│   Schema: review_id, sentence_id, topic, sentiment,              │
│            confidence, property_id, review_date                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
┌─────────────────────┐   ┌──────────────────────────────────┐
│   GUEST PORTAL UI   │   │   PROPERTY MANAGER DASHBOARD     │
│                     │   │                                  │
│  • Topic filter     │   │  • Topic heatmap (by volume +    │
│    chips (dynamic)  │   │    sentiment trend)              │
│  • Review cards     │   │  • Actionable alerts:            │
│    with highlighted │   │    "Noise: ↑18% complaints       │
│    sentences per    │   │     this week"                   │
│    topic            │   │  • AI-drafted response template  │
│  • Sentiment badge  │   │    per topic cluster             │
└─────────────────────┘   └──────────────────────────────────┘
```

---

### Technology Choices

| Layer | Technology | Justification |
|---|---|---|
| **LLM Engine** | Anthropic Claude Sonnet 4.5 (via TIP.ai) | Available in Marriott's TIP space per "Models vs Use Cases" Confluence page; excels at structured extraction |
| **Backend API** | Python + FastAPI | Lightweight, async-native, aligns with TIP.OS platform Python libraries documented in Confluence |
| **Frontend** | React + TypeScript + Tailwind CSS | Matches UXL (GQL) team stack; component-based for easy integration into marriott.com |
| **Data Store** | SQLite (demo) / PostgreSQL (production) | Zero-cost for hackathon; production-ready migration path |
| **Hosting** | AWS Lambda + S3 (demo) | Within $250 cloud budget; scales to production on existing Marriott AWS infrastructure |
| **Mock Data** | Python Faker + GPT-generated hotel reviews | 200 synthetic reviews across 5 mock properties; no proprietary Marriott data used |

---

### Integration with Current / Future Marriott Systems

**Current (Inflight Integration Points — no Marriott infra used in demo):**
- **UXL / Shop & Book (GQL):** ReviewLens topic tags are designed to integrate as a filter parameter in UXL's search and property detail APIs. The UXL Search Squad B page explicitly lists "catalog integrations" as a current workstream.
- **mHelp Property Agent (future):** Topic heatmap data can feed a future mHelp sub-agent for property managers — *"Your top 3 service recovery priorities this week are…"* — aligning with the mHelp progressive agentic model.
- **Marketing Platforms (MPAD):** High-sentiment topic clusters (e.g., "Spa: 4.8/5, 89 mentions") feed CampaignCraft-style briefs for SMS/email amplification.

**Data Flow in Production:**
```
Marriott Review Platform → Kafka topic → ReviewLens Categorization Service
                                              ↓
                                      PostgreSQL Review Store
                                              ↓
                         ┌────────────────────┴────────────────────┐
                         ↓                                         ↓
                  UXL GraphQL API                     Property Manager Portal
               (guest-facing filter)              (operational intelligence feed)
```

---

## 3. Code Execution / Working POC
**Weightage: 30% | Score Range: 0–3**

---

### What the POC Demonstrates

The working demo runs entirely on synthetic data (zero Marriott infrastructure) and shows:

1. **Batch categorization pipeline** — 200 mock hotel reviews run through Claude Sonnet 4.5 to extract dynamic topic tags and sentiment scores per sentence.
2. **Guest-facing review browser** — React UI with dynamic topic filter chips that update in real time as topics are detected (no hardcoded list).
3. **Property Manager dashboard** — Topic heatmap ranked by mention volume and sentiment trend, with AI-generated service recovery alerts.
4. **Response draft generator** — Clicking a topic cluster generates an AI-drafted manager response template.

### Demo Flow (2-minute walkthrough)

```
Step 1: [Manager View] See heatmap — "Noise near elevator: 23 mentions, 2.1/5 ↓ trending"
Step 2: [Click topic] See all review sentences tagged "Noise" highlighted in context
Step 3: [Click "Draft Response"] Claude generates: "We hear you on the noise levels on
         floors 3–5 near the elevator bank. We are installing sound-dampening panels
         in Q3 2026 and have added this to your welcome note so you can request a
         higher floor at check-in."
Step 4: [Guest View] Switch to guest portal — filter reviews by "Pool", "Gym", "Valet"
Step 5: [Show] Only reviews mentioning those topics appear, sentences highlighted
```

### Repository Structure

```
reviewlens/
├── backend/
│   ├── main.py                  # FastAPI app (5 endpoints)
│   ├── categorizer.py           # Claude Sonnet 4.5 topic extraction
│   ├── mock_data.py             # 200 synthetic reviews generator
│   ├── models.py                # SQLite schema + ORM
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TopicHeatmap.tsx       # Manager dashboard
│   │   │   ├── ReviewBrowser.tsx      # Guest filter UI
│   │   │   ├── TopicChip.tsx          # Dynamic filter chips
│   │   │   └── ResponseDrafter.tsx    # AI response generator
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── package.json
└── README.md
```

### API Endpoints (FastAPI)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/reviews/categorize` | Run Claude on a batch of reviews, store tagged results |
| `GET` | `/topics/{property_id}` | Return ranked topic heatmap for a property |
| `GET` | `/reviews/{property_id}?topic=Noise` | Return filtered review sentences by topic |
| `POST` | `/response/draft` | Generate AI manager response draft for a topic cluster |
| `GET` | `/health` | Health check |

---

## 4. Path to Production
**Weightage: 15%**

---

### Phase 1 — MVP (Hackathon, 48 hrs, $0–$50 cloud cost)
- Synthetic dataset (200 reviews, 5 mock properties)
- Claude Sonnet 4.5 via Anthropic API (personal key)
- SQLite local store
- React frontend on localhost
- FastAPI backend on localhost
- Demo-ready in 48 hours

### Phase 2 — Pilot (< 4 Weeks, $500–$2,000/month)
- Deploy backend on AWS Lambda + API Gateway (serverless, auto-scaling)
- Move to RDS PostgreSQL for persistent store
- Integrate with 3 real properties' public review feed (no Marriott infra — use public review aggregator)
- Replace personal Anthropic key with TIP.ai enterprise endpoint
- Soft-launch guest filter UI on a staging version of marriott.com property detail page
- **Inflight alignment:** Propose integration via UXL Shop & Book Squad A (active GQL space) as a new GraphQL resolver `propertyReviewTopics(propertyId)`

### Phase 3 — Production Scale (Q3–Q4 2026, ~$15,000–$25,000/month infrastructure)

| Component | Production Choice | Cost Driver |
|---|---|---|
| LLM Inference | TIP.ai Claude Sonnet 4.5 (bulk pricing) | ~$0.003/1K tokens × ~10M reviews/month |
| Data pipeline | AWS Kinesis → Lambda (streaming categorization) | ~$3K/month |
| Storage | Amazon Aurora PostgreSQL (multi-region) | ~$5K/month |
| CDN / Frontend | CloudFront + S3 | ~$500/month |
| Observability | AWS CloudWatch + Datadog | ~$1K/month |

**Total Cost of Ownership (Year 1):** ~$180,000–$250,000 infrastructure
**vs. Estimated Revenue Impact:** $30M+ in direct booking conversion lift + operational savings
**ROI:** >100x in Year 1

### Governance & Compliance
- All LLM processing uses anonymized/aggregated review text — no PII in prompt payloads
- Follows TIP.ai data handling standards (documented in Marriott TIP Confluence space)
- Review topic tags stored per Marriott data retention policy
- Aligns with mHelp Agent Integration Standards: ReviewLens acts as a **knowledge agent** (informational stage) per the mHelp progressive maturity model

### Integration Roadmap

```
Now (Hackathon POC)
  └─→ Phase 2: UXL GraphQL integration (property detail page topic filters)
       └─→ Phase 3: Bonvoy app personalized review feed (preference-matched topics)
            └─→ Phase 4: mHelp Property Manager Agent (topic heatmap → action recommendations)
                 └─→ Phase 5: Cross-brand benchmarking (brand quality team analytics)
```

---

## Codefest Judging Alignment Summary

| Criterion | Weight | ReviewLens Coverage |
|---|---|---|
| **Hypothesis** | 30% | ✅ Clear problem (static review categories), measurable KPI impact (NPS +4–8pts, Direct Share +0.2%), 6 value types addressed, 5 personas identified, revenue quantified ($30M+ opportunity) |
| **Solution Framework** | 25% | ✅ Full architecture diagram, technology justification, integration with UXL/mHelp/MPAD, production data flow |
| **Working POC** | 30% | ✅ 5 API endpoints, 4 React components, 2-minute demo flow, runs on synthetic data, zero Marriott infra |
| **Path to Production** | 15% | ✅ 3-phase rollout, TCO breakdown, governance/compliance, integration roadmap to 5 future systems |

**Enterprise KPIs Addressed:**
- **Intent to Recommend** — primary driver (NPS signal → faster service recovery loops)
- **Digital Direct Share** — richer on-site review experience reduces OTA dependency
- **RevPAR** — higher conversion from review-confident bookers
- **Marriott Bonvoy Enrollments** — personalized review feed as a visible loyalty benefit

---

*ReviewLens | Codefest 4.0 | Built with TIP.ai (Claude Sonnet 4.5) · AWS · React · FastAPI · Synthetic Data Only*
