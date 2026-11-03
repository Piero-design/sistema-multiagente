FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e .
# Boundary wrapper (not part of the agent): its MCP server binds 127.0.0.1 by module constant.
COPY --from=wrap g3_run.py /opt/g3_run.py
EXPOSE 8001
CMD ["python", "/opt/g3_run.py"]
