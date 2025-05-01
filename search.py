import streamlit as st
import requests
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
KENDRA_INDEX_ID = os.getenv('KENDRA_INDEX_ID')
AWS_REGION = 'us-east-2'
FLASK_API_URL = "http://127.0.0.1:5000"  

@st.cache_resource
def get_kendra_client():
    return boto3.client("kendra", region_name=AWS_REGION)

def query_kendra(query):
    client = get_kendra_client()
    try:
        response = client.query(
            IndexId=KENDRA_INDEX_ID,
            QueryText=query
        )
        results = []
        for item in response.get("ResultItems", []):
            title = item.get("DocumentTitle", {}).get("Text", "No Title")
            excerpt = item.get("DocumentExcerpt", {}).get("Text", "No excerpt available.")
            link = item.get("DocumentURI", "#")
            results.append({"title": title, "excerpt": excerpt, "link": link})
        return results
    except (BotoCoreError, ClientError) as e:
        return [{"title": "Error", "excerpt": str(e), "link": "#"}]

def scrape_url(url):
    try:
        resp = requests.post(f"{FLASK_API_URL}/scrape-to-pdf", json={"url": url})
        if resp.ok:
            return resp.json().get("pdf_url")
        else:
            return None
    except Exception as e:
        return None

# Streamlit UI
st.set_page_config(page_title="Kendra Search", layout="centered")
st.title("🔍 Search Open Cities Data")

mode = st.radio("Choose a mode:", ["Search Data", "Scrape URL"])

user_input = st.text_input("Enter your query or URL", "", placeholder="Type your query or URL...")

if st.button("Go") or user_input:
    if mode == "Search Data":
        with st.spinner("Searching Data..."):
            results = query_kendra(user_input)
        if results:
            for r in results:
                st.markdown(f"{r['excerpt']}")
                st.markdown(f"### Source: [{r['title']}]({r['link']})")
        else:
            st.info("No results found.")
    else:  
        with st.spinner("Scraping and uploading..."):
            pdf_url = scrape_url(user_input)
        if pdf_url:
            st.success("Scraped and uploaded to S3!")
            st.markdown(f"[📄 View scraped content]({pdf_url})")
        else:
            st.error("Failed to scrape or upload.")
