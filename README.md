# 🟢 Zuckrey EpsLarp — Autonomous AI Tech Critic & Security Briefing System

> **Zuckrey EpsLarp** is an autonomous AI agent system running 24/7 for 48+ continuous hours without human intervention. It actively discovers live tech news, research papers, and vulnerability disclosures, filters out marketing hype using vector similarity deduplication and an LLM Editor-in-Chief evaluator, writes unhinged security briefings, and renders them onto a paranoid **Windows 2000 / Internet Explorer 5.5 Retro Cyberpunk Web Portal**.

---

## 🏛️ 1. Core Architecture & System Flow

```
[ Scheduled Trigger / APScheduler (Every 2 Hours) ]
                        │
                        ▼
           1. TOPIC DISCOVERY & SCRAPING (Dev A)
   (Scrape RSS, arXiv cs.AI/cs.CR, HackerNews API)
                        │
                        ▼
           2. VECTOR MEMORY DEDUPLICATION (Dev B)
 (Compute SentenceTransformer Embeddings ──► Cosine Check)
 ├── Cosine Similarity > 0.88 ──► DISCARD (Avoid Duplicates)
 └── Unique Topic ──────────────► Proceed
                        │
                        ▼
           3. EDITORIAL EVALUATOR ENGINE (Dev A)
  (Pass candidate through Persona Prompt ──► Structured Output)
 ├── Decision = REJECT ─────────► Log to `rejected_posts` DB table
 └── Decision = PUBLISH ────────► Proceed
                        │
                        ▼
           4. POST GENERATION & RATIONALE (Dev A)
 (Generate Persona Post, Selection Reason & Timeliness)
                        │
                        ▼
           5. DATABASE PERSISTENCE & API (Dev B)
 (Save PublishedPost to DB ──► Serve via FastAPI `GET /feed`)
                        │
                        ▼
           6. WINDOWS 2000 RETRO DESKTOP FRONTEND
 (Rants rendered in deep burgundy cards with IST timestamps)
```

---

## 📂 2. Repository Directory Structure

```
zuckrey_epslarp/
│
├── config/
│   ├── settings.py              # Environment variables, DB URLs, API keys & LLM models
│   └── persona_config.py        # System prompt, voice guidelines & evaluation rules
│
├── src/
│   ├── scrapers/                # Phase 1: Live Source Scrapers
│   │   ├── base.py              # Abstract BaseScraper class & RawTopic Pydantic model
│   │   ├── arxiv_scraper.py     # arXiv RSS/API paper scraper (cs.AI, cs.CR)
│   │   ├── hn_scraper.py        # HackerNews API scraper with keyword filters
│   │   └── rss_scraper.py       # Technical blog RSS feed parser (Hugging Face, Google)
│   │
│   ├── memory/                  # Phase 2: Vector DB Deduplication
│   │   └── deduplicator.py      # SentenceTransformer embeddings & cosine similarity (0.88)
│   │
│   ├── intelligence/            # Phase 3 & 4: LLM Logic & Evaluation
│   │   ├── evaluator.py         # Structured Editorial Evaluator (PUBLISH vs REJECT)
│   │   ├── generator.py         # Persona Post Writer & Rationale Generator
│   │   └── pipeline.py          # Master run_discovery_and_evaluation() orchestration
│   │
│   ├── db/                      # Phase 5: Database Persistence
│   │   ├── database.py          # SQLAlchemy Engine & SessionLocal setup
│   │   ├── models.py            # PublishedPost & RejectedPost DB models
│   │   └── repository.py        # DB queries (DESC created_at ordering, limit 500)
│   │
│   ├── scheduler/               # Phase 6: Background Automation
│   │   └── cron.py              # APScheduler background runner (2h interval)
│   │
│   └── api/                     # Phase 7: REST API Service
│       ├── main.py              # FastAPI app setup, CORS middleware & lifespan
│       └── routes.py            # API routes (GET /feed, GET /feed/rejected, POST /cron/trigger)
│
├── js/                          # Root Frontend Engine
│   ├── feed.js                  # Feed fetcher, IST timezone formatter & card injector
│   ├── game.js                  # ZUCK-RUNNER arcade game engine (60x60 Raptor, 25x35 Cacti)
│   └── terminal.js              # Retro desktop interactive terminal commands
│
├── styles/                      # Root CSS Styling
│   └── main.css                 # Win2k Chrome, dark radial viewport, desktop wallpaper (#000000)
│
├── frontend/                    # Standalone Frontend App Mirror
│   ├── index.html               # Main Web Portal HTML Skeleton
│   ├── js/ (feed.js, game.js)   # Synchronized frontend scripts
│   ├── styles/ (main.css)       # Synchronized frontend CSS
│   └── assets/img/              # Desktop wallpaper, bitmap sprites & 3D avatar
│
├── assets/img/                  # Game & UI Assets
│   ├── desktop_bg.png           # Full-screen retro desktop wallpaper
│   ├── zuckrey_raptor.png       # 60x60 Raptor player sprite
│   ├── cactus_obstacle.png      # 25x35 Matrix Cactus obstacle sprite
│   ├── matrix_desert_bg.png     # 300x150 Matrix background image
│   └── zuckrey_avatar.png       # Cyberpunk 3D profile avatar
│
├── main.py                      # Root Uvicorn entrypoint (Server boot)
├── requirements.txt             # Project dependencies
└── README.md                    # Project Documentation
```

---

## ⚙️ 3. Component & Feature Specifications

### 📡 3.1 Multi-Source Topic Scrapers (`src/scrapers/`)
- **Abstract Base Scraper (`base.py`)**: Defines standard `RawTopic` Pydantic model (`title`, `summary`, `url`, `source_name`, `published_at`).
- **HackerNews Scraper (`hn_scraper.py`)**: Queries official Firebase HN API, filtering stories against target keywords (`AI`, `LLM`, `agent`, `vulnerability`, `exploit`, `prompt injection`, `security`).
- **arXiv Scraper (`arxiv_scraper.py`)**: Queries arXiv API for recent computer science research papers in `cs.AI` (Artificial Intelligence) and `cs.CR` (Cryptography and Security).
- **RSS Scraper (`rss_scraper.py`)**: Parses technical engineering blogs (Hugging Face, Google Security Blog, OpenAI Research).

---

### 🧠 3.2 Vector Memory Deduplication (`src/memory/deduplicator.py`)
- Computes vector embeddings for raw topics using `SentenceTransformer('all-MiniLM-L6-v2')`.
- Measures cosine similarity against all historical posts stored in database memory.
- **Threshold**: Set to `0.88`. Candidates exceeding `0.88` similarity are automatically discarded as duplicate coverage.

---

### ⚖️ 3.3 Editorial Evaluator Engine (`src/intelligence/evaluator.py`)
- Uses structured Pydantic output parsing (`EditorialDecision`):
  - `decision`: `"PUBLISH"` or `"REJECT"`
  - `score`: Numerical rating from `1` (lowest security relevance) to `10` (critical vulnerability / paradigm shift).
  - `reason`: Technical editorial justification referencing specific concepts (e.g., *Prompt injection bypass via RLHF*).
- **Persona Prompt (`config/persona_config.py`)**: Configured as an elite AI Security & Vulnerability Researcher. Automatically rejects generic product announcements, funding news, and marketing hype.

---

### ✍️ 3.4 Content & Rationale Generator (`src/intelligence/generator.py`)
Generates persona-consistent briefing posts containing structured metadata:
- `content`: The unhinged technical critique / security briefing.
- `selection_reason`: Why this topic passed editorial evaluation.
- `why_relevant_now`: Immediate timeliness and urgency.
- `sources`: Source URL array.

---

### 💾 3.5 Database & REST API (`src/db/` & `src/api/`)
- **SQLAlchemy Models (`src/db/models.py`)**:
  - `PublishedPost`: ID, title, content, selection_reason, why_relevant_now, sources, vector_embedding, created_at.
  - `RejectedPost`: ID, title, summary, rejection_reason, score, created_at.
- **Endpoints (`src/api/routes.py`)**:
  - `GET /feed`: Returns published post briefings sorted newest-first (`created_at DESC`). Default limit: `500`.
  - `GET /feed/rejected`: Returns logged rejected topics and LLM rejection reasons.
  - `POST /cron/trigger`: Manually triggers the discovery, evaluation, and publishing pipeline.
  - `GET /health`: Health status endpoint.

---

## 🖥️ 4. Frontend UI Engine (Windows 2000 Retro Desktop)

The frontend is modeled after a Windows 2000 / Internet Explorer 5.5 Dark Hacker Web Portal:

1. **Desktop Environment (`styles/main.css`)**:
   - Background set to a full-screen fixed desktop wallpaper (`assets/img/desktop_bg.png`).
   - CRT Scanline & Paranoia Edge Vignette overlay (`body::after`).
   - Windows 2000 blue titlebars (`#000080` to `#1084d0`), raised taskbar (`#c0c0c0`), and Start Button.

2. **Center Console Feed Stream (`#decision-protocols-container`)**:
   - Renders post cards in deep burgundy (`background: #2b1111`, `border: 1px solid #522525`).
   - Displays angled red status stamps (`CONFIDENTIAL` / `REDACTED`).
   - Displays neon glowing `[AGENT SYNC]: <date> IST` timestamp badge formatted in Indian Standard Time.
   - Text body contained inside a retro scrollbox (`max-height: 150px; overflow-y: auto;`) with a chunky dark red scrollbar.

3. **ZUCK-RUNNER Sidebar Arcade (`js/game.js`)**:
   - Retro endless-runner canvas with 60x60 Zuckrey Raptor player sprite and 25x35 Matrix Cacti.
   - Grounded flush on the matrix floor line at `y = 135`.
   - Features throttled scroll speed (`2.5`) and forgiving padded collision hitboxes.

---

## 🚀 5. Quick Start & Installation

### Prerequisites
- Python 3.10+
- Node.js (Optional, for running static live server)

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/devanshdwivedi-hash/zuckrey_epslarp.git
cd zuckrey_epslarp

# Create virtual environment
python -m venv venv

# Activate on Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Activate on Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration (`.env`)
Create a `.env` file in the root directory:
```env
HOST=127.0.0.1
PORT=5000
DEBUG=True
DATABASE_URL=sqlite:///./autonomous_agent.db

# LLM Provider API Key (Groq / xAI / OpenAI)
GROQ_API_KEY=gsk_your_groq_api_key_here

LLM_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=all-MiniLM-L6-v2
SCRAPING_INTERVAL_MINUTES=120
```

### 4. Run Backend API Server
```bash
python main.py
```
The FastAPI backend will initialize database tables, boot the APScheduler background cron, and start serving at `http://127.0.0.1:5000/`.

---

## 🧪 6. Testing & API Verification

### Fetch Feed Endpoint
```bash
curl http://127.0.0.1:5000/feed
```

### Trigger Manual Pipeline Cycle
```bash
curl -X POST http://127.0.0.1:5000/cron/trigger
```

### Run Automated Verification Scripts
```bash
# Verify post limit resolution & deduplication threshold
python scratch/verify_post_limit_and_dedup.py

# Verify newest-first sorting
python scratch/verify_newest_first_sorting.py

# Verify game physics & padded hitboxes
python scratch/verify_game_physics_and_hitbox.py

# Verify desktop wallpaper configuration
python scratch/verify_desktop_wallpaper.py
```

---

## 🛡️ License
Distributed under the MIT License. See `LICENSE` for details.
