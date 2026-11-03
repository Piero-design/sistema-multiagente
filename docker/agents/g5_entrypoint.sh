#!/bin/sh
# Integration wrapper for Group 5 (n8n). Does what the group's install guide does by hand, at container start:
# regenerate path-dependent flows for this folder, import/publish them, then start n8n.
set -e
cd /app/g5
[ -f datos/.seeded ] || { cp -a /app/seed/datos/. datos/; touch datos/.seeded; }
[ -f organizaciones/.seeded ] || { cp -a /app/seed/organizaciones/. organizaciones/; touch organizaciones/.seeded; }

# Model: the group's own config file, pointed at the shared gateway (OpenAI-compatible branch).
python3 - <<'PY'
import json, os
p = "datos/config_modelo.json"
c = json.load(open(p, encoding="utf-8"))
c.update({"proveedor": "openai", "url_openai": os.environ["GATEWAY_V1_URL"],
          "modelo": os.environ.get("LLM_MODEL", "gateway"), "api_key": "gateway-managed"})
json.dump(c, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
PY

export N8N_RESTRICT_FILE_ACCESS_TO=/app/g5 GENERIC_TIMEZONE=America/Lima N8N_PORT=5678 \
       N8N_LISTEN_ADDRESS=0.0.0.0 N8N_DIAGNOSTICS_ENABLED=false N8N_PERSONALIZATION_ENABLED=false NODES_EXCLUDE="[]"
python3 n8n/instalar_flujos.py --importar
exec n8n start
