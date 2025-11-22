import sys
import time
from argparse import ArgumentParser
from typing import List ,Optional, Dict # Added Dict for type hinting
from concurrent.futures import ThreadPoolExecutor

from .pagescrape import pagescrape
# Importing the JSON-focused scraping and writing functions
from .mcqscrape import mcqscrape_json, write_to_json 
from .mcqscrape import mcqscrape_html, write_to_html 
from bs4 import BeautifulSoup

# We are keeping the multithreading arguments based on the original structure (source: 3, 4)
mul_threading: Optional[bool] = sys.argv[1:]

# added a little cli helper
parser = ArgumentParser(description="A CLI Tool for scrapping quizs from SANFOUNDARY" , usage="\n python main.py --thread --workers 15", epilog="Batmobile lost the wheel lol")
parser.add_argument("--url" , help="URL of quiz" , type=str , default=None , dest="url")
parser.add_argument("--thread" , action="store_true" , help="Uses Multithreading for scrapping")
parser.add_argument("--workers" , type=int , help="Maximum number of threads[ More number More speed but More Unstability]" , default=5)
args = parser.parse_args()

# The global list now stores dictionaries (JSON objects) gathered from all threads.
QUIZ_LIST: List[Dict] = []

# --- Deprecated/Placeholder main function ---
# This is kept only to satisfy original code structure but is not used in the JSON path.
def main(url: str):
    MEGA_HTML: str = ''
    if url == '':
        print("Please Enter a URL!") # cite: 10
        sys.exit()
    pages = pagescrape(url)
    for k, v in pages.items():
        print("getting", k, "from ->", v, end=' ... ')
        MEGA_HTML += mcqscrape_html(v)
        print("Done!")
    write_to_html(BeautifulSoup(MEGA_HTML, 'lxml'),
                  url.split('/')[-2])

# --- Multithreading Functions (Modified for JSON) ---
def writer(url: str) -> None:
    # Use the robust JSON scraper for individual pages
    res: List[Dict] = mcqscrape_json(url)
    # Append the list of dictionaries from this page to the global list
    QUIZ_LIST.extend(res) # cite: 11 (original structure extended HTML, now extending JSON dicts)

def async_main(url: str) -> None:
    print("\nStarting multithreaded JSON data extraction...")
    pages: List[str] = [ v for _ , v in pagescrape(url).items()]
    
    if not pages:
        print("Error: No quiz pages found or connection failed.")
        return

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        # This runs the writer function in multiple threads for each quiz URL
        executor.map(writer , pages)

    # The final output is the accumulated list of question dictionaries
    FINAL_JSON_LIST = QUIZ_LIST
    
    # Write the complete list of dictionaries to a JSON file
    if FINAL_JSON_LIST:
        write_to_json(FINAL_JSON_LIST, url.split('/')[-2])
    else:
        print("Warning: No MCQs were extracted successfully.")


def scraper():
    command = "Enter the URL of the Page where you see links of all Subject related MCQs: " # cite: 12
    PAGE_URL = args.url or input(command)

    # We enforce multithreading here, as it's the only path with full robustness/JSON logic
    async_main(PAGE_URL)

if __name__ == "__main__":
    scraper()
