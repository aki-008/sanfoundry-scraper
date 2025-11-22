# In sanfoundry_scraper/main.py

# ... existing imports ...
from .pagescrape import pagescrape
from .mcqscrape import mcqscrape_json, write_to_json # MODIFIED IMPORT
from .mcqscrape import mcqscrape_html, write_to_html # Keep existing for compatibility
from bs4 import BeautifulSoup

# ... existing argparse setup ...

QUIZ_LIST: List[Dict] = [] # CHANGE: List of Dictionaries for JSON output

def main(url: str): # This function is still geared toward HTML and should be deprecated or skipped
    print("Use the JSON-specific functions.")
    sys.exit()

# These both functions are for multithreading (modifying for JSON)
def writer(url: str) -> None:
    # This now calls the JSON scraping function
    res: List[Dict] = mcqscrape_json(url)
    QUIZ_LIST.extend(res) # Extend with list of dicts

def async_main(url: str) -> None:
    pages: List[str] = [ v for _ , v in pagescrape(url).items()]
    
    # Check if pages found
    if not pages:
        print("Error: Could not retrieve quiz pages. Check URL and connectivity.")
        return

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        # This will run writer function in multithread with each quiz url
        executor.map(writer , pages)

    # Output is now a List of Dictionaries, not HTML string
    FINAL_JSON_LIST = QUIZ_LIST
    
    # Call the new JSON writer function
    write_to_json(FINAL_JSON_LIST, url.split('/')[-2])


def scraper():
    command = "Enter the URL of the Page where you see links of all Subject related MCQs: "
    PAGE_URL = args.url or input(command)

    # Always use the async/multithread logic now, which supports JSON aggregation
    async_main(PAGE_URL)

if __name__ == "__main__":
    scraper()
