"""Deploy-time adapter for Group 2. Reads the group's ORIGINAL workflow JSONs (never edited) and writes
adapted copies where Gemini nodes are swapped for OpenAI-compatible nodes pointed at the shared gateway.
Preserved: node names, connections, prompts, tools, memory settings, skill sub-workflows.
Usage: g2_adapt_workflows.py <src_dir> <out_dir>   (env: GATEWAY_V1_URL, LLM_MODEL, LLM_EMBED_MODEL)"""
import hashlib
import json
import os
import sys
import uuid

src, out = sys.argv[1], sys.argv[2]
URL = os.environ["GATEWAY_V1_URL"]
MODEL = os.environ.get("LLM_MODEL", "gateway")
EMBED = os.environ.get("LLM_EMBED_MODEL", "gateway-embed")
CRED_LLM = {"openAiApi": {"id": "GwLlmCred0000001", "name": "Shared LLM gateway"}}
CRED_QDRANT = {"qdrantApi": {"id": "QdrantCred000001", "name": "Qdrant (internal)"}}
swaps = []

# Stable ids so the skill sub-workflows can be re-linked (templates ship without ids).
loaded = {}
for fn in sorted(os.listdir(src)):
    if fn.endswith(".json"):
        wf = json.load(open(os.path.join(src, fn), encoding="utf-8"))
        if not wf.get("id"):
            wf["id"] = "G2" + hashlib.sha1(wf["name"].encode()).hexdigest()[:14]
            swaps.append(f"{fn}: assigned workflow id {wf['id']}")
        loaded[fn] = wf
ids_by_name = {w["name"]: w["id"] for w in loaded.values()}

for fn, wf in loaded.items():
    for n in wf["nodes"]:
        ref = (n.get("parameters") or {}).get("workflowId")
        if isinstance(ref, dict) and ref.get("cachedResultName") in ids_by_name:
            new = ids_by_name[ref["cachedResultName"]]
            if ref.get("value") != new:
                swaps.append(f"{fn}: '{n['name']}' re-linked to {ref['cachedResultName']} ({new})")
            ref["value"], ref["cachedResultUrl"] = new, f"/workflow/{new}"
    for n in wf["nodes"]:
        t = n["type"].split(".")[-1]
        if n["type"] == "n8n-nodes-base.if" and n.get("typeVersion", 0) > 2.3:
            # The reconstructed template asks for If v2.4, which the pinned n8n 2.x does not provide.
            swaps.append(f"{fn}: '{n['name']}' If typeVersion {n['typeVersion']} -> 2.3 (not available in this n8n)")
            n["typeVersion"] = 2.3
        if t == "formTrigger" and not n.get("webhookId"):
            n["webhookId"] = str(uuid.uuid5(uuid.NAMESPACE_URL, "g2-form-" + wf["id"]))
            swaps.append(f"{fn}: '{n['name']}' formTrigger given webhookId {n['webhookId']} (template ships none; needed to publish)")
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
            if n["parameters"].get("mode") == "insert" and n["parameters"].get("embeddingBatchSize", 0) > 50:
                swaps.append(f"{fn}: '{n['name']}' embeddingBatchSize {n['parameters']['embeddingBatchSize']} -> 50 "
                             "(keeps each request under the HTTP timeout when the provider quota throttles)")
                n["parameters"]["embeddingBatchSize"] = 50
            swaps.append(f"{fn}: '{n['name']}' qdrant credential bound to internal Qdrant")
    json.dump(wf, open(os.path.join(out, fn), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("\n".join(swaps))
