import bs4
from .pagescrape import pagescrape
import os
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- Helper: Robust Session Creator ---
def get_session():
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.google.com/'
    })
    return session

def write_to_html(data: BeautifulSoup, filename):
    if not os.path.exists("Saved_MCQs"):
        os.mkdir("Saved_MCQs")
    
    # --- FIX: Safety Check for Empty/Blocked Content ---
    if data is None or data.body is None:
        print(f"Warning: No content to write for {filename}. (Likely blocked or empty)")
        return

    head = BeautifulSoup("""
    <head>
    <script>
      MathJax = {
        tex: {
          inlineMath: [['$', '$'], ['\\(', '\\)']]
        }
      };
    </script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">
    </script>
    </head>""", "lxml")
    
    data.body.insert_before(head)
   
    with open(f"./Saved_MCQs/{filename}.html", "w+", encoding="utf-8") as file:
        file.write(str(data.prettify()))


def mcqscrape_json(url: str):
    session = get_session()
    mcqs = []
    try:
        res = session.get(url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(res.content, 'lxml')
    content = soup.find('div', 'entry-content')
    if not content: return []

    paras = content.findAll('p')
    if not paras: return []
    
    header = paras[0].text
    print(header)
    
    try:
        for each in paras[1:-3]:
            if not each.span: continue # Skip if structure is unexpected
            answerid = each.span['id']
            answer_div = content.find('div', id='target-'+answerid)
            
            each.span.decompose()
            question = each.text.split("\n")[0].split(".", 1)[-1].strip()
            options = [option.split(')', 1)[-1].strip()
                       for option in each.text.split('\n')[1:] if option != '']
            
            answer = answer_div.text.split('\n', 1)[0].strip('Answer: ')
            explanation = answer_div.text.split('\n', 1)[1].strip()
            
            question_dict = {
                "question": question,
                "options": options,
                "answer": answer,
                "explanation": explanation
            }
            mcqs.append(question_dict)
    except Exception as err:
        print("Error parsing question:", err)
    return mcqs


def mcqscrape_html(url: str) -> str:
    # Recursive case for subject pages (URLs containing '1000')
    if '1000' in url:
        pages = pagescrape(url)
        mega_html = ''
        if not pages:
            print("No pages found (Block or Error).")
            return ''
            
        for k, v in pages.items():
            print("getting", k, "from ->", v, end=' ... ')
            mega_html += mcqscrape_html(v)
            print("Done!")
            
        # Avoid writing empty files
        if mega_html:
            write_to_html(BeautifulSoup(mega_html, 'lxml'), url.split('/')[-2])
        return ''

    # Base case: Scrape individual MCQ page
    session = get_session()
    try:
        res = session.get(url, timeout=10)
        if res.status_code == 403:
            print(f"\n[BLOCKED 403] {url}")
            return ''
        res.raise_for_status()
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ''

    soup = BeautifulSoup(res.content, 'lxml')
    content = soup.find('div', class_='entry-content')
    
    if content is None:
        return ''

    # Clean up the HTML
    paras = content.findAll('p')
    classes_to_remove = ["sf-mobile-ads", "desktop-content", "mobile-content", "sf-nav-bottom"]
    tags_to_remove = ["script"]
    
    for sp in content.findAll('span', class_="collapseomatic"): sp.decompose()
    for cls in classes_to_remove:
        for sp in content.findAll('div', class_=cls): sp.decompose()
    for tag in tags_to_remove:
        for sp in content.findAll(tag): sp.decompose()
    
    if len(paras) > 3:
        for tag in paras[-3:]: tag.decompose()
        
    for tag in content.find_all("div"):
        if tag.text == "advertisement": tag.extract()

    # Attribute cleanup
    for tag in content.findAll(True):
        tag.attrs.pop("class", "")
        tag.attrs.pop("id", "")
        
    return content.prettify()
