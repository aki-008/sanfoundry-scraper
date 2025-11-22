from typing import Dict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

def pagescrape(url: str) -> Dict[str, str]:
    # 1. Configure the Retry Strategy
    retry_strategy = Retry(
        total=3,                                  # Retry up to 3 times
        backoff_factor=1,                         # Wait 1s, 2s, 4s between retries
        status_forcelist=[429, 500, 502, 503, 504], # Retry on rate limits or server errors
        allowed_methods=["HEAD", "GET", "OPTIONS"]  # Only retry on read operations
    )
    
    # 2. Create a Session and mount the adapter
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    # 3. Add Headers to mimic a browser (Essential for Sanfoundry)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # 4. Use session.get() instead of requests.get()
        res = session.get(url, headers=headers, timeout=10)
        res.raise_for_status() # Check for HTTP errors (like 404)
    except Exception as e:
        print(f"\n[Error] Failed to fetch URL after retries: {e}")
        return {}

    soup = BeautifulSoup(res.content, 'lxml')
    content = soup.find('div', class_='entry-content')

    # Safety check for your AttributeError
    if content is None:
        print(f"\n[Error] Could not find content on {url}. The structure might have changed or access is denied.")
        return {}

    sf_contents = content.findAll('div', class_='sf-section')
    
    # Original filtering logic [cite: 24]
    filtered_sf_content = [
        item for item in sf_contents
        if item.h2 is not None and item.table is not None
    ]
    tables = [item.table for item in filtered_sf_content]
    links = {}
    for table in tables:
        hrefs = {link.text.strip().replace(
            " ", '-'): link["href"] for link in table.findAll('a') if link.has_attr('href')}
        links.update(hrefs)
    
    return links
