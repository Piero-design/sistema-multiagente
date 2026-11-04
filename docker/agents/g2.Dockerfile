FROM node:22-slim
RUN apt-get update && apt-get install -y --no-install-recommends python3 ca-certificates wget && rm -rf /var/lib/apt/lists/*
RUN npm install -g n8n@2 && npm cache clean --force
WORKDIR /app/g2
COPY ISO-Studio-Auditoria/ .
RUN cd frontend && npm ci --no-audit --no-fund && npm run build
COPY --from=wrap g2_adapt_workflows.py /opt/g2_adapt_workflows.py
COPY --from=wrap g2_ingest.py /opt/g2_ingest.py
COPY --from=wrap g2_entrypoint.sh /opt/g2_entrypoint.sh
RUN chmod +x /opt/g2_entrypoint.sh
EXPOSE 4317
CMD ["/opt/g2_entrypoint.sh"]
