import os
import time
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

def scrape_catalogue_pages():
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    current_url = PAGE_1_URL
    catalogue_pages_count = 0
    all_book_urls = []
    
    # We want exactly the first 3 catalogue pages
    for page_num in range(1, 4):
        cache_file = os.path.join(CACHE_DIR, f"catalogue-page-{page_num}.html")
        
        # Check cache first
        if os.path.exists(cache_file):
            print(f"CACHE HIT: Loading page {page_num} from cache")
            with open(cache_file, "r", encoding="utf-8") as f:
                html_content = f.read()
        else:
            print(f"FETCH: Requesting page {page_num} from {current_url}")
            html_content = polite_get(current_url)
            if not html_content:
                break
            
            # Save to cache
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            # Be polite: wait at least 500ms between real live requests
            time.sleep(0.5)

        catalogue_pages_count += 1
        
        # Parse HTML with Beautiful Soup
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Extract book links from the page
        # Books to Scrape product links are inside <article class="product_pod"> -> <h3> -> <a>
        product_pods = soup.find_all("article", class_="product_pod")
        for pod in product_pods:
            a_tag = pod.find("h3").find("a")
            if a_tag and a_tag.has_attr("href"):
                relative_url = a_tag["href"]
                # Safely turn relative URL into absolute URL using urljoin
                absolute_url = urljoin(current_url, relative_url)
                all_book_urls.append(absolute_url)
        
        # Find the 'next' link for the subsequent iteration
        next_tag = soup.find("li", class_="next")
        if next_tag and next_tag.find("a"):
            next_href = next_tag.find("a")["href"]
            current_url = urljoin(current_url, next_href)
        else:
            break

    # Remove duplicates
    unique_urls = list(set(all_book_urls))
    
    print(f"\n--- Summary ---")
    print(f"catalogue_pages={catalogue_pages_count}")
    print(f"discovered={len(all_book_urls)}")
    print(f"unique_urls={len(unique_urls)}")
    
    return unique_urls

if __name__ == "__main__":
    scrape_catalogue_pages()