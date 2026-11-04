#!/bin/sh
# Group 3 container: the agent's MCP server (unchanged) + the internal human-decision bridge (g3_human.py, with
# the DPO case-work routes of g3_gestion.py added to the same app) + the agent's own mail worker (reads the mailbox
# folder or IMAP and queues requests; it never decides).
python -m uvicorn --app-dir /opt g3_gestion:app --host 0.0.0.0 --port 8002 &
python -m dsar.worker --interval "${DSAR_WORKER_INTERVAL:-60}" &
exec python /opt/g3_run.py
