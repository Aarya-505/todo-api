import os
import json
import time
from datetime import datetime, timezone
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, ValidationError

# Constants
BASE_URL = "https://books.toscrape.com/catalogue/"
PAGE_1_URL = urljoin(BASE_URL, "page-1.html")
CACHE_DIR = "cache"
OUTPUT_DIR = "output"

# Polite User-Agent
USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/Aarya-505/todo-api)"
HEADERS = {"User-Agent": USER_AGENT}

# Pydantic Schema for Validation
class BookRecord(BaseModel):
    title: str = Field(..., min_length=1)
    product_url: str
    price_text: str
    price_gbp: float = Field(..., gt=0)
    availability_text: str
    rating_text: str | None = None
    description: str | None = None
    source_page: str
    fetched_at: str

def polite_get_with_retry(url, max_retries=2):
    """Fetch a URL with polite headers, timeout, status check, and single retry on 5xx/timeouts."""
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=5)
            
            # Do not retry 404 or 403
            if response.status_code in (404, 403):
                print(f"Client error {response.status_code} for {url}. Skipping retries.")
                return response, False
            
            if response.status_code != 200:
                print(f"Attempt {attempt}: Server error {response.status_code} for {url}.")
                if attempt < max_retries:
                    time.sleep(1) # wait before retry
                    continue
                return response, False
                
            return response, True
            
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt}: Request failed for {url} due to error: {e}")
            if attempt < max_retries:
                time.sleep(1)
                continue
            return None, False
            
    return None, False

def get_or_cache_page(url, cache_filename, delay=0.5):
    """Retrieve page content from cache or fetch live with retry logic & politeness."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, cache_filename)
    
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read(), True, False # content, cached=True, failed=False
    else:
        response, success = polite_get_with_retry(url)
        if not success or not response:
            return None, False, True # failed=True
            
        html_content = response.text
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        time.sleep(delay) # Be polite between live requests
        
        return html_content, False, False

def parse_price(price_text):
    """Clean price string like '£51.77' into float 51.77."""
    if not price_text:
        return 0.0
    cleaned = price_text.replace("£", "").replace("Â", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def scrape_book_details(book_url, source_page_url, index):
    """Visit an individual book page and extract the raw fields safely."""
    cache_name = f"book-{index}.html"
    html_content, cached, failed = get_or_cache_page(book_url, cache_name)
    
    if failed or not html_content:
        return None, True

    soup = BeautifulSoup(html_content, "html.parser")
    
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else None

    price_tag = soup.find("p", class_="price_color")
    price_text = price_tag.get_text(strip=True) if price_tag else None

    avail_tag = soup.find("p", class_="availability")
    availability_text = avail_tag.get_text(strip=True) if avail_tag else None

    rating_text = None
    star_tag = soup.find("p", class_="star-rating")
    if star_tag and star_tag.has_attr("class"):
        classes = star_tag["class"]
        if len(classes) > 1:
            rating_text = classes[1]

    description = None
    desc_header = soup.find("div", id="product_description")
    if desc_header:
        desc_p = desc_header.find_next_sibling("p")
        if desc_p:
            description = desc_p.get_text(strip=True)

    record = {
        "title": title,
        "product_url": book_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page_url,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }
    return record, False

def run_pipeline(inject_fake_url=False):
    start_time = datetime.now(timezone.utc)
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    current_url = PAGE_1_URL
    all_book_links = []
    pages_fetched_count = 0
    cache_hits_count = 0
    failed_pages_count = 0
    
    # 1. Discover catalogue pages & book links
    for page_num in range(1, 4):
        cache_name = f"catalogue-page-{page_num}.html"
        cache_file = os.path.join(CACHE_DIR, cache_name)
        was_cached = os.path.exists(cache_file)
        
        html_content, cached, failed = get_or_cache_page(current_url, cache_name)
        
        if was_cached or cached:
            cache_hits_count += 1
        else:
            pages_fetched_count += 1
            
        if failed or not html_content:
            failed_pages_count += 1
            break
            
        soup = BeautifulSoup(html_content, "html.parser")
        product_pods = soup.find_all("article", class_="product_pod")
        
        for pod in product_pods:
            a_tag = pod.find("h3").find("a")
            if a_tag and a_tag.has_attr("href"):
                relative_url = a_tag["href"]
                absolute_url = urljoin(current_url, relative_url)
                all_book_links.append((absolute_url, current_url))
        
        next_tag = soup.find("li", class_="next")
        if next_tag and next_tag.find("a"):
            current_url = urljoin(current_url, next_tag.find("a")["href"])
        else:
            break

    # Remove duplicates
    seen = set()
    unique_books = []
    for book_url, source_url in all_book_links:
        if book_url not in seen:
            seen.add(book_url)
            unique_books.append((book_url, source_url))

    # Optional checkpoint test: inject one deliberately broken/fake book URL
    if inject_fake_url:
        unique_books.append(("https://books.toscrape.com/catalogue/non-existent-book_999/index.html", PAGE_1_URL))
        print("-> Injected 1 fake URL for failure testing.")

    print(f"Processing {len(unique_books)} book URLs safely...")

    valid_records = []
    error_records = []
    stored_books = {}

    for idx, (book_url, source_url) in enumerate(unique_books, start=1):
        # Check cache for book detail
        cache_name = f"book-{idx}.html"
        cache_file = os.path.join(CACHE_DIR, cache_name)
        was_cached = os.path.exists(cache_file)
        
        raw_record, failed = scrape_book_details(book_url, source_url, idx)
        
        if was_cached:
            cache_hits_count += 1
        else:
            pages_fetched_count += 1

        if failed or not raw_record:
            failed_pages_count += 1
            error_records.append({
                "url": book_url,
                "error": "Page fetch failed or returned non-200 status"
            })
            continue

        # Normalize price
        price_gbp = parse_price(raw_record["price_text"])
        normalized_data = {
            **raw_record,
            "price_gbp": price_gbp
        }

        # Validate with Pydantic
        try:
            validated_book = BookRecord(**normalized_data)
            stored_books[validated_book.product_url] = validated_book.model_dump()
        except ValidationError as e:
            error_records.append({
                "record": raw_record,
                "error": str(e)
            })

    valid_records = list(stored_books.values())
    end_time = datetime.now(timezone.utc)
    duration_seconds = (end_time - start_time).total_seconds()

    # Save output files
    books_file = os.path.join(OUTPUT_DIR, "books.json")
    errors_file = os.path.join(OUTPUT_DIR, "errors.json")
    report_file = os.path.join(OUTPUT_DIR, "run-report.json")

    with open(books_file, "w", encoding="utf-8") as f:
        json.dump(valid_records, f, indent=2, ensure_ascii=False)

    with open(errors_file, "w", encoding="utf-8") as f:
        json.dump(error_records, f, indent=2, ensure_ascii=False)

    run_report = {
        "start_time": start_time.isoformat(),
        "duration_seconds": round(duration_seconds, 2),
        "pages_fetched": pages_fetched_count,
        "cache_hits": cache_hits_count,
        "valid_records": len(valid_records),
        "invalid_records": len(error_records),
        "failed_pages": failed_pages_count
    }

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(run_report, f, indent=2)

    print(f"\n--- Stage 5 Run Report ---")
    print(json.dumps(run_report, indent=2))

    return run_report

if __name__ == "__main__":
    # Test normal run first, or pass inject_fake_url=True to test the failure checkpoint!
    run_pipeline(inject_fake_url=False)