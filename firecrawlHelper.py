import os
import requests
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from pprint import pprint
import time


load_dotenv()

FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
FIRECRAWL_URL = "https://api.firecrawl.dev/v1/scrape"
FIRECRAWL_CRAWL_URL = "https://api.firecrawl.dev/v1/crawl"

# Firecrawl SDK app
app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

def scrape_with_firecrawl(url, only_main_content=True):
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
        markdown = data["data"]["markdown"]
        return markdown, data
    except Exception as e:
        print("[scrape_with_firecrawl] Error:", e)
        return None, None


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


def crawl_with_firecrawl(url):
    payload = {
        "url": url,
        "maxDepth": 1,
        "ignoreSitemap": False,
        "ignoreQueryParameters": False,
        "limit": 2,
        "scrapeOptions": {
            "formats": ["markdown"],
            "onlyMainContent": True,
            "headers": {},
            "waitFor": 0,
            "mobile": False,
            "skipTlsVerification": False,
            "timeout": 30000,
            "removeBase64Images": True,
            "blockAds": True,
            "proxy": "basic",
        }
    }

    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(FIRECRAWL_CRAWL_URL, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    crawl_id = data.get("id")

    if not crawl_id:
        print("❌ No crawl ID returned.")
        return

    print("⏳ Polling for crawl completion...")

    for attempt in range(30):  
        time.sleep(10)  
        result_url = f"{FIRECRAWL_CRAWL_URL}/{crawl_id}"
        result_response = requests.get(result_url, headers=headers)
        result_data = result_response.json()

        status = result_data.get("status")
        print(f"Attempt {attempt + 1}: Status = {status}")

        if status == "completed":
            print("\n✅ Crawl completed.")
            return result_data

    print("❌ Timed out waiting for crawl to complete.")
    return None
