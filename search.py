import streamlit as st
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Configuration
KENDRA_INDEX_ID = 'ddb9f433-6cbd-405e-a821-01a91c5b5d23'  # Replace with your Kendra Index ID
AWS_REGION = 'ap-south-1'  # e.g., 'us-east-1'

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

# Streamlit UI
st.set_page_config(page_title="Kendra Search", layout="centered")
st.title("🔍 Search with Amazon Kendra")

# Search bar
query = st.text_input("Enter your query", "", placeholder="Type something and press Enter...")

if st.button("Search") or query:
    with st.spinner("Searching..."):
        results = query_kendra(query)

    if results:
        for r in results:
            st.markdown(f"{r['excerpt']}")
            st.markdown(f"### Source: [{r['title']}]({r['link']})")
            #st.markdown("---")
    else:
        st.info("No results found.")
