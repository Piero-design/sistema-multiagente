"""Deploy-time adapter for Group 2. Reads the group's ORIGINAL workflow JSONs (never edited) and writes
adapted copies where Gemini nodes are swapped for OpenAI-compatible nodes pointed at the shared gateway.
Preserved: node names, connections, prompts, tools, memory settings, skill sub-workflows.
Usage: g2_adapt_workflows.py <src_dir> <out_dir>   (env: GATEWAY_V1_URL, LLM_MODEL, LLM_EMBED_MODEL)"""
import json
import os
import sys

src, out = sys.argv[1], sys.argv[2]
URL = os.environ["GATEWAY_V1_URL"]
MODEL = os.environ.get("LLM_MODEL", "gateway")
EMBED = os.environ.get("LLM_EMBED_MODEL", "gateway-embed")
CRED_LLM = {"openAiApi": {"id": "GwLlmCred0000001", "name": "Shared LLM gateway"}}
CRED_QDRANT = {"qdrantApi": {"id": "QdrantCred000001", "name": "Qdrant (internal)"}}
swaps = []

for fn in sorted(os.listdir(src)):
    if not fn.endswith(".json"):
        continue
    wf = json.load(open(os.path.join(src, fn), encoding="utf-8"))
    for n in wf["nodes"]:
        t = n["type"].split(".")[-1]
        if t == "lmChatGoogleGemini":
            old = n["parameters"].get("modelName")
            temp = (n["parameters"].get("options") or {}).get("temperature", 0.2)
            n["type"], n["typeVersion"] = "@n8n/n8n-nodes-langchain.lmChatOpenAi", 1.2
            n["parameters"] = {"model": {"__rl": True, "value": MODEL, "mode": "id"},
                               "options": {"temperature": temp, "baseURL": URL}}
            n["credentials"] = CRED_LLM
            swaps.append(f"{fn}: '{n['name']}' lmChatGoogleGemini({old}) -> lmChatOpenAi({MODEL})")
        elif t == "embeddingsGoogleGemini":
            n["type"], n["typeVersion"] = "@n8n/n8n-nodes-langchain.embeddingsOpenAi", 1.2
            n["parameters"] = {"model": EMBED, "options": {"baseURL": URL}}
            n["credentials"] = CRED_LLM
            swaps.append(f"{fn}: '{n['name']}' embeddingsGoogleGemini -> embeddingsOpenAi({EMBED})")
        elif t == "vectorStoreQdrant":
            n["credentials"] = CRED_QDRANT
            swaps.append(f"{fn}: '{n['name']}' qdrant credential bound to internal Qdrant")
    json.dump(wf, open(os.path.join(out, fn), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("\n".join(swaps))
