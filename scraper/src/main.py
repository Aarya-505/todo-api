import os
import time
from datetime import datetime, timezone
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# Constants
BASE_URL = "https://books.toscrape.com/catalogue/"
PAGE_1_URL = urljoin(BASE_URL, "page-1.html")
CACHE_DIR = "cache"

# Polite User-Agent
USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/Aarya-505/todo-api)"
HEADERS = {"User-Agent": USER_AGENT}

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
            return f.read(), True  # True means cache hit
    else:
        html_content = polite_get(url)
        if html_content:
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            time.sleep(delay)  # Be polite between live requests
        return html_content, False

def scrape_book_details(book_url, source_page_url, index):
    """Visit an individual book page and extract the 8 raw fields."""
    # Create a safe cache filename for each book
    cache_name = f"book-{index}.html"
    html_content, cached = get_or_cache_page(book_url, cache_name)
    
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, "html.parser")
    
    # 1. Title
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else None

    # 3. Price text
    price_tag = soup.find("p", class_="price_color")
    price_text = price_tag.get_text(strip=True) if price_tag else None

    # 4. Availability text
    avail_tag = soup.find("p", class_="availability")
    availability_text = avail_tag.get_text(strip=True) if avail_tag else None

    # 5. Rating text (extracted from class name like "star-rating Three")
    rating_text = None
    star_tag = soup.find("p", class_="star-rating")
    if star_tag and star_tag.has_attr("class"):
        classes = star_tag["class"]
        # classes usually looks like ['star-rating', 'Three']
        if len(classes) > 1:
            rating_text = classes[1]

    # 6. Description (Books to Scrape puts description in a <p> right before product table, or following #product_description div)
    description = None
    desc_header = soup.find("div", id="product_description")
    if desc_header:
        desc_p = desc_header.find_next_sibling("p")
        if desc_p:
            description = desc_p.get_text(strip=True)
    else:
        # Fallback search if layout varies
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.has_attr("content"):
            description = meta_desc["content"].strip()

    # Construct the raw record with all 8 keys
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
    
    current_url = PAGE_1_URL
    all_book_links = [] # Stores tuples of (book_url, source_page_url)
    
    # Step A: Discover 3 catalogue pages & 60 book links
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
        
        # Find next page link
        next_tag = soup.find("li", class_="next")
        if next_tag and next_tag.find("a"):
            current_url = urljoin(current_url, next_tag.find("a")["href"])
        else:
            break

    # Remove duplicates based on book URL
    seen = set()
    unique_books = []
    for book_url, source_url in all_book_links:
        if book_url not in seen:
            seen.add(book_url)
            unique_books.append((book_url, source_url))

    print(f"Discovered {len(unique_books)} unique book URLs. Fetching details...")

    # Step B: Visit each book detail page
    raw_records = []
    for idx, (book_url, source_url) in enumerate(unique_books, start=1):
        record = scrape_book_details(book_url, source_url, idx)
        if record:
            raw_records.append(record)

    print(f"\n--- Stage 3 Summary ---")
    print(f"detail_pages={len(raw_records)}")
    
    if raw_records:
        print("\nSample Raw Record:")
        import json
        print(json.dumps(raw_records[0], indent=2))

    return raw_records

if __name__ == "__main__":
    run_pipeline()