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
        response = client.query(IndexId=KENDRA_INDEX_ID, QueryText=query)
        item = next(iter(response.get("ResultItems", [])), None)
        if item:
            title = item.get("DocumentTitle", {}).get("Text", "No Title")
            excerpt = item.get("DocumentExcerpt", {}).get("Text", "No excerpt available.")
            link = item.get("DocumentURI", "#")
            return [{"title": title, "excerpt": excerpt, "link": link}]
        return []
    except (BotoCoreError, ClientError) as e:
        return [{"title": "Error", "excerpt": str(e), "link": "#"}]

def scrape_url(url, mode="partial"):
    try:
        resp = requests.post(
            f"{FLASK_API_URL}/scrape-to-pdf",
            json={"url": url, "mode": mode}
        )
        if resp.ok:
            return resp.json().get("pdf_url")
        else:
            return None
    except Exception:
        return None

st.set_page_config(page_title="Kendra Search", layout="centered")
st.title("🔍 Search Open Cities Data")

mode = st.radio("Choose a mode:", ["Search Data", "Scrape URL"])

scraped_links = [
    "https://denvergov.org/Home",
    "https://denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Community-Planning-and-Development/E-permits",
    "https://www.pcbfl.gov/government/city-council/city-council-meeting-agendas",
    "https://www.oakislandnc.gov/government/clerk/meeting-agendas-minutes-video",
    "https://www.mountainview.gov/whats-happening/events"
]

tooltip_html = "<br>".join(f'<a href="{link}" target="_blank">{link}</a>' for link in scraped_links)

st.markdown("""
    <style>
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
        font-size: 18px;
        margin-left: 8px;
    }

    .tooltip .tooltiptext {
        visibility: hidden;
        width: 500px;
        background-color: #f9f9f9;
        color: #333;
        text-align: left;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0px 0px 8px rgba(0,0,0,0.2);
        position: absolute;
        z-index: 1;
        top: 120%;
        left: 0;
    }

    .tooltip:hover .tooltiptext {
        visibility: visible;
    }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([0.9, 0.1])
with col1:
    user_input = st.text_input("Enter your query or URL", "", placeholder="Type your query or URL...")
with col2:
    st.markdown(f"""
        <div class="tooltip">ℹ️
            <div class="tooltiptext">{tooltip_html}</div>
        </div>
    """, unsafe_allow_html=True)

if mode == "Scrape URL":
    scrape_mode = st.selectbox("Scraping mode", ["partial", "full", "crawl"])

# Action
if st.button("Go"):
    if mode == "Search Data":
        with st.spinner("Searching Data..."):
            result = query_kendra(user_input)
        if result:
            st.markdown(f"{result[0]['excerpt']}")
        else:
            st.info("No results found.")
    else:
        with st.spinner("Scraping and uploading..."):
            pdf_url = scrape_url(user_input, scrape_mode)
        if pdf_url:
            st.success("Scraped and uploaded to S3!")
            st.markdown(f"[📄 View scraped content]({pdf_url})")
        else:
            st.error("Failed to scrape or upload.")
