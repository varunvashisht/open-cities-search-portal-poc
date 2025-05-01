import streamlit as st
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import os

# Configuration
KENDRA_INDEX_ID = os.getenv('KENDRA_INDEX_ID') 
AWS_REGION = 'us-east-2'  # e.g., 'us-east-1'

# Initialize Kendra client
@st.cache_resource
def get_kendra_client():
    return boto3.client('kendra', region_name=AWS_REGION)

def query_kendra(question):
    client = get_kendra_client()
    try:
        response = client.query(
            IndexId=KENDRA_INDEX_ID,
            QueryText=question
        )
        results = []
        for result in response.get("ResultItems", []):
            if "DocumentExcerpt" in result:
                excerpt = result["DocumentExcerpt"]["Text"]
                results.append(excerpt)
        return results if results else ["No relevant results found."]
    except (BotoCoreError, ClientError) as e:
        return [f"Error querying Kendra: {str(e)}"]

# UI setup
st.title("💬 Chat with Amazon Kendra")
st.markdown("Ask a question and get answers powered by Amazon Kendra.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_input = st.chat_input("Ask your question...")
if user_input:
    st.session_state.chat_history.append(("user", user_input))
    with st.spinner("Searching Kendra..."):
        kendra_responses = query_kendra(user_input)
    st.session_state.chat_history.append(("kendra", kendra_responses))

# Display chat history
for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        if isinstance(msg, list):
            for line in msg:
                st.markdown(line)
        else:
            st.markdown(msg)
