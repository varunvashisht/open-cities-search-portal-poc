# app.py
import uuid
from flask import Flask, request, jsonify
import boto3
import os

from firecrawlHelper import scrape, scrape_with_firecrawl
from pdfHelper import generate_text_file
from awsHelper import upload_to_s3

app = Flask(__name__)

# AWS Kendra Setup
KENDRA_INDEX_ID = "ddb9f433-6cbd-405e-a821-01a91c5b5d23"      #os.getenv('KENDRA_INDEX_ID')  # Set in environment variables
kendra_client = boto3.client('kendra', region_name='ap-south-1')  # Change region if needed


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
        
        # Extracting some useful fields
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
    
    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # Scrape the site
        content = scrape_with_firecrawl(url)
        if not content:
            return jsonify({"error": "Failed to extract content"}), 500

        # Create PDF
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.txt"
        text_path = generate_text_file(content, file_id)

        # Upload to S3
        s3_url = upload_to_s3(text_path, filename)

        return jsonify({"pdf_url": s3_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
