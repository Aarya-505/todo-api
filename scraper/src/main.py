import os
import requests

# Constants
URL = "https://books.toscrape.com/catalogue/page-1.html"
CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "catalogue-page-1.html")

# Polite User-Agent identifying yourself and your repo
USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/Aarya-505/todo-api)"
HEADERS = {"User-Agent": USER_AGENT}

def fetch_catalogue_page_1():
    # Ensure cache directory exists
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # Check if already cached
    if os.path.exists(CACHE_FILE):
        print(f"CACHE HIT: Loading from {CACHE_FILE}")
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"Response size: {len(content)} bytes")
        return content

    # If not cached, fetch from web politely
    print(f"FETCH: Requesting {URL}")
    try:
        # Set a timeout of 5 seconds
        response = requests.get(URL, headers=HEADERS, timeout=5)
        
        # Check if status code is 200 OK
        if response.status_code != 200:
            print(f"Failed to fetch page. Status code: {response.status_code}")
            return None
        
        content = response.text
        
        # Save to cache
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"Successfully cached! Response size: {len(content)} bytes")
        return content

    except requests.exceptions.RequestException as e:
        print(f"Request failed due to an error: {e}")
        return None

if __name__ == "__main__":
    fetch_catalogue_page_1()