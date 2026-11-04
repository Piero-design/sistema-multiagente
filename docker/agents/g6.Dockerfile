FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .
ENV INVENTARIO_DB_PATH=/data/inventario.sqlite3
EXPOSE 8006
CMD ["python", "-m", "uvicorn", "inventario.api:app", "--host", "0.0.0.0", "--port", "8006"]
