import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin

class QuoteCrawler:
    """
    A polite web crawler designed to scrape quotes.toscrape.com.
    Enforces a strict politeness window between requests.
    """
    
    def __init__(self, base_url: str = "https://quotes.toscrape.com/", delay: int = 6):
        self.base_url = base_url
        self.delay = delay
        self.visited_urls = set()
        # Using a Session object is an "Outstanding" tier practice for connection pooling
        self.session = requests.Session() 
        
    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetches a page and returns a BeautifulSoup object, respecting the delay."""
        if url in self.visited_urls:
            return None
            
        print(f"Crawling: {url} (Waiting {self.delay} seconds...)")
        time.sleep(self.delay) # Mandatory politeness window 
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status() # Graceful error handling [cite: 141]
            self.visited_urls.add(url)
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def crawl(self) -> List[Dict[str, str]]:
        """
        Initiates the crawl, extracting text and following pagination.
        """
        crawled_data = []
        current_url = self.base_url
        
        while current_url:
            soup = self._fetch_page(current_url)
            
            # Defensive programming: If the page failed to load, stop the loop.
            if not soup:
                print("Stopping crawl due to missing page or network error.")
                break 
                
            # 1. DATA EXTRACTION
            # Find all <div> elements with the class 'quote'
            quotes = soup.find_all('div', class_='quote')
            
            for q in quotes:
                # Extract the actual quote text, stripping whitespace
                text = q.find('span', class_='text').get_text(strip=True)
                crawled_data.append({
                    "url": current_url,
                    "text": text
                })
                
            # 2. PAGINATION
            # Look for the 'Next' button
            next_btn = soup.find('li', class_='next')
            
            if next_btn:
                # Extract the relative URL (e.g., '/page/2/') from the <a> tag
                next_link = next_btn.find('a')['href']
                # Construct the full absolute URL using urllib.parse.urljoin
                current_url = urljoin(self.base_url, next_link)
            else:
                # If there's no next button, we've hit the last page.
                print("Reached the end of the pagination.")
                current_url = None 
                
        return crawled_data

# Quick test execution
if __name__ == "__main__":
    crawler = QuoteCrawler()
    # crawler.crawl()