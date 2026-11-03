"""Envío por SMTP. Solo se usa cuando una persona pulsa «Enviar» en la bandeja de salida."""

from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage
from typing import Protocol

SECURITY = frozenset({"starttls", "ssl", "none"})
LOOPBACK = frozenset({"127.0.0.1", "localhost", "::1"})


class MailSender(Protocol):
    def send(self, message: EmailMessage) -> None: ...


class SmtpSender:
    def __init__(self, host: str, port: int, user: str = "", password: str = "", security: str = "starttls",
                 timeout: int = 30) -> None:
        if not host:
            raise ValueError("Configura DSAR_MAIL_SMTP_HOST.")
        if security not in SECURITY:
            raise ValueError("DSAR_MAIL_SMTP_SECURITY debe ser starttls, ssl o none.")
        if security == "none" and host not in LOOPBACK:
            raise ValueError("Sin cifrado solo se admite un servidor local (p. ej. Mailpit en 127.0.0.1).")
        self.host, self.port, self.user, self.password, self.security, self.timeout = (
            host, port, user, password, security, timeout)

    def _open(self) -> smtplib.SMTP:
        context = ssl.create_default_context()
        if self.security == "ssl":
            return smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout, context=context)
        server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
        if self.security == "starttls":
            server.starttls(context=context)
        return server

    def send(self, message: EmailMessage) -> None:
        with self._open() as server:
            if self.user:
                server.login(self.user, self.password)
            server.send_message(message)
