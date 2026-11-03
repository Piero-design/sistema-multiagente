"""Correos entrantes: cola, análisis, registro automático y triaje humano."""

from __future__ import annotations

import hashlib
import imaplib
import time
from collections import Counter
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.utils import format_datetime, make_msgid
from fnmatch import fnmatchcase
from typing import Any

from dsar.assistant import guard
from dsar.assistant.intake import (
    DISCARD,
    REGISTER,
    TRIAGE,
    extract,
    keyword_is_dsar,
    keyword_rights,
    ordered,
    route,
    valid_email,
)
from dsar.assistant.llm import LLMError
from dsar.core.errors import CaseInputError, TransitionError
from dsar.mail.demo import generate, to_message
from dsar.mail.parse import parse_message
from dsar.services import cases, outbox
from dsar.services.context import ServiceContext
from dsar.services.errors import MailboxError, NotFoundError

RECEIVED, ANALYSING, REGISTERED, LINKED = "recibido", "en_analisis", "registrado", "asociado"
STATES = (RECEIVED, ANALYSING, REGISTERED, TRIAGE, DISCARD, LINKED)
DUPLICATE = "duplicado"
STALE_AFTER = timedelta(minutes=10)
MAX_ATTEMPTS = 3
DEFAULT_PROFILE = "PE-LEY29733"
LIST_FIELDS = ("id", "message_id", "sender", "subject", "received_at", "status", "reason", "case_id", "attempts",
               "analysis_s", "decided_by", "updated_at")


def _iso(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat()


def sender_allowed(sender: str, patterns: tuple[str, ...]) -> bool:
    return bool(sender) and any(fnmatchcase(sender, pattern) for pattern in patterns)


def enqueue(ctx: ServiceContext, raw: bytes, server_received_at: datetime | None = None) -> str:
    """Guarda el correo en la cola. Lo que se descarta aquí nunca llega al modelo."""
    message = parse_message(raw, server_received_at)
    repo, mail = ctx.repository, ctx.settings.mail
    if repo.has_inbound(message.message_id, message.sha256):
        return DUPLICATE
    status, reason, body = RECEIVED, None, message.text
    allowed = sender_allowed(message.sender, mail.allowed_senders)
    thread = [item for item in (message.in_reply_to, *message.references) if item]
    linked = repo.outbox_case(thread) if allowed and not message.automatic else None
    since = _iso(message.received_at - timedelta(hours=1))
    if not allowed:
        status, reason, body = DISCARD, "Remitente fuera de la lista blanca.", ""
    elif message.automatic:
        status, reason = DISCARD, "Respuesta automática o envío masivo."
    elif linked:
        status, reason = LINKED, f"Respuesta del titular al expediente {linked}."
    elif repo.count_inbound_from(message.sender, since) >= mail.max_per_sender_hour:
        status, reason = DISCARD, f"Cuarentena: más de {mail.max_per_sender_hour} correos del remitente en una hora."
    elif not body:
        status, reason = TRIAGE, "El correo no tiene texto que analizar."
    inserted = repo.add_inbound({
        "message_id": message.message_id, "sha256": message.sha256, "sender": message.sender,
        "subject": message.subject, "body": body, "received_at": _iso(message.received_at),
        "in_reply_to": message.in_reply_to, "status": status, "reason": reason,
        "attachments": [vars(item) for item in message.attachments] if body else [],
    })
    if inserted and linked:
        repo.update_inbound(inserted, case_id=linked)
        outbox.link_reply(ctx, linked, inserted)
    return status if inserted else DUPLICATE


def ingest(ctx: ServiceContext) -> dict[str, int]:
    """Descarga un lote del buzón; cada correo se confirma en la fuente solo después de guardarlo."""
    counts: Counter[str] = Counter()
    try:
        with ctx.mail_source() as source:
            for mail in source.fetch(ctx.settings.mail.batch):
                counts[enqueue(ctx, mail.raw, mail.received_at)] += 1
                source.ack(mail.uid)
    except (OSError, imaplib.IMAP4.error, ValueError) as exc:
        raise MailboxError(f"No se pudo leer el buzón: {exc}") from exc
    return dict(counts)


def principal_for(ctx: ServiceContext, email: str) -> str:
    """Titular sintético con ese correo o, si no existe, un seudónimo estable del correo."""
    for record in ctx.records():
        if str(record.get("data", {}).get("email", "")).lower() == email:
            return record["principal_id"]
    return "mail-" + hashlib.sha256(email.encode("utf-8")).hexdigest()[:12]


def _received_date(ctx: ServiceContext, received_at: str) -> str:
    local = datetime.fromisoformat(received_at) + timedelta(hours=ctx.settings.utc_offset_hours)
    return local.date().isoformat()


def register_from_mail(ctx: ServiceContext, item: dict[str, Any], rights: list[str] | tuple[str, ...],
                       subject_email: str) -> str:
    request = {
        "principal_id": principal_for(ctx, subject_email),
        "request_types": list(rights),
        "policy_id": (ctx.organization() or {}).get("legal_profile") or DEFAULT_PROFILE,
        "received_at": _received_date(ctx, item["received_at"]),
        "request_text": item["body"][:2000],
        "identity_verification": {"status": "pending", "method": "correo electrónico (sin verificar)",
                                  "reference": item["message_id"][:200]},
    }
    case_id = cases.register(ctx, request, origin="EMAIL")["case"]["case_id"]
    outbox.prepare(ctx, case_id, "identidad", subject_email, in_reply_to=item["message_id"])
    return case_id


def _log(ctx: ServiceContext, entry: dict[str, Any] | None) -> None:
    if entry:
        ctx.repository.log_llm_call(entry | {"task": "correo"})


def _analyse(ctx: ServiceContext, item: dict[str, Any]) -> dict[str, Any]:
    text = f"{item['subject']}\n{item['body']}"
    keywords, hinted = keyword_rights(text), keyword_is_dsar(text)
    evidence: dict[str, Any] = {"keywords": list(keywords), "hinted": hinted, "model": None}
    evasion = guard.detect_evasion(item["body"], semantic=ctx.semantic)
    evidence["evasion"] = evasion
    if evasion:
        return {"status": TRIAGE, "reason": f"El filtro de evasión detectó un intento de tipo «{evasion}».",
                "proposal": evidence}
    provider = ctx.providers.get("ollama")
    if provider is None:
        return {"status": TRIAGE, "reason": "No hay un modelo local configurado.", "proposal": evidence}
    try:
        proposal, result = extract(provider, item["subject"], item["body"])
    except LLMError as exc:
        _log(ctx, exc.entry)
        return {"status": TRIAGE, "reason": f"El modelo no pudo analizar el correo: {exc}", "proposal": evidence}
    _log(ctx, result.log_entry())
    subject_email = proposal.subject_email or valid_email(item["sender"])
    evidence |= {"model": proposal.to_dict(), "subject_email": subject_email}
    status, reason = route(keywords, hinted, proposal, subject_email)
    if status != REGISTER:
        return {"status": status, "reason": reason, "proposal": evidence}
    try:
        case_id = register_from_mail(ctx, item, proposal.rights, subject_email)
    except CaseInputError as exc:
        return {"status": TRIAGE, "reason": f"No se pudo registrar: {exc}", "proposal": evidence}
    return {"status": REGISTERED, "reason": reason, "proposal": evidence, "case_id": case_id}


def process_next(ctx: ServiceContext) -> dict[str, Any] | None:
    now = ctx.now()
    item = ctx.repository.claim_inbound(_iso(now), _iso(now - STALE_AFTER))
    if item is None:
        return None
    if item["attempts"] > MAX_ATTEMPTS:
        outcome = {"status": TRIAGE, "reason": "Se agotaron los intentos de análisis."}
    else:
        started = time.monotonic()
        outcome = _analyse(ctx, item) | {"analysis_s": round(time.monotonic() - started, 2)}
    ctx.repository.update_inbound(item["id"], **outcome)
    return get(ctx, item["id"])


def process_pending(ctx: ServiceContext, limit: int) -> list[dict[str, Any]]:
    processed = []
    for _ in range(limit):
        item = process_next(ctx)
        if item is None:
            break
        processed.append(item)
    return processed


def synchronize(ctx: ServiceContext, limit: int) -> dict[str, Any]:
    fetched = ingest(ctx)
    processed = process_pending(ctx, limit)
    return {"fetched": fetched, "processed": dict(Counter(item["status"] for item in processed)),
            "pending": ctx.repository.count_inbound().get(RECEIVED, 0)}


def get(ctx: ServiceContext, inbound_id: int) -> dict[str, Any]:
    item = ctx.repository.get_inbound(inbound_id)
    if item is None:
        raise NotFoundError(f"No existe el correo {inbound_id}.")
    return item


def list_inbound(ctx: ServiceContext, status: str | None = None, case_id: str | None = None) -> list[dict[str, Any]]:
    if status is not None and status not in STATES:
        raise CaseInputError(f"Estado de correo desconocido: {status}")
    rows = ctx.repository.list_inbound(status, case_id=case_id)
    return [{key: item[key] for key in LIST_FIELDS} for item in rows]


def summary(ctx: ServiceContext) -> dict[str, int]:
    counts = ctx.repository.count_inbound()
    return {state: counts.get(state, 0) for state in STATES}


def _in_triage(ctx: ServiceContext, inbound_id: int) -> dict[str, Any]:
    item = get(ctx, inbound_id)
    if item["status"] != TRIAGE:
        raise TransitionError(f"El correo está en estado {item['status']}; solo se resuelve desde triaje.")
    return item


def _reviewer(reviewer: str) -> str:
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise CaseInputError("Indica quién resuelve el triaje.")
    return reviewer.strip()


def confirm(ctx: ServiceContext, inbound_id: int, reviewer: str, rights: list[str], subject_email: str) -> dict[str, Any]:
    """Una persona confirma (o corrige) la propuesta y el caso se registra con origen EMAIL."""
    reviewer = _reviewer(reviewer)
    item = _in_triage(ctx, inbound_id)
    email = valid_email(subject_email)
    if email is None:
        raise CaseInputError("Indica un correo válido del titular.")
    if not rights:
        raise CaseInputError("Indica al menos un derecho.")
    case_id = register_from_mail(ctx, item, ordered(rights), email)
    ctx.repository.update_inbound(inbound_id, status=REGISTERED, case_id=case_id, decided_by=reviewer,
                                  reason=f"Confirmado en triaje por {reviewer}.")
    return get(ctx, inbound_id)


def discard(ctx: ServiceContext, inbound_id: int, reviewer: str, reason: str) -> dict[str, Any]:
    reviewer = _reviewer(reviewer)
    _in_triage(ctx, inbound_id)
    if not isinstance(reason, str) or not reason.strip():
        raise CaseInputError("Indica el motivo del descarte.")
    ctx.repository.update_inbound(inbound_id, status=DISCARD, decided_by=reviewer,
                                  reason=f"Descartado por {reviewer}: {reason.strip()}")
    return get(ctx, inbound_id)


def reopen(ctx: ServiceContext, inbound_ids: list[int], reviewer: str) -> list[dict[str, Any]]:
    """Una persona pasa a triaje correos descartados por su contenido (no los de remitentes ajenos: no hay cuerpo)."""
    reviewer = _reviewer(reviewer)
    items = [get(ctx, inbound_id) for inbound_id in dict.fromkeys(inbound_ids)]
    for item in items:
        if item["status"] != DISCARD or not item["body"]:
            raise TransitionError(f"El correo {item['id']} no es un descarte por contenido; no se puede reabrir.")
    for item in items:
        ctx.repository.update_inbound(item["id"], status=TRIAGE, decided_by=reviewer,
                                      reason=f"Reabierto por {reviewer} para revisión.")
    return [get(ctx, item["id"]) for item in items]


def build_message(sender: str, subject: str, body: str, sent_at: datetime, to: str = "dsar@example.test") -> bytes:
    message = EmailMessage()
    message["From"], message["To"], message["Subject"] = sender, to, subject
    message["Date"] = format_datetime(sent_at)
    message["Message-ID"] = make_msgid(domain="example.test")
    message.set_content(body)
    return bytes(message)


def _require_development(ctx: ServiceContext) -> None:
    if not ctx.settings.is_development:
        raise NotFoundError("Los correos de demostración solo existen en desarrollo.")


def load_demo(ctx: ServiceContext, count: int, seed: int | None = None) -> dict[str, Any]:
    """Solo en desarrollo: encola correos del generador de la demo. Otra semilla da correos nuevos."""
    _require_development(ctx)
    seed = int(ctx.now().timestamp()) if seed is None else seed
    now = ctx.now()
    counts = Counter(enqueue(ctx, bytes(to_message(mail, now - timedelta(seconds=count - mail.number))))
                     for mail in generate(count, seed))
    return {"seed": seed, "queued": dict(counts), "pending": ctx.repository.count_inbound().get(RECEIVED, 0)}
