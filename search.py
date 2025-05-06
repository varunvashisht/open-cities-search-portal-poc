import streamlit as st
import requests
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import os
from dotenv import load_dotenv

load_dotenv()

KENDRA_INDEX_ID = os.getenv('KENDRA_INDEX_ID')
AWS_REGION = 'us-east-2'
FLASK_API_URL = "http://127.0.0.1:5000"

@st.cache_resource
def get_kendra_client():
    return boto3.client("kendra", region_name=AWS_REGION)

def query_kendra(query):
    client = get_kendra_client()
    try:
        response = client.retrieve(IndexId=KENDRA_INDEX_ID, QueryText=query)
        result_items = response.get("ResultItems", [])
        if not result_items:
            return None

        first_item = result_items[0]
        title = first_item.get("DocumentTitle", "").strip()
        excerpt = first_item.get("Content", "").strip()
        document_uri = first_item.get("DocumentURI", "#")

        filename = document_uri.split("/")[-1] if document_uri else "Unknown"

        scraped_url = "Unknown"
        if "___" in filename:
            parts = filename.rsplit("___", 1)
            if len(parts) == 2:
                scraped_url = parts[1].removesuffix(".pdf")

        return {
            "title": title or "No Title",
            "excerpt": excerpt or "No excerpt available.",
            "source_url": document_uri,
            "filename": filename,
            "scraped_url": scraped_url
        }

    except (BotoCoreError, ClientError) as e:
        return {
            "title": "Error",
            "excerpt": str(e),
            "source_url": "#",
            "filename": "Error",
            "scraped_url": "Error"
        }

def scrape_url(url, mode="partial"):
    try:
        resp = requests.post(
            f"{FLASK_API_URL}/scrape-to-pdf",
            json={"url": url, "mode": mode}
        )
        if resp.ok:
            return resp.json().get("pdf_url")
        return None
    except Exception:
        return None

st.set_page_config(page_title="Kendra Search", layout="centered")
st.title("🔍 Search Open Cities Data")

mode = st.radio("Choose a mode:", ["Search Data", "Scrape URL"])

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
        word-break: break-word;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
    }
    </style>
""", unsafe_allow_html=True)

user_input = st.text_input("Enter your query or URL", "", placeholder="Type your query or URL...")

if mode == "Scrape URL":
    scrape_mode = st.selectbox("Scraping mode", ["partial", "full", "crawl"])

if st.button("Go"):
    if not user_input.strip():
        st.warning("Please enter a query or URL.")
    elif mode == "Search Data":
        with st.spinner("Searching Kendra..."):
            result = query_kendra(user_input)
        if result:
            st.markdown(result['excerpt'])
            original_filename = result['filename']
            id_part = original_filename.split('___')[0] + '.pdf'
            st.markdown(f"**🗂 Source File:** `{id_part}`")

            display_url = result['scraped_url'].replace("_",".")
            st.markdown(f"**🔗 Retrieved From:** {display_url}")
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