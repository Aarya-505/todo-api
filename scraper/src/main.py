import os
import json
import time
from datetime import datetime, timezone
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, HttpUrl, ValidationError

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

def polite_get(url):
    """Fetch a URL with polite headers, timeout, and status check."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code != 200:
            print(f"Failed to fetch {url}. Status code: {response.status_code}")
            return None
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return None

def get_or_cache_page(url, cache_filename, delay=0.5):
    """Retrieve page content from cache or fetch live with politeness."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, cache_filename)
    
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read(), True
    else:
        html_content = polite_get(url)
        if html_content:
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            time.sleep(delay)
        return html_content, False

def parse_price(price_text):
    """Clean price string like '£51.77' into float 51.77."""
    if not price_text:
        return 0.0
    # Remove currency symbols (handling potential encoding quirks like Â£ or £)
    cleaned = price_text.replace("£", "").replace("Â", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def scrape_book_details(book_url, source_page_url, index):
    """Visit an individual book page and extract the raw fields."""
    cache_name = f"book-{index}.html"
    html_content, _ = get_or_cache_page(book_url, cache_name)
    
    if not html_content:
        return None

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
    return record

def run_pipeline():
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    current_url = PAGE_1_URL
    all_book_links = []
    
    # 1. Discover catalogue pages & book links
    for page_num in range(1, 4):
        cache_name = f"catalogue-page-{page_num}.html"
        html_content, _ = get_or_cache_page(current_url, cache_name)
        if not html_content:
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

    print(f"Discovered {len(unique_books)} unique book URLs. Processing records...")

    valid_records = []
    error_records = []
    
    # Track canonical URLs for idempotency uniqueness dictionary
    stored_books = {}

    for idx, (book_url, source_url) in enumerate(unique_books, start=1):
        raw_record = scrape_book_details(book_url, source_url, idx)
        if not raw_record:
            continue

        # Normalize price
        price_gbp = parse_price(raw_record["price_text"])
        
        # Build normalized record dictionary matching Pydantic schema
        normalized_data = {
            **raw_record,
            "price_gbp": price_gbp
        }

        # Validate with Pydantic
        try:
            validated_book = BookRecord(**normalized_data)
            # Idempotency check using canonical product_url as unique key
            stored_books[validated_book.product_url] = validated_book.model_dump()
        except ValidationError as e:
            error_records.append({
                "record": raw_record,
                "error": str(e)
            })

    # Convert dictionary values back to list ensuring unique 60 records
    valid_records = list(stored_books.values())

    # Save to output files
    books_file = os.path.join(OUTPUT_DIR, "books.json")
    errors_file = os.path.join(OUTPUT_DIR, "errors.json")

    with open(books_file, "w", encoding="utf-8") as f:
        json.dump(valid_records, f, indent=2, ensure_ascii=False)

    with open(errors_file, "w", encoding="utf-8") as f:
        json.dump(error_records, f, indent=2, ensure_ascii=False)

    print(f"\n--- Stage 4 Summary ---")
    print(f"Valid records stored in {books_file}: {len(valid_records)}")
    print(f"Invalid records stored in {errors_file}: {len(error_records)}")

    return valid_records

if __name__ == "__main__":
    run_pipeline()