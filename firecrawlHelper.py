import os
import requests
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

load_dotenv()

FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
FIRECRAWL_URL = "https://api.firecrawl.dev/v1/scrape"

# Firecrawl SDK app
app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

def scrape_with_firecrawl(url, only_main_content=True):
    """
    Uses raw HTTP request to Firecrawl API for partial/full scraping.
    """
    try:
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "formats": ["markdown"],
            "onlyMainContent": only_main_content,
            "headers": {},
            "waitFor": 0,
            "mobile": False,
            "skipTlsVerification": False,
            "timeout": 30000,
            "removeBase64Images": True,
            "blockAds": True,
            "proxy": "basic",
        }
        resp = requests.post(FIRECRAWL_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["data"]["markdown"]
    except Exception as e:
        print("[scrape_with_firecrawl] Error:", e)
        return None

def scrape(url):

    try:
        response = app.scrape_url(url=url, params={
            "formats": ["markdown"]
        })
        data = response.json()
        return data["data"]["markdown"]
    except Exception as e:
        print("[scrape] Error:", e)
        return None
