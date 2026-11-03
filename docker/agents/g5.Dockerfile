FROM node:22-slim
RUN apt-get update && apt-get install -y --no-install-recommends python3 ca-certificates && rm -rf /var/lib/apt/lists/*
RUN npm install -g n8n@2 && npm cache clean --force
WORKDIR /app/g5
COPY . .
# runtime data (datos/, organizaciones/) lives in volumes; seeds are kept to initialise them once
RUN mkdir -p /app/seed && cp -a datos /app/seed/datos && cp -a organizaciones /app/seed/organizaciones
COPY --from=wrap g5_entrypoint.sh /opt/g5_entrypoint.sh
RUN chmod +x /opt/g5_entrypoint.sh
EXPOSE 5678
CMD ["/opt/g5_entrypoint.sh"]
