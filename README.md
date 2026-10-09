# Policy-Aware RAG Knowledge Assistant


[![Live Demo](https://img.shields.io/badge/Live%20Demo-onrender.com-blue?style=for-the-badge)](https://policy-aware-rag-assistant.onrender.com/)
[![API Docs](https://img.shields.io/badge/API%20Docs-Swagger-green?style=for-the-badge)](https://policy-aware-rag-assistant.onrender.com/docs)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)](https://github.com/patanchandini/policy-aware-rag-assistant)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](https://opensource.org/licenses/MIT)


A production-grade Retrieval-Augmented Generation (RAG) system that answers
questions using product documents, FAQs, policies, and troubleshooting guides —
with **metadata-aware retrieval**, **temporal filtering**, **access control**,
**conflict resolution**, **mandatory citations**, and **prompt-injection defense**.


**🔗 Live Demo:** [https://policy-aware-rag-assistant.onrender.com](https://policy-aware-rag-assistant.onrender.com/)

**📚 API Docs:** [https://policy-aware-rag-assistant.onrender.com/docs](https://policy-aware-rag-assistant.onrender.com/docs)


Built with FastAPI + PostgreSQL/pgvector + Google Gemini (free tier).

---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Metadata Schema](#metadata-schema)
- [Key Design Decisions](#key-design-decisions)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Metadata-aware retrieval** | Every chunk carries `doc_id`, `version`, `product`, `region`, `access_level`, `effective_date`, `expiry_date` |
| **Temporal filtering** | Current queries ignore expired & future policies; historical queries retrieve the policy active on a given date |
| **Access control** | Server-side enforcement — users only see documents at or below their access level |
| **Conflict resolution** | When documents disagree, the latest applicable policy wins |
| **Mandatory citations** | Every factual claim includes `[Source: <citation_label>]` |
| **Refusal on missing evidence** | If evidence is insufficient or ambiguous, the assistant refuses cleanly |
| **Prompt-injection defense** | Embedded instructions in documents are sanitized and ignored |
| **Free to run** | Uses Google Gemini free tier — no OpenAI billing required |

---

## 🏗 Architecture
USER QUERY
│
▼
QUERY ANALYSIS LAYER (current vs historical, product/region scope)
│
▼
RETRIEVAL LAYER (pgvector + metadata + temporal filters)
│
▼
CONFLICT RESOLUTION (latest applicable policy wins)
│
▼
GENERATION LAYER (LLM with mandatory citations)
│
▼
VALIDATION (citation check + refusal gate)

text

---

## 🧰 Requirements

- **Python** 3.11 or newer
- **Docker Desktop** (Windows / macOS / Linux)
- **WSL 2** (Windows only)
- **Google Gemini API key** (free) — https://aistudio.google.com/apikey
- **VS Code** (recommended)

---

## 🚀 Quick Start

### 1. Open the project

```bash
cd "E:\real-time projects\knowledge-assistant"
code .
2. Create virtual environment
Windows CMD:

cmd
python -m venv .venv
.venv\Scripts\activate
macOS / Linux:

bash
python3 -m venv .venv
source .venv/bin/activate
3. Install dependencies
cmd
pip install --upgrade pip
pip install -r requirements.txt
4. Configure environment
Copy .env.example to .env and fill in your Gemini API key:

env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=knowledge_assistant
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password

GEMINI_API_KEY=AIzaSy...your-real-key
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_LLM_MODEL=gemini-2.5-flash
5. Start PostgreSQL with pgvector
cmd
docker compose up -d
docker compose ps
Wait until rag_postgres shows healthy.

6. Initialize the database schema
cmd
docker exec -i rag_postgres psql -U rag_user -d knowledge_assistant < scripts/init.sql
7. Ingest sample documents
cmd
python -m scripts.ingest_sample
Expected:

text
SUCCESS | Ingested 1 chunks from refund_policy_v1.txt
SUCCESS | Ingested 1 chunks from refund_policy_v2.txt
Ingested 2 chunks.
8. Run the API
cmd
uvicorn src.api.app:app --reload --port 8000
Open: http://127.0.0.1:8000/docs

9. Test the query
In Swagger UI → POST /query → Try it out → paste:

json
{
  "query": "What is the refund window?",
  "user_context": {
    "user_id": "u-001",
    "access_levels": ["public"],
    "authorized_products": ["CloudBackup"],
    "authorized_regions": ["US"]
  }
}
Expected response cites v2.0 (2024) — the expired v1.0 policy is auto-filtered.

📁 Project Structure
text
knowledge-assistant/
├── config/settings.py
├── data/raw/
├── scripts/
│   ├── init.sql
│   ├── ingest_sample.py
│   └── sample_query.json
├── src/
│   ├── api/app.py
│   ├── conflict/
│   ├── generation/
│   ├── ingestion/
│   ├── models/schemas.py
│   ├── retrieval/
│   ├── security/
│   ├── utils/
│   └── pipeline.py
├── docker-compose.yml
├── requirements.txt
└── README.md
🔌 API Reference
GET /health
Returns {"status": "ok"}.

POST /query
Request:

json
{
  "query": "What is the refund window?",
  "historical_date": "2023-06-15",
  "user_context": {
    "user_id": "u-001",
    "access_levels": ["public"],
    "authorized_products": ["CloudBackup"],
    "authorized_regions": ["US"]
  }
}
Response:

json
{
  "answer": "Customers may request a full refund within 14 days of purchase [Source: CloudBackup Refund Policy v2.0 (2024)].",
  "citations": [
    {
      "citation_label": "CloudBackup Refund Policy v2.0 (2024)",
      "doc_id": "refund-v2",
      "version": "2.0",
      "effective_date": "2024-01-01"
    }
  ],
  "refused": false
}
📊 Metadata Schema
Field	Type	Purpose
doc_id	string	Unique ID
version	string	Version
product	string	Product line
region	string	Region
access_level	enum	public / internal / confidential / restricted
effective_date	date	When policy becomes active
expiry_date	date (nullable)	When policy expires
source_type	enum	product_doc / faq / policy / troubleshooting
citation_label	string	Human-readable label
🎯 Key Design Decisions
Pre-filtering for access control (never post-filter)

::jsonb and ::vector casts in ingestion (psycopg2 doesn't auto-adapt)

768-dim embeddings via Gemini (gemini-embedding-001)

Two refusal gates: retrieval threshold + LLM NO_ANSWER

Citation validation: reject any citation not in retrieved set

Temporal filtering by effective_date/expiry_date

🛠 Troubleshooting
Error	Fix
docker: not recognized	Install Docker Desktop
Virtualization support not detected	Enable VT-x / SVM in BIOS; enable WSL 2
ModuleNotFoundError: No module named 'src'	Run from project root
404 NOT_FOUND: text-embedding-004	Use gemini-embedding-001
expected 1536 dimensions, not 768	Recreate table with VECTOR(768)
relation "documents" does not exist	Re-run scripts/init.sql
can't adapt type 'dict'	Use json.dumps() + ::jsonb
📜 License
MIT
===== STOP COPYING HERE =====

text

---

## 📋 Where to Paste

### Step 1 — Open the README file in VS Code

In VS Code's Explorer (left sidebar):

1. Click **`knowledge-assistant`** at the top (the workspace root)
2. Find **`README.md`**
3. Click it to open

**If `README.md` doesn't exist**, create it:
- Right-click the `knowledge-assistant` root folder
- Click **New File**
- Name it exactly: **`README.md`**
- Press Enter

### Step 2 — Clear the file

In the open `README.md` editor:

1. Click inside the editor
2. Press **`Ctrl+A`** (select all)
3. Press **`Delete`** (removes existing content)

### Step 3 — Paste

1. Press **`Ctrl+V`** to paste the copied content

### Step 4 — Save

1. Press **`Ctrl+S`**

---

## 🖼 Visual Guide
┌─────────────────────────────────────────────────┐
│ EXPLORER (VS Code left sidebar) │
├─────────────────────────────────────────────────┤
│ ▼ knowledge-assistant ← workspace root │
│ ├── config/ │
│ ├── data/ │
│ ├── scripts/ │
│ ├── src/ │
│ ├── .env │
│ ├── docker-compose.yml │
│ ├── requirements.txt │
│ └── README.md ◄── CLICK THIS FILE │
└─────────────────────────────────────────────────┘

text

---

## 🎯 Quick Checklist

- [ ] Copy content between `===== START COPYING HERE =====` and `===== STOP COPYING HERE =====` (excluding the markers)
- [ ] Open `README.md` in VS Code
- [ ] `Ctrl+A` → `Delete` to clear
- [ ] `Ctrl+V` to paste
- [ ] `Ctrl+S` to save
- [ ] Preview with `Ctrl+Shift+V` (renders Markdown)

---

## 🔍 How to Verify It Worked

After saving:

1. Press **`Ctrl+Shift+V`** — VS Code opens a **Markdown Preview** tab
2. You should see:
   - Title: **"Policy-Aware RAG Knowledge Assistant"**
   - Badges/sections rendering as headings
   - Tables rendering properly
   - Code blocks with syntax highlighting

If you see raw `#` and `##` symbols, you're in the editor tab, not the preview.

---

## 🎯 Summary

| Action | Details |
|--------|---------|
| **What to copy** | Everything between `===== START COPYING HERE =====` and `===== STOP COPYING HERE =====` |
| **Where to paste** | `E:\real-time projects\knowledge-assistant\README.md` |
| **Before pasting** | Open the file → `Ctrl+A` → `Delete` |
| **After pasting** | `Ctrl+S` to save |
| **To preview** | `Ctrl+Shift+V` |
