"""Integration wrapper for Group 3: same server, bound to 0.0.0.0 inside the container network."""
from dsar.mcp import server

server.HTTP_HOST = "0.0.0.0"
raise SystemExit(server.main(["--http"]))
