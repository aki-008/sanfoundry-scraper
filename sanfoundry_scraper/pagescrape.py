from typing import Dict
import requests
from bs4 import BeautifulSoup


def pagescrape(url: str) -> Dict[str, str]:
    # Add headers to mimic a real browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status() # Check for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return {}

    soup = BeautifulSoup(res.content, 'lxml')
    content = soup.find('div', class_='entry-content')

    # Safety check: If content is not found, return empty dict instead of crashing
    if content is None:
        print(f"Error: Could not find 'entry-content' div. Page content might be blocked or structure changed. (Status: {res.status_code})")
        return {}

    sf_contents = content.findAll('div', class_='sf-section')
    
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
