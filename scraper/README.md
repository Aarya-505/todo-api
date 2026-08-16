# FlyRank Backend Track - Assignment A9: The Polite Scraper

A robust, polite, and resilient web scraping pipeline built for the **Books to Scrape** practice sandbox. It fetches catalogue pages, discovers all 60 book URLs, extracts structured details, cleans prices, validates schemas via Pydantic, handles failures gracefully, and outputs clean JSON records along with a run report.

---

## 🚀 Quick Start (Run in under 5 minutes)

Follow these steps to clone, set up, and run the scraper:

1. **Clone the repository and navigate into the scraper folder:**
   ```bash
   git clone <your-public-repo-url>
   cd todo-api/scraper
   ```
2. **Set up a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   
   # On Windows:
   .\venv\Scripts\Activate
   
   # On macOS/Linux:
   source venv/bin/activate
   
   pip install requests beautifulsoup4 pydantic

   ```
3. **Run the scraper:**
    ```bash
    python src/main.py
    ```
---

## 🎯 Target Classification & Scope

1. Target Website: Books to Scrape
2. Purpose: Practice sandbox built specifically for learning and testing web scraping safely.
3. Scope: The first 3 catalogue pages only, discovering exactly 60 unique book detail pages.
4. Robots.txt Check: Checked https://books.toscrape.com/robots.txt and noted that no robots file was found (404 Not Found), allowing standard polite practice.
5. Ethics Statement: I will not reuse this code on another site without checking its rules and terms first. Official APIs should be used when available; never bypass logins, paywalls, or blocks; collect only what is necessary.

--- 

## 🛡️ Politeness & Resilience Rules

1. User-Agent: Identifies software explicitly with provenance contact info (FlyRankInternship-A9/1.0 (+https://github.com/Aarya-505/todo-api)).
2. Timeouts & Rate Limiting: Implements a strict 5-second request timeout and a 500 ms delay between live network requests.
3. Caching: Saves all fetched pages locally inside cache/ to ensure development reruns never spam the server.
4. Idempotency: Uses canonical absolute product_url identities so rerunning the pipeline updates records safely without duplicates.
5. Fault Tolerance: Catches connection errors or 5xx server issues with a single retry rule; client errors like 404 are skipped instantly without crashing.

---

## 📋 Record Schema (Pydantic Validation)

Every scraped book record is validated against this strict schema before storage:

1. title (string, required)
2. product_url (string / absolute URL, required)
3. price_text (string raw price, e.g., "£51.77", required)
4. price_gbp (float numeric price, e.g., 51.77, required)
5. availability_text (string, required)
6. rating_text (string or null, e.g., "Three", optional)
7. description (string or null, optional)
8. source_page (string provenance link, required)
9. fetched_at (ISO timestamp string, required)

---

## 📊 Sample Run Report (output/run-report.json)

{
  "start_time": "2026-08-16T16:18:51.377937+00:00",
  "duration_seconds": 2.13,
  "pages_fetched": 0,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0
}

---

## 💡 Why No Browser Was Needed

The target site is server-side rendered HTML. All required text, prices, descriptions, and pagination links are fully present in the raw HTML payload returned by an ordinary HTTP request. Utilizing a headless browser (like Playwright or Selenium) would introduce massive unnecessary memory overhead, slower execution speeds, and higher compute costs without adding any data value.