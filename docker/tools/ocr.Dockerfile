FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng poppler-utils fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir fpdf2
COPY docker/tools/ocr_norma.py docker/tools/md_to_pdf.py /opt/
CMD ["python", "/opt/ocr_norma.py"]
