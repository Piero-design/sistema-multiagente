#!/bin/sh
# Integration wrapper for Group 2: automates the manual setup (import workflows, credentials, publish,
# discover the Chat Trigger URL) and starts Express (serving the built React app) next to n8n.
set -e
APP=/app/g2
FLOWS=/tmp/flows; mkdir -p $FLOWS
python3 /opt/g2_adapt_workflows.py $APP/n8n/workflows $FLOWS | tee /tmp/swaps.log

cat > /tmp/creds.json <<JSON
[{"id":"GwLlmCred0000001","name":"Shared LLM gateway","type":"openAiApi","data":{"apiKey":"gateway-managed","url":"$GATEWAY_V1_URL"}},
 {"id":"QdrantCred000001","name":"Qdrant (internal)","type":"qdrantApi","data":{"qdrantUrl":"http://qdrant:6333","apiKey":"$QDRANT_API_KEY"}}]
JSON
export N8N_DIAGNOSTICS_ENABLED=false N8N_PERSONALIZATION_ENABLED=false GENERIC_TIMEZONE=America/Lima N8N_PORT=5678
n8n import:credentials --input=/tmp/creds.json
n8n import:workflow --separate --input=$FLOWS
for id in $(python3 -c "import json,glob;print(' '.join(json.load(open(f,encoding='utf-8'))['id'] for f in glob.glob('$FLOWS/*.json')))"); do
  n8n publish:workflow --id=$id || echo "publish skipped for $id"
done

n8n start &
for i in $(seq 1 60); do wget -qO- http://127.0.0.1:5678/healthz >/dev/null 2>&1 && break; sleep 2; done

CHAT_ID=$(python3 -c "import json;d=json.load(open('$FLOWS/Agente_Evaluacion_Riesgos.json',encoding='utf-8'));print([n['webhookId'] for n in d['nodes'] if 'chatTrigger' in n['type']][0])")
export N8N_CHAT_URL="http://127.0.0.1:5678/webhook/$CHAT_ID/chat" PORT=4317 NODE_ENV=production
cd $APP/frontend
exec node server/index.js
