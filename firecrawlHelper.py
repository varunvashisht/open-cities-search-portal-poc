import os

import requests
from dotenv import load_dotenv

from firecrawl import FirecrawlApp

load_dotenv()

app = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))

FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
FIRECRAWL_URL = "https://api.firecrawl.dev/v1/scrape"

def scrape_with_firecrawl(url):
    try:
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
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
        resp = requests.post(FIRECRAWL_URL, json=payload, headers=headers)
        data = resp.json()
        print(data["data"]["markdown"])
        #resp.raise_for_status()
        return data["data"]["markdown"]
    except Exception as e:
        print("error")
        print(e)

def scrape(url):
    try:
        response = app.scrape_url(url=url, params={
	            'formats': [ 'markdown' ],
            })
        print(response.json())
    except Exception as e:
        print("error")
        print(e)