FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng poppler-utils \
 && rm -rf /var/lib/apt/lists/*
COPY docker/tools/ocr_norma.py /opt/ocr_norma.py
CMD ["python", "/opt/ocr_norma.py"]
