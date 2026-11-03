"""De dónde llegan los correos: una carpeta de .eml (pruebas y desarrollo) o un buzón IMAP."""

from __future__ import annotations

import imaplib
import re
import ssl
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

PROCESSED_DIR = "procesados"


@dataclass(frozen=True)
class RawMail:
    uid: str
    raw: bytes
    received_at: datetime | None = None


class MailSource(Protocol):
    def __enter__(self) -> MailSource: ...

    def __exit__(self, *exc: object) -> None: ...

    def fetch(self, limit: int) -> list[RawMail]: ...

    def ack(self, uid: str) -> None: ...


class FolderSource:
    """Lee `*.eml` de una carpeta; al confirmar, los mueve a `procesados/`."""

    def __init__(self, inbox: Path) -> None:
        self.inbox = Path(inbox)

    def __enter__(self) -> FolderSource:
        self.inbox.mkdir(parents=True, exist_ok=True)
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def fetch(self, limit: int) -> list[RawMail]:
        return [RawMail(uid=path.name, raw=path.read_bytes()) for path in sorted(self.inbox.glob("*.eml"))[:limit]]

    def ack(self, uid: str) -> None:
        target = self.inbox / PROCESSED_DIR
        target.mkdir(exist_ok=True)
        (self.inbox / Path(uid).name).replace(target / Path(uid).name)


def _internaldate(response: bytes) -> datetime | None:
    parsed = imaplib.Internaldate2tuple(response)
    return datetime.fromtimestamp(time.mktime(parsed), timezone.utc) if parsed else None


class ImapSource:
    """IMAP sobre TLS. Lee sin marcar (`BODY.PEEK`) y marca como leído solo lo ya guardado en la cola."""

    def __init__(self, host: str, user: str, password: str, folder: str = "INBOX", port: int = 993,
                 timeout: int = 30, connect: Callable[..., imaplib.IMAP4] | None = None) -> None:
        if not host or not user or not password:
            raise ValueError("Configura DSAR_MAIL_IMAP_HOST, DSAR_MAIL_USER y DSAR_MAIL_PASSWORD.")
        self.host, self.user, self.password, self.folder, self.port, self.timeout = host, user, password, folder, port, timeout
        self.connect = connect or self._connect_tls
        self.conn: imaplib.IMAP4 | None = None

    def _connect_tls(self) -> imaplib.IMAP4:
        return imaplib.IMAP4_SSL(self.host, self.port, ssl_context=ssl.create_default_context(), timeout=self.timeout)

    def __enter__(self) -> ImapSource:
        self.conn = self.connect()
        self.conn.login(self.user, self.password)
        status, _ = self.conn.select(self.folder)
        if status != "OK":
            raise ValueError(f"No existe la carpeta {self.folder} en el buzón.")
        return self

    def __exit__(self, *exc: object) -> None:
        if self.conn is not None:
            try:
                self.conn.logout()
            finally:
                self.conn = None

    def _require(self) -> imaplib.IMAP4:
        if self.conn is None:
            raise RuntimeError("La fuente IMAP no está abierta.")
        return self.conn

    def fetch(self, limit: int) -> list[RawMail]:
        conn = self._require()
        status, data = conn.uid("SEARCH", None, "UNSEEN")
        if status != "OK":
            return []
        mails = []
        for uid in (data[0] or b"").split()[:limit]:
            status, parts = conn.uid("FETCH", uid, "(INTERNALDATE BODY.PEEK[])")
            item = next((part for part in parts or [] if isinstance(part, tuple)), None)
            if status != "OK" or item is None:
                continue
            header = item[0] if re.search(rb"INTERNALDATE", item[0]) else b""
            mails.append(RawMail(uid=uid.decode(), raw=item[1], received_at=_internaldate(header)))
        return mails

    def ack(self, uid: str) -> None:
        self._require().uid("STORE", uid, "+FLAGS", "(\\Seen)")
