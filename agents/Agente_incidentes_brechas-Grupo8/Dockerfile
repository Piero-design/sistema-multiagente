# Interfaz web + agente de incidentes y brechas, con Claude Code dentro del contenedor.
# 1) Compila la interfaz React
FROM node:22-slim AS ui
WORKDIR /ui
COPY web/client/package.json web/client/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY web/client/ ./
RUN npm run build

# 2) Imagen final: servidor Node sin dependencias + Claude Code
FROM node:22-slim
RUN npm install -g @anthropic-ai/claude-code && npm cache clean --force
WORKDIR /app
COPY .claude ./.claude
COPY knowledge ./knowledge
COPY examples ./examples
COPY demo ./demo
COPY archivos-demo ./archivos-demo
COPY web/server.js ./web/server.js
COPY web/autonomia ./web/autonomia
COPY config ./config
COPY package.json package-lock.json ./
RUN npm install --omit=dev && npm cache clean --force
COPY --from=ui /ui/dist ./web/client/dist
RUN mkdir -p salidas contextos buzon .ib-data /home/node/.claude \
 && chown -R node:node /app /home/node/.claude
USER node
ENV HOST=0.0.0.0 PORT=3100 NODE_ENV=production
EXPOSE 3100
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s CMD node -e "fetch('http://127.0.0.1:'+process.env.PORT+'/api/config').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
CMD ["node", "web/server.js"]
