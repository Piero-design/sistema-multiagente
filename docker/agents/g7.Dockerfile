FROM python:3.12-slim
WORKDIR /app
COPY tif-pims-controles/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt python-docx
COPY tif-pims-controles/ .
ENV PORT=5007
EXPOSE 5007
CMD ["python", "app.py"]
