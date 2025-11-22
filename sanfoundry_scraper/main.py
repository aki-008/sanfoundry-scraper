# FILE: sanfoundry_scraper/main.py
import sys
import time
from argparse import ArgumentParser
from typing import List, Optional, Dict
from concurrent.futures import ThreadPoolExecutor

# RELATIVE IMPORTS (Crucial for running as a package)
from .pagescrape import pagescrape
from .mcqscrape import mcqscrape_json, write_to_json

# CLI Helper
parser = ArgumentParser(description="A CLI Tool for scraping quizzes from SANFOUNDRY", usage="\n python main.py --url https://... ")
parser.add_argument("--url", help="URL of quiz", type=str, default=None, dest="url")
parser.add_argument("--thread", action="store_true", help="Uses Multithreading for scraping")
parser.add_argument("--workers", type=int, help="Maximum number of threads", default=5)

# Parse args safely
try:
    args = parser.parse_args()
except:
    args = None

# Global list to store JSON objects
QUIZ_LIST: List[Dict] = []

def writer(url: str) -> None:
    """Scrapes a single page and appends the JSON dicts to the global list."""
    # Uses the JSON function from mcqscrape.py
    res: List[Dict] = mcqscrape_json(url)
    QUIZ_LIST.extend(res)

def async_main(url: str) -> None:
    """Manages the multithreaded scraping process."""
    print("\nStarting multithreaded JSON data extraction...")
    
    # Get all chapter links from the main subject page
    pages_dict = pagescrape(url)
    
    # Extract just the URLs from the dictionary
    pages: List[str] = [v for _, v in pages_dict.items()]
    
    if not pages:
        print("Error: No quiz pages found or connection failed. Check URL.")
        return

    # Determine worker count
    workers = args.workers if args and args.workers else 5

    # Run the writer function in parallel
    with ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(writer, pages)

    # Write the accumulated data to JSON
    FINAL_JSON_LIST = QUIZ_LIST
    if FINAL_JSON_LIST:
        # Extract the subject name from URL for the filename
        subject_name = url.strip('/').split('/')[-1]
        write_to_json(FINAL_JSON_LIST, subject_name)
    else:
        print("Warning: No MCQs were extracted successfully.")

def scraper():
    # Handle arguments or input prompt
    if args and args.url:
        PAGE_URL = args.url
    else:
        command = "Enter the URL of the Subject Page: "
        PAGE_URL = input(command)

    if not PAGE_URL:
        print("Please enter a valid URL.")
        sys.exit()

    async_main(PAGE_URL)

if __name__ == "__main__":
    scraper()