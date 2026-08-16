# The Polite Scraper — FlyRank Backend Track (Assignment A9)

A polite, robust, and strongly typed web scraping pipeline integrated with a **FastAPI** backend. It extracts book details from the Books to Scrape sandbox, transforms messy HTML into validated JSON records, survives network/parsing failures gracefully, and generates transparent execution reports.

---

## 🎯 Target Classification

- **Target Site:** [Books to Scrape](https://books.toscrape.com/)
- **Why this target:** As stated directly on [toscrape.com](https://toscrape.com/), Books to Scrape is *"a fictional bookstore that desperately wants to be scraped. It's a safe place for beginners learning web scraping and for developers validating their scraping technologies as well."* It is an explicitly provided public sandbox for practicing scraping techniques.
- **Scraping Scope:** Strictly limited to the first **3 catalogue pages** (a total of **60 books**).
- **Data Collected:** Book Title, Price, Star Rating (1–5), Availability / Stock Count, Product Description, UPC, Category, and Product Image URL.
- **Why this data collection is appropriate:** The target is a synthetic practice playground designed specifically for testing extraction logic, and collecting product metadata across 60 items at a throttled rate places negligible load on the server while fulfilling educational learning objectives.
- **Robots.txt Analysis:** Request to `https://books.toscrape.com/robots.txt` returned `404 Not Found` (**no robots file found**). As a sandbox with explicit site-level permission, no crawling restrictions are defined, though polite rate limiting is still strictly applied.

> **Ethics & Compliance Statement:**  
> **"I will not reuse this code on another site without checking its rules and terms first."**

---

## 🏗️ Architecture & Pipeline

```text
[Stage 0: Target Classification & Robots.txt Check]
                        ↓
[Stage 1: Polite Fetcher & Rate Throttling]
                        ↓
[Stage 2: BeautifulSoup Raw HTML Extraction]
                        ↓
[Stage 3: Normalizer (Currency, Star Ratings, Absolute URLs)]
                        ↓
[Stage 4: Pydantic Schema Validation & Quarantine Guard]
                        ↓
[Stage 5: Data Storage (books.json)]
                        ↓
[Stage 6: Transparent Run Reporting]
```

---

## 🚀 Quick Start (Under 5 Minutes)

### 1. Prerequisites
- Python 3.10+ installed

### 2. Setup Virtual Environment & Dependencies
```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the Scraper via CLI
```bash
python -m src.main --scrape
```

### 4. Run the FastAPI Backend Server
```bash
uvicorn src.main:app --reload --port 8000
```
Open **Interactive API Docs (Swagger UI)** at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API status and overview |
| `POST` | `/api/scrape` | Trigger a polite scraping run |
| `GET` | `/api/status` | Current pipeline status |
| `GET` | `/api/books` | Query, filter, and paginate scraped books |
| `GET` | `/api/books/{upc}` | Get book details by UPC |
| `GET` | `/api/report` | View the latest honest execution report |
| `GET` | `/api/export/json` | Download `books.json` directly |

---

## 🧪 Testing
```bash
pytest -v
```
