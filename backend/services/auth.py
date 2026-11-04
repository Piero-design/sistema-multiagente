"""Minimal authentication for human decisions. Demo accounts come from HUMAN_USERS ("user:password:ROLE;...").
Tokens are HMAC-signed and expire; the secret is random per process unless HUMAN_SECRET is set.
This identifies WHO decides so the decision can be recorded; it is not a full identity system."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from fastapi import Header, HTTPException

_SECRET = (os.getenv("HUMAN_SECRET") or secrets.token_hex(32)).encode()
TTL = 8 * 3600


def _users() -> dict[str, tuple[str, str]]:
    out = {}
    for item in os.getenv("HUMAN_USERS", "").split(";"):
        parts = item.strip().split(":")
        if len(parts) == 3 and all(parts):
            out[parts[0]] = (parts[1], parts[2])
    return out


def login(user: str, password: str) -> dict:
    rec = _users().get(user)
    ok = rec is not None and hmac.compare_digest(rec[0].encode(), password.encode())
    if not ok:
        time.sleep(1)                               # slows down guessing
        raise HTTPException(401, "Usuario o contraseña incorrectos")
    payload = base64.urlsafe_b64encode(json.dumps({"u": user, "r": rec[1], "e": int(time.time()) + TTL}).encode()).decode()
    sig = hmac.new(_SECRET, payload.encode(), hashlib.sha256).hexdigest()
    return {"token": f"{payload}.{sig}", "user": user, "role": rec[1]}


def current(authorization: str | None = Header(default=None)) -> dict:
    """FastAPI dependency: the authenticated human, or 401."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Inicia sesión para registrar decisiones humanas")
    token = authorization[7:]
    try:
        payload, sig = token.rsplit(".", 1)
        good = hmac.new(_SECRET, payload.encode(), hashlib.sha256).hexdigest()
        data = json.loads(base64.urlsafe_b64decode(payload.encode()))
        if not hmac.compare_digest(sig, good) or data["e"] < time.time():
            raise ValueError
    except Exception:  # noqa: BLE001
        raise HTTPException(401, "Sesión inválida o vencida")
    return {"user": data["u"], "role": data["r"]}


def require(*roles: str):
    def dep(authorization: str | None = Header(default=None)) -> dict:
        who = current(authorization)
        if who["role"] not in roles:
            raise HTTPException(403, f"Esta acción requiere el rol: {', '.join(roles)}")
        return who
    return dep
