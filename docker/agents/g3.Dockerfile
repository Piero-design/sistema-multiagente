FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -e .
# Boundary wrapper (not part of the agent): its MCP server binds 127.0.0.1 by module constant.
COPY --from=wrap g3_run.py /opt/g3_run.py
COPY --from=wrap g3_human.py /opt/g3_human.py
COPY --from=wrap g3_start.sh /opt/g3_start.sh
RUN chmod +x /opt/g3_start.sh
EXPOSE 8001
CMD ["/opt/g3_start.sh"]
