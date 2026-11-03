"""Bandeja de salida: el agente prepara los correos al titular y solo una persona los envía."""

from __future__ import annotations

import copy
import hashlib
import smtplib
from email.message import EmailMessage
from email.utils import format_datetime, make_msgid
from fnmatch import fnmatchcase
from typing import Any

from dsar.assistant.guard import executed_claims
from dsar.core.engine import append_event
from dsar.core.errors import CaseInputError, TransitionError
from dsar.core.procedures import observe_request
from dsar.core.render import guided_letter
from dsar.core.states import TERMINAL_STATES
from dsar.services import cases
from dsar.services.context import ServiceContext
from dsar.services.errors import MailboxError, NotFoundError

DRAFT, SENT, DISCARDED = "borrador", "enviado", "descartado"
STATES = (DRAFT, SENT, DISCARDED)
KINDS = ("identidad", "subsanacion", "respuesta")
SUBJECTS = {"identidad": "Verificación de identidad para su solicitud",
            "subsanacion": "Información pendiente de su solicitud",
            "respuesta": "Respuesta a su solicitud de derechos"}
IDENTITY_STEP = ("Para continuar, responda a este correo con la información que nos permita verificar su identidad "
                 "(por ejemplo, el número de su documento). Una persona la revisará; un correo por sí solo no "
                 "basta para confirmarla.")
DECIDED = frozenset({"APPROVED", "REJECTED"})


def _text(value: str, message: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CaseInputError(message)
    return value.strip()


def recipient_allowed(ctx: ServiceContext, address: str) -> bool:
    return any(fnmatchcase(address.lower(), pattern) for pattern in ctx.settings.mail.allowed_senders)


def _letter(package: dict[str, Any], kind: str, missing: str | None) -> str:
    letter = guided_letter(package).replace("  \n", "\n")
    body, closing = letter.rsplit("\n\nAtentamente", 1)
    extra = []
    if kind == "identidad":
        extra.append(IDENTITY_STEP)
    if kind == "subsanacion" and missing:
        extra.append(f"Para continuar con su solicitud necesitamos que nos indique: {missing}")
    return "\n\n".join([body, *extra]) + "\n\nAtentamente" + closing + "\n"


def _check_kind(package: dict[str, Any], kind: str) -> None:
    if kind not in KINDS:
        raise CaseInputError(f"Tipo de correo desconocido: {kind}")
    if kind == "respuesta" and package["status"] not in DECIDED:
        raise TransitionError("La respuesta solo se prepara después de la decisión humana.")
    if kind != "respuesta" and package["status"] in TERMINAL_STATES:
        raise TransitionError(f"El expediente está en {package['status']}.")
    if kind == "identidad" and package["status"] != "IDENTITY_PENDING":
        raise TransitionError("La identidad del titular ya no está pendiente.")


def _observation(ctx: ServiceContext, package: dict[str, Any], outbox_id: int | str, decided_by: str) -> dict[str, Any]:
    """Observación del art. 66.2 que suspende el plazo; el motor rechaza si el perfil no la admite o ya pasó el plazo."""
    return observe_request(package, ctx.profiles, ctx.today(),
                           f"Información pendiente solicitada al titular por correo (salida {outbox_id}).", decided_by)


def last_address(ctx: ServiceContext, case_id: str) -> tuple[str | None, str | None]:
    """Dirección y Message-ID del último correo del expediente, para responder en el mismo hilo."""
    previous = ctx.repository.list_outbox(case_id=case_id)
    if not previous:
        return None, None
    return previous[0]["to_address"], previous[0]["message_id"] or previous[0]["in_reply_to"]


def prepare(ctx: ServiceContext, case_id: str, kind: str, to_address: str | None = None,
            in_reply_to: str | None = None, missing: str | None = None) -> dict[str, Any]:
    package = cases.get(ctx, case_id)
    _check_kind(package, kind)
    if kind == "subsanacion":
        missing = _text(missing or "", "Indica qué información falta.")[:500]
        _observation(ctx, package, "por preparar", "verificación previa")
    known, thread = last_address(ctx, case_id)
    address = (to_address or known or "").strip().lower()
    if not address:
        raise CaseInputError("Indica el correo del titular.")
    for item in ctx.repository.list_outbox(DRAFT, case_id):
        if item["kind"] == kind:
            return item
    outbox_id = ctx.repository.add_outbox({
        "case_id": case_id, "kind": kind, "to_address": address, "in_reply_to": in_reply_to or thread,
        "subject": f"[{case_id}] {SUBJECTS[kind]}", "body": _letter(package, kind, missing),
    })
    return get(ctx, outbox_id)


def after_decision(ctx: ServiceContext, package: dict[str, Any]) -> dict[str, Any] | None:
    """Si el caso llegó por correo, deja la respuesta preparada en la bandeja de salida."""
    if cases.origin_of(package["case_id"]) != "EMAIL" or package["status"] not in DECIDED:
        return None
    if last_address(ctx, package["case_id"])[0] is None:
        return None
    return prepare(ctx, package["case_id"], "respuesta")


def get(ctx: ServiceContext, outbox_id: int) -> dict[str, Any]:
    item = ctx.repository.get_outbox(outbox_id)
    if item is None:
        raise NotFoundError(f"No existe el correo de salida {outbox_id}.")
    return item | {"warnings": executed_claims(item["body"])}


def list_outbox(ctx: ServiceContext, status: str | None = None, case_id: str | None = None) -> list[dict[str, Any]]:
    if status is not None and status not in STATES:
        raise CaseInputError(f"Estado de salida desconocido: {status}")
    return ctx.repository.list_outbox(status, case_id)


def _draft(ctx: ServiceContext, outbox_id: int) -> dict[str, Any]:
    item = get(ctx, outbox_id)
    if item["status"] != DRAFT:
        raise TransitionError(f"El correo ya está {item['status']}.")
    return item


def edit(ctx: ServiceContext, outbox_id: int, reviewer: str, subject: str, body: str) -> dict[str, Any]:
    _text(reviewer, "Indica quién edita el correo.")
    _draft(ctx, outbox_id)
    ctx.repository.update_outbox(outbox_id, subject=_text(subject, "Indica el asunto.")[:300],
                                 body=_text(body, "El correo no puede quedar vacío.")[:20_000])
    return get(ctx, outbox_id)


def discard(ctx: ServiceContext, outbox_id: int, reviewer: str, reason: str) -> dict[str, Any]:
    reviewer = _text(reviewer, "Indica quién descarta el correo.")
    _draft(ctx, outbox_id)
    ctx.repository.update_outbox(outbox_id, status=DISCARDED, decided_by=reviewer,
                                 reason=_text(reason, "Indica el motivo del descarte.")[:500])
    return get(ctx, outbox_id)


def _message(ctx: ServiceContext, item: dict[str, Any]) -> EmailMessage:
    sender = ctx.settings.mail.from_address
    message = EmailMessage()
    message["From"], message["To"], message["Subject"] = sender, item["to_address"], item["subject"]
    message["Date"] = format_datetime(ctx.now())
    message["Message-ID"] = make_msgid(domain=sender.rsplit("@", 1)[-1])
    if item["in_reply_to"]:
        message["In-Reply-To"] = message["References"] = item["in_reply_to"]
    message.set_content(item["body"])
    return message


def send(ctx: ServiceContext, outbox_id: int, reviewer: str) -> dict[str, Any]:
    """Única vía de envío: una persona, con el envío activado y a un destinatario de la lista blanca."""
    reviewer = _text(reviewer, "Indica quién envía el correo.")
    item = _draft(ctx, outbox_id)
    if not ctx.settings.mail.send_enabled:
        raise TransitionError("El envío de correos está desactivado (DSAR_MAIL_SEND_ENABLED=false).")
    if not recipient_allowed(ctx, item["to_address"]):
        raise TransitionError("El destinatario no está en la lista blanca de la demo.")
    if item["warnings"]:
        raise CaseInputError("El correo afirma una acción ejecutada; corrígelo antes de enviarlo.")
    package = cases.get(ctx, item["case_id"])
    held = _observation(ctx, package, outbox_id, reviewer) if item["kind"] == "subsanacion" else None
    message = _message(ctx, item)
    try:
        ctx.mail_sender().send(message)
    except (OSError, smtplib.SMTPException, ValueError) as exc:
        raise MailboxError(f"No se pudo enviar el correo: {exc}") from exc
    ctx.repository.update_outbox(outbox_id, status=SENT, decided_by=reviewer, sent_at=ctx.now().isoformat(),
                                 message_id=message["Message-ID"],
                                 sha256=hashlib.sha256(bytes(message)).hexdigest())
    logged = held or copy.deepcopy(package)
    append_event(logged, logged["status"], f"Correo «{item['kind']}» enviado al titular por {reviewer}.")
    cases.save(ctx, logged)
    return get(ctx, outbox_id)


def link_reply(ctx: ServiceContext, case_id: str, inbound_id: int) -> None:
    """Deja constancia en el expediente de que el titular respondió por correo."""
    package = copy.deepcopy(cases.get(ctx, case_id))
    append_event(package, package["status"], f"El titular respondió por correo (mensaje {inbound_id}).")
    cases.save(ctx, package)
