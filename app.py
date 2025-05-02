import uuid
from flask import Flask, request, jsonify
import boto3
import os
from dotenv import load_dotenv
import traceback
import pandas as pd
from io import BytesIO
from pandas import json_normalize

from firecrawlHelper import scrape, scrape_with_firecrawl
from pdfHelper import generate_pdf
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
        if mode == "partial":
            markdown, full_response = scrape_with_firecrawl(url, only_main_content=True)
        elif mode == "full":
            markdown, full_response = scrape_with_firecrawl(url, only_main_content=False)
        elif mode == "crawl":
            return jsonify({"error": "Crawl mode not implemented yet"}), 400
        else:
            return jsonify({"error": f"Unknown mode: {mode}"}), 400

        if not markdown or not full_response:
            return jsonify({"error": "Failed to extract content"}), 500

        file_id = str(uuid.uuid4())

        pdf_path = generate_pdf(markdown, file_id)
        pdf_filename = f"{file_id}.pdf"
        pdf_s3_url = upload_to_s3(pdf_path, pdf_filename)

        flat_df = json_normalize(full_response)

        buffer = BytesIO()
        flat_df.to_parquet(buffer, index=False)
        buffer.seek(0)

        parquet_filename = f"scraped_parquets/{file_id}.parquet"
        parquet_s3_url = upload_to_s3(buffer, parquet_filename)

        return jsonify({
            "pdf_url": pdf_s3_url,
            "parquet_url": parquet_s3_url
        })

    except Exception as e:
        print("Exception during /scrape-to-pdf:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)