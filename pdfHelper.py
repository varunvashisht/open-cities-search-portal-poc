import os
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import textwrap
from awsHelper import upload_to_s3
import uuid
import pandas as pd
from io import BytesIO


# def generate_pdf(content, filename):
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_auto_page_break(auto=True, margin=15)
#     pdf.set_font("Arial", size=12)
    
#     for line in content.splitlines():
#         pdf.multi_cell(0, 10, line)

#     filepath = f"/tmp/{filename}.pdf"
#     pdf.output(filepath)
#     return filepath

# def wrap_text(text, width=100):
#     lines = []
#     for paragraph in text.splitlines():
#         lines.extend(textwrap.wrap(paragraph, width=width))
#     return lines


def sanitize_html(text):
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    return text

def generate_pdf(content, filename):
    filepath = f"/tmp/{filename}.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(filepath, pagesize=A4)

    story = []
    for paragraph in content.split('\n'):
        paragraph = sanitize_html(paragraph.strip())
        if paragraph:
            try:
                story.append(Paragraph(paragraph, styles["Normal"]))
                story.append(Spacer(1, 12))
            except Exception as e:
                print("Skipping problematic paragraph:", paragraph)
                print("Error:", e)
    
    doc.build(story)
    return filepath


def generate_text_file(content, filename):
    filepath = f"/tmp/{filename}.txt"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


def process_and_upload_scraped_data(markdown_text, url_val, title_val):
    file_id = f"{uuid.uuid4()}___{url_val}"
    pdf_path = generate_pdf(markdown_text, file_id)
    pdf_filename = f"websites_pdf/{file_id}.pdf"
    pdf_s3_url = upload_to_s3(pdf_path, pdf_filename)

    CHUNK_SIZE = 30000
    chunks = [markdown_text[i:i + CHUNK_SIZE] for i in range(0, len(markdown_text), CHUNK_SIZE)]

    data_dict = {f"data_col_{i+1}": [chunk] for i, chunk in enumerate(chunks)}
    data_dict["url"] = [url_val]
    data_dict["title"] = [title_val.strip()]
    df = pd.DataFrame(data_dict)

    buffer = BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)

    parquet_id = file_id.split("___")[0]
    parquet_filename = f"websites_data/{parquet_id}.parquet"
    parquet_s3_url = upload_to_s3(buffer, parquet_filename)

    return {
        "pdf_url": pdf_s3_url,
        "parquet_url": parquet_s3_url,
        "file_id": file_id
    }