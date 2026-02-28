import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def extract_url_from_prompt(prompt: str) -> str:
    """Uses regex to find the first URL in the user's plain English prompt."""
    match = re.search(r'(https?://[^\s]+)', prompt)
    return match.group(0) if match else None

def get_clean_dom(url: str) -> str:
    """Navigates to the URL, grabs the HTML, and removes unnecessary bloat."""
    print(f"🕵️‍♂️ Pre-flight: Scraping DOM from {url}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Go to the URL and wait for the network to settle
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            raw_html = page.content()
        except Exception as e:
            print(f"⚠️ Warning: Failed to scrape DOM. LLM will have to guess locators. Error: {e}")
            return "No DOM context available."
        finally:
            browser.close()

    # Use BeautifulSoup to clean the HTML
    soup = BeautifulSoup(raw_html, "html.parser")

    # Destroy tags that the LLM doesn't need for locators
    for tag in soup(["script", "style", "svg", "noscript", "meta", "link", "head"]):
        tag.decompose()

    # Get the cleaned text, strip extra whitespace, and truncate to save LLM context limits
    clean_html = str(soup)
    clean_html = re.sub(r'\n\s*\n', '\n', clean_html) # Remove blank lines
    
    # Return a maximum of 30,000 characters to prevent token overflow
    return clean_html[:30000]