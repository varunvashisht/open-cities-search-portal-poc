import streamlit as st
import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = "us-east-2"
BEDROCK_KB_ID = os.getenv("BEDROCK_KNOWLEDGE_BASE_ID")

@st.cache_resource
def get_bedrock_client():
    return boto3.client("bedrock-agent-runtime", region_name=AWS_REGION)

def query_bedrock_knowledge_base(query):
    client = get_bedrock_client()
    try:
        response = client.retrieve_and_generate(
            input={"text": query},
            retrieveAndGenerateConfiguration={
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": BEDROCK_KB_ID,
                    "modelArn": "arn:aws:bedrock:us-east-2:358607849468:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0"
                    # "inferenceConfigurationArn": "arn:aws:bedrock:us-east-2:358607849468:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0"
                },
                "type": "KNOWLEDGE_BASE"
            }
        )
        return response.get("output", {}).get("text", "No response.")
    except (BotoCoreError, ClientError) as e:
        return f"Error: {str(e)}"

# ----------------- Streamlit UI -----------------

st.set_page_config(page_title="AI KB Search", layout="centered")
st.title("🧠 Ask AI")

query = st.text_input("Ask a question", "", placeholder="e.g., When is the next meeting?")

if st.button("Submit") or query:
    with st.spinner("Querying Knowledge Base..."):
        answer = query_bedrock_knowledge_base(query)
    st.markdown(answer)
