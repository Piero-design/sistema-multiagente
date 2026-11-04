"""Builds a text-layer PDF from the OCR markdown so Group 2's ingestion form (PDF only) can read it."""
from fpdf import FPDF

txt = open("/out/ISO27701-2025.md", encoding="utf-8").read()
pdf = FPDF()
pdf.add_font("dv", fname="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
pdf.set_font("dv", size=9)
pdf.set_auto_page_break(True, 12)
for page in txt.split("<!-- page ")[1:]:
    pdf.add_page()
    head, _, body = page.partition("-->")
    pdf.multi_cell(0, 4.5, f"[page {head.strip()}]\n{body.strip()}")
pdf.output("/out/ISO27701-2025.ocr.pdf")
print("pdf pages:", pdf.page)
