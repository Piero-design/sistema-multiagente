#!/bin/sh
# Group 3 container: the agent's MCP server (unchanged) + the internal human-decision bridge.
python -m uvicorn --app-dir /opt g3_human:app --host 0.0.0.0 --port 8002 &
exec python /opt/g3_run.py
