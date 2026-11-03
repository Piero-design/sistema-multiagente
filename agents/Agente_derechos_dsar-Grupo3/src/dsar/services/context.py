"""Configuración y dependencias compartidas por los casos de uso (API, MCP y pruebas)."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from functools import cached_property
from pathlib import Path
from typing import Any

from dsar.assistant.llm import Provider, default_providers
from dsar.core.policy import load_org_policy
from dsar.core.profiles import load_profiles
from dsar.mail.smtp import MailSender, SmtpSender
from dsar.mail.sources import FolderSource, ImapSource, MailSource
from dsar.paths import BACKEND_ROOT, FIXTURES_DIR, ORGANIZATION_PATH, PROFILES_PATH, REFERENCES_DIR
from dsar.rag.retrieve import retrieve
from dsar.storage.repository import CaseRepository
from dsar.storage.sqlite import SqliteRepository

ENV_FILE = BACKEND_ROOT.parent / ".env"


def load_env_file(path: Path = ENV_FILE) -> list[str]:
    """Carga `CLAVE=valor` de un .env sin pisar variables ya definidas; devuelve las claves añadidas.

    Solo lo llaman los puntos de arranque (API y MCP), nunca las pruebas. Los valores vacíos se ignoran.
    """
    if not path.is_file():
        return []
    added = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = (part.strip() for part in line.removeprefix("export ").split("=", 1))
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key and value and key not in os.environ:
            os.environ[key] = value
            added.append(key)
    return added


def _env_path(name: str, default: Path) -> Path:
    value = os.environ.get(name, "").strip()
    return Path(value) if value else default


def _env_offset(name: str, default: int) -> int:
    value = os.environ.get(name, "").strip()
    if not value:
        return default
    try:
        offset = int(value)
    except ValueError:
        raise ValueError(f"{name} debe ser un entero entre -12 y 14 (horas respecto de UTC).") from None
    if not -12 <= offset <= 14:
        raise ValueError(f"{name} debe estar entre -12 y 14 (horas respecto de UTC).")
    return offset


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name, "").strip()
    if not value:
        return default
    if not value.isdigit() or int(value) <= 0:
        raise ValueError(f"{name} debe ser un entero positivo.")
    return int(value)


@dataclass(frozen=True)
class MailSettings:
    source: str = "folder"
    inbox_dir: Path = BACKEND_ROOT / "mail" / "entrada"
    imap_host: str = ""
    imap_port: int = 993
    user: str = ""
    password: str = field(default="", repr=False)
    folder: str = "INBOX"
    allowed_senders: tuple[str, ...] = ("*@example.test",)
    max_per_sender_hour: int = 20
    batch: int = 50
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_security: str = "starttls"
    from_address: str = "dsar@example.test"
    send_enabled: bool = False

    @classmethod
    def from_env(cls) -> MailSettings:
        source = os.environ.get("DSAR_MAIL_SOURCE", "folder").strip().lower() or "folder"
        if source not in {"folder", "imap"}:
            raise ValueError("DSAR_MAIL_SOURCE debe ser folder o imap.")
        senders = os.environ.get("DSAR_MAIL_ALLOWED_SENDERS", "").strip()
        return cls(
            source=source,
            inbox_dir=_env_path("DSAR_MAIL_INBOX_DIR", cls.inbox_dir),
            imap_host=os.environ.get("DSAR_MAIL_IMAP_HOST", "").strip(),
            imap_port=_env_int("DSAR_MAIL_IMAP_PORT", 993),
            user=os.environ.get("DSAR_MAIL_USER", "").strip(),
            password=os.environ.get("DSAR_MAIL_PASSWORD", ""),
            folder=os.environ.get("DSAR_MAIL_FOLDER", "INBOX").strip() or "INBOX",
            allowed_senders=tuple(item.strip().lower() for item in senders.split(",") if item.strip())
            if senders else cls.allowed_senders,
            max_per_sender_hour=_env_int("DSAR_MAIL_MAX_PER_SENDER_HOUR", 20),
            batch=_env_int("DSAR_MAIL_BATCH", 50),
            smtp_host=os.environ.get("DSAR_MAIL_SMTP_HOST", "").strip(),
            smtp_port=_env_int("DSAR_MAIL_SMTP_PORT", 587),
            smtp_security=os.environ.get("DSAR_MAIL_SMTP_SECURITY", "starttls").strip().lower() or "starttls",
            from_address=os.environ.get("DSAR_MAIL_FROM", "").strip() or os.environ.get("DSAR_MAIL_USER", "").strip()
            or cls.from_address,
            send_enabled=os.environ.get("DSAR_MAIL_SEND_ENABLED", "false").strip().lower() == "true",
        )


@dataclass(frozen=True)
class Settings:
    db_path: Path
    handoff_dir: Path
    export_dir: Path
    profiles_path: Path = PROFILES_PATH
    org_policy_path: Path = ORGANIZATION_PATH
    org_text_path: Path = REFERENCES_DIR / "organizacion-politica-interna.md"
    org_history_dir: Path = ORGANIZATION_PATH.parent / "historial"
    records_path: Path = FIXTURES_DIR / "subject-data.json"
    environment: str = "development"
    warmup: bool = True
    # Desfase respecto de UTC del día de trabajo (Lima: −5, sin horario de verano). Los plazos se cuentan por día civil.
    utc_offset_hours: int = -5
    mail: MailSettings = field(default_factory=MailSettings)

    @classmethod
    def from_env(cls) -> Settings:
        """Variables documentadas en .env.example; rutas relativas al backend por defecto."""
        return cls(
            db_path=_env_path("DSAR_DB_PATH", BACKEND_ROOT / "data" / "dsar.sqlite3"),
            handoff_dir=_env_path("DSAR_HANDOFF_DIR", BACKEND_ROOT / "handoffs"),
            export_dir=_env_path("DSAR_EXPORT_DIR", BACKEND_ROOT / "exports"),
            environment=os.environ.get("DSAR_ENV", "development").strip() or "development",
            utc_offset_hours=_env_offset("DSAR_UTC_OFFSET_HOURS", -5),
            mail=MailSettings.from_env(),
        )

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


@dataclass
class ServiceContext:
    """Todo lo que necesitan los casos de uso; las pruebas lo construyen con rutas temporales."""

    settings: Settings
    repository: CaseRepository
    providers: Mapping[str, Provider] = field(default_factory=default_providers)
    clock: Callable[[], datetime] = utc_now
    rag_method: str = "auto"
    semantic: bool = True
    mail_source_factory: Callable[[], MailSource] | None = None
    mail_sender_factory: Callable[[], MailSender] | None = None

    def now(self) -> datetime:
        return self.clock()

    def today(self) -> date:
        """El día civil de la jornada de trabajo (no el de UTC): de noche en Lima, UTC ya va un día adelantado."""
        return (self.clock() + timedelta(hours=self.settings.utc_offset_hours)).date()

    @cached_property
    def profiles(self) -> dict[str, Any]:
        return load_profiles(self.settings.profiles_path)

    def organization(self) -> dict[str, Any] | None:
        """Se lee en cada uso: una política guardada se aplica de inmediato."""
        path = self.settings.org_policy_path
        return load_org_policy(path, self.profiles) if path.is_file() else None

    def records(self) -> list[dict[str, Any]]:
        return json.loads(self.settings.records_path.read_text(encoding="utf-8"))

    def retrieve(self, query: str, top_k: int = 3) -> dict[str, Any]:
        return retrieve(query, top_k=top_k, method=self.rag_method)

    def mail_source(self) -> MailSource:
        if self.mail_source_factory is not None:
            return self.mail_source_factory()
        mail = self.settings.mail
        if mail.source == "imap":
            return ImapSource(mail.imap_host, mail.user, mail.password, mail.folder, mail.imap_port)
        return FolderSource(mail.inbox_dir)

    def mail_sender(self) -> MailSender:
        if self.mail_sender_factory is not None:
            return self.mail_sender_factory()
        mail = self.settings.mail
        return SmtpSender(mail.smtp_host, mail.smtp_port, mail.user, mail.password, mail.smtp_security)


def build_context(settings: Settings | None = None) -> ServiceContext:
    settings = settings or Settings.from_env()
    return ServiceContext(settings=settings, repository=SqliteRepository(settings.db_path))
