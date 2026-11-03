"""Correo RFC 5322 → InboundMessage: cabeceras útiles, texto limpio y huellas de los adjuntos."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email import message_from_bytes, policy
from email.message import EmailMessage
from email.utils import parseaddr, parsedate_to_datetime
from html.parser import HTMLParser

MAX_TEXT = 4000
AUTOMATIC_SENDERS = ("mailer-daemon@", "postmaster@", "no-reply@", "noreply@")
REPLY_MARKERS = re.compile(
    r"^(\s*(el|on)\s.{0,120}(escribi[oó]|wrote)\s*:\s*$|-{2,}\s*(mensaje original|original message)\s*-{2,})",
    re.IGNORECASE)


@dataclass(frozen=True)
class Attachment:
    filename: str
    content_type: str
    size: int
    sha256: str


@dataclass(frozen=True)
class InboundMessage:
    message_id: str
    sender: str
    subject: str
    text: str
    received_at: datetime
    sha256: str
    in_reply_to: str | None = None
    references: tuple[str, ...] = ()
    automatic: bool = False
    attachments: tuple[Attachment, ...] = field(default_factory=tuple)


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style"}:
            self.skip += 1
        elif tag in {"br", "p", "div", "li", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.parts.append(data)


def html_to_text(html: str) -> str:
    extractor = _TextExtractor()
    extractor.feed(html)
    return "".join(extractor.parts)


def clean_text(text: str) -> str:
    """Quita la parte citada de respuestas anteriores y la firma; normaliza espacios."""
    lines: list[str] = []
    for line in text.replace("\r\n", "\n").split("\n"):
        if REPLY_MARKERS.match(line) or line.rstrip() == "--":
            break
        if line.lstrip().startswith(">"):
            continue
        lines.append(line.rstrip())
    cleaned = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    return cleaned[:MAX_TEXT]


def _body(message: EmailMessage) -> str:
    part = message.get_body(preferencelist=("plain", "html"))
    if part is None:
        return ""
    content = part.get_content()
    return html_to_text(content) if part.get_content_type() == "text/html" else content


def _attachments(message: EmailMessage) -> tuple[Attachment, ...]:
    found = []
    for part in message.iter_attachments():
        payload = part.get_payload(decode=True) or b""
        found.append(Attachment(filename=(part.get_filename() or "sin-nombre")[:200],
                                content_type=part.get_content_type(), size=len(payload),
                                sha256=hashlib.sha256(payload).hexdigest()))
    return tuple(found)


def _is_automatic(message: EmailMessage, sender: str) -> bool:
    auto = str(message.get("Auto-Submitted", "no")).strip().lower()
    precedence = str(message.get("Precedence", "")).strip().lower()
    return (auto != "no" or precedence in {"bulk", "junk", "list"} or message.get("List-Unsubscribe") is not None
            or message.get_content_type() == "multipart/report" or sender.startswith(AUTOMATIC_SENDERS))


def _ids(value: str | None) -> tuple[str, ...]:
    return tuple(re.findall(r"<[^<>\s]+>", value or ""))


def _date(message: EmailMessage) -> datetime | None:
    try:
        value = parsedate_to_datetime(str(message["Date"])) if message["Date"] else None
    except (TypeError, ValueError):
        return None
    if value is None:
        return None
    return (value if value.tzinfo else value.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)


def parse_message(raw: bytes, server_received_at: datetime | None = None) -> InboundMessage:
    """La fecha de recepción es la del servidor si se conoce; la cabecera Date la pone el remitente."""
    message = message_from_bytes(raw, policy=policy.default)
    digest = hashlib.sha256(raw).hexdigest()
    sender = parseaddr(str(message.get("From", "")))[1].strip().lower()
    received = server_received_at or _date(message) or datetime.now(timezone.utc)
    message_id = (_ids(str(message.get("Message-ID", ""))) or (f"<{digest[:32]}@sin-message-id>",))[0]
    in_reply_to = _ids(str(message.get("In-Reply-To", "")))
    return InboundMessage(
        message_id=message_id[:300],
        sender=sender[:254],
        subject=str(message.get("Subject", "")).strip()[:300],
        text=clean_text(_body(message)),
        received_at=received.astimezone(timezone.utc).replace(microsecond=0),
        sha256=digest,
        in_reply_to=in_reply_to[0] if in_reply_to else None,
        references=_ids(str(message.get("References", ""))),
        automatic=_is_automatic(message, sender),
        attachments=_attachments(message),
    )
