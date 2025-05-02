import os
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import os
import textwrap


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