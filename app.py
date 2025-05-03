import uuid
from flask import Flask, request, jsonify
import boto3
import os
from dotenv import load_dotenv
import traceback
import pandas as pd
from io import BytesIO
from pandas import json_normalize
import re
from urllib.parse import urlparse


from firecrawlHelper import scrape, scrape_with_firecrawl, crawl_with_firecrawl
from pdfHelper import process_and_upload_scraped_data
from awsHelper import upload_to_s3

app = Flask(__name__)
load_dotenv()

KENDRA_INDEX_ID = os.getenv('KENDRA_INDEX_ID')
kendra_client = boto3.client('kendra', region_name='us-east-2')


@app.route('/search', methods=['GET'])
def hello():
    return jsonify({"results": "success"})


@app.route('/search', methods=['POST'])
def search_kendra():
    data = request.json
    query_text = data.get('query')

    if not query_text:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    try:
        response = kendra_client.query(
            IndexId=KENDRA_INDEX_ID,
            QueryText=query_text
        )

        results = []
        for item in response.get('ResultItems', []):
            result = {
                "type": item.get('Type'),
                "document_id": item.get('DocumentId'),
                "document_title": item.get('DocumentTitle', {}).get('Text'),
                "document_excerpt": item.get('DocumentExcerpt', {}).get('Text')
            }
            results.append(result)

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/scrape-to-pdf', methods=['POST'])
def scrape_to_pdf():
    data = request.get_json()
    url = data.get("url")
    mode = data.get("mode", "partial")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        if mode in ("partial", "full"):
            only_main = mode == "partial"
            markdown, full_response = scrape_with_firecrawl(url, only_main_content=only_main)
            if not markdown or not full_response:
                return jsonify({"error": "Failed to extract content"}), 500

            markdown_text = full_response.get("data", {}).get("markdown", "")
            original_url = full_response.get("data", {}).get("metadata", {}).get("url", url)
            parsed = urlparse(original_url)
            url_val = parsed.netloc
            title_val = full_response.get("data", {}).get("metadata", {}).get("title", "")
        
        elif mode == "crawl":
            crawl_result = crawl_with_firecrawl(url)
            print("Crawl Result: ", crawl_result)
            if not crawl_result:
                return jsonify({"error": "Crawl failed or timed out"}), 500

            data = crawl_result.get("data", [])
            if not isinstance(data, list) or len(data) == 0:
                return jsonify({"error": "No pages found in crawl"}), 404

            combined_markdown = ""
            for idx, page in enumerate(data):
                page_markdown = page.get("markdown", "")
                page_title = page.get("metadata", {}).get("title", f"Page {idx + 1}")
                combined_markdown += f"\n\n# {page_title}\n\n{page_markdown}"

            markdown_text = combined_markdown
            title_val = data[0].get("metadata", {}).get("title", "")
            parsed = urlparse(url)
            url_val = parsed.netloc


        else:
            return jsonify({"error": f"Unknown mode: {mode}"}), 400

        url_cleaned = re.sub(r'\W+', '_', url_val)[:50] 
        result = process_and_upload_scraped_data(markdown_text, url_cleaned, title_val.strip())

        return jsonify({
            "pdf_url": result["pdf_url"],
            "parquet_url": result["parquet_url"]
        })

    except Exception as e:
        print("Exception during /scrape-to-pdf:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)