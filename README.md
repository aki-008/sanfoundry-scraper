# 📚 sanfoundry-scraper

A **Python library** for efficiently scraping Multiple Choice Questions (MCQs) from Sanfoundry.

It extracts **all MCQs** of a subject that you input the link of. [cite_start]The output is a single, aggregated HTML file, making it easier to "study" offline.

---

## ✨ Features

* [cite_start]**Subject-Level Scraping:** Input the main subject page URL (e.g., for 1000 questions) and the script automatically scrapes all linked quiz pages.
* [cite_start]**Multithreading Support:** Utilizes multithreading to drastically reduce scraping time[cite: 3].
    * *Example Performance:* One test run showed a reduction from ~50 seconds (normal) to **~17 seconds** (with 10 workers) on a 1000-question quiz.
* [cite_start]**HTML Output:** Saves all aggregated content into a single, clean HTML file.
* [cite_start]**MathJax Ready:** Injects MathJax scripts into the output HTML, ensuring mathematical equations and complex symbols render correctly in your browser[cite: 14].
* [cite_start]**Customizable Workers:** Control the number of concurrent threads used for scraping.

---

## 🚀 Quick Start

### 1. Installation

[cite_start]Run the following command to install the required Python libraries (`bs4`, `requests`, `lxml`):

```bash
pip install -r requirements.txt
