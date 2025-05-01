import os
import re
from fpdf import FPDF
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

def wrap_text(text, width=100):
    lines = []
    for paragraph in text.splitlines():
        lines.extend(textwrap.wrap(paragraph, width=width))
    return lines


def generate_pdf(content, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(left=10, top=15, right=10)

    # Use a Unicode-safe font
    font_path = "DejaVuSans.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError("DejaVuSans.ttf not found. Update the font path or install it.")

    pdf.add_font("DejaVu", "", font_path, uni=True)
    pdf.set_font("DejaVu", "", 10)

    def safe_wrap(line, max_chars=80):
        # Break long lines safely at character level
        return [line[i:i+max_chars] for i in range(0, len(line), max_chars)]

    for paragraph in content.splitlines():
        paragraph = paragraph.strip()
        if not paragraph:
            pdf.ln(5)
            continue
        for wrapped_line in safe_wrap(paragraph):
            try:
                pdf.multi_cell(0, 10, wrapped_line)
            except Exception as e:
                # Replace non-renderable characters
                cleaned = ''.join(c if c.isprintable() else '?' for c in wrapped_line)
                pdf.multi_cell(0, 10, cleaned)

    filepath = f"/tmp/{filename}.pdf"
    pdf.output(filepath)
    return filepath

def generate_text_file(content, filename):
    filepath = f"/tmp/{filename}.txt"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath