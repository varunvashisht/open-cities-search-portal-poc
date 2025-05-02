import os
import re
import boto3
from dotenv import load_dotenv
from firecrawl import FirecrawlApp, ScrapeOptions
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

load_dotenv()

firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")

app = FirecrawlApp(api_key=firecrawl_api_key)

# using the landing page (HOME) and the E-Permits page
urls = ["https://denvergov.org/Home", "https://denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Community-Planning-and-Development/E-permits"]

# Scraping 
markdown_texts = []

for url in urls:
    result = app.scrape_url(url, formats=["markdown"])  
    markdown_texts.append(result.markdown)

# Preprocessing

def preprocess_markdown(markdown):
    markdown = re.sub(r'``````', '', markdown, flags=re.DOTALL)
    markdown = re.sub(r'`[^`]*`', '', markdown)
    markdown = re.sub(r'!\[.*?\]\(.*?\)', '', markdown)
    markdown = re.sub(r'^\|.*\|$', '', markdown, flags=re.MULTILINE)
    markdown = re.sub(r'^\s*[-|]+\s*$', '', markdown, flags=re.MULTILINE)
    markdown = re.sub(r'[#>*_~-]', '', markdown)
    markdown = re.sub(r'\s+', ' ', markdown).strip()
    return markdown

cleaned_texts = [preprocess_markdown(md) for md in markdown_texts]

# Creating PDF and Saving in S3

s3_client = boto3.client('s3')
bucket_name = 'genai-poc-s3-bucket'

def upload_to_s3(file_path, bucket_name, s3_key):
    try:
        s3_client.upload_file(file_path, bucket_name, s3_key)
        print(f"Successfully uploaded {file_path} to {bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Error uploading {file_path} to S3: {e}")
        
styles = getSampleStyleSheet()

for idx, text in enumerate(cleaned_texts):
    pdf_filename = f"webpage_{idx+1}.pdf"
    pdf_path = f"/tmp/{pdf_filename}"  
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    story = []
    for paragraph in text.split('\n'):
        story.append(Paragraph(paragraph, styles["Normal"]))
        story.append(Spacer(1, 12))
    doc.build(story)
    
    s3_key = f"scraped_data/{pdf_filename}"  
    upload_to_s3(pdf_path, bucket_name, s3_key)
    
    os.remove(pdf_path)