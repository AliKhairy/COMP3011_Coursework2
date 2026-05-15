import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin

class QuoteCrawler:
    """
    A polite web crawler designed to scrape quotes.
    Implements robust error handling, pagination safety, and spider-trap guards.
    """
    def __init__(self, base_url="https://quotes.toscrape.com"):
        self.base_url = base_url
        self.delay = 6.0  # Strict 6-second politeness window
        self.visited = set() # Keeps track of visited URLs to prevent infinite loops

    def crawl(self):
        print(f"Starting crawler at {self.base_url}...")
        all_quotes = []
        url_to_crawl = self.base_url
        
        while url_to_crawl:
            # 1. SPIDER TRAP GUARD: Prevent infinite loops if pages link to each other
            if url_to_crawl in self.visited:
                print(f"Already visited {url_to_crawl}, halting to prevent loop.")
                break
            self.visited.add(url_to_crawl)

            try:
                response = requests.get(url_to_crawl, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Network error crawling {url_to_crawl}: {e}")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            quotes_on_page = soup.find_all('div', class_='quote')

            for q in quotes_on_page:
                # 2. MALFORMED HTML GUARD: Gracefully skip if the text span is missing
                text_el = q.find('span', class_='text')
                if not text_el:
                    continue 
                
                quote_text = text_el.get_text()
                all_quotes.append({
                    "url": url_to_crawl,
                    "text": quote_text
                })

            # 3. SAFE PAGINATION: Check if the button, the anchor, AND the href exist
            next_btn = soup.find('li', class_='next')
            if next_btn and next_btn.find('a') and next_btn.find('a').get('href'):
                next_page = next_btn.find('a')['href']
                url_to_crawl = urljoin(self.base_url, next_page)
                
                print(f"Found next page. Sleeping for {self.delay} seconds...")
                time.sleep(self.delay) 
            else:
                print("Reached the end of the pagination.")
                url_to_crawl = None # Breaks the while loop

        return all_quotes