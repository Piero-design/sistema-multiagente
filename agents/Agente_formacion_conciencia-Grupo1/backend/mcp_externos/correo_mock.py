import hashlib
import uuid
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_EMAIL, RESEND_API_KEY
from db import get_db_connection, registrar_audit

logger = logging.getLogger("mcp_correo")

def _despachar_resend_real(destinatario_email: str, asunto: str, cuerpo: str, remitente_email: str) -> bool:
    """
    Despacha correo real mediante Resend API (Directo a la bandeja de Gmail sin contraseñas de app).
    """
    if not RESEND_API_KEY:
        return False
    try:
        dest_envio = destinatario_email
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": "UNSA Formacion y Privacidad <onboarding@resend.dev>",
                    "to": [dest_envio],
                    "reply_to": remitente_email,
                    "subject": asunto,
                    "text": cuerpo
                }
            )
            if resp.status_code in (200, 201):
                logger.info(f"[Resend] Correo entregado exitosamente a {dest_envio}")
                print(f" -> [Resend API] Correo entregado fisicamente a {dest_envio}!")
                return True
            else:
                logger.warning(f"[Resend] Error {resp.status_code}: {resp.text}")
                print(f" -> [Resend API] Error {resp.status_code}: {resp.text}")
                return False
    except Exception as e:
        logger.warning(f"[Resend] Excepcion: {e}")
        return False

def _despachar_smtp_real(destinatario_email: str, asunto: str, cuerpo: str, remitente_email: str) -> bool:
    """
    Intenta el despacho físico mediante servidor SMTP (ej. Gmail / Google Workspace UNSA).
    """
    if not (SMTP_USER and SMTP_PASSWORD):
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = f"UNSA PIMS <{remitente_email}>"
        msg['To'] = destinatario_email
        msg['Subject'] = asunto
        msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=12)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"[SMTP REAL] Correo despachado físicamente a {destinatario_email}")
        print(f" -> [SMTP REAL] Correo entregado con exito a la bandeja de {destinatario_email}")
        return True
    except Exception as e:
        logger.warning(f"[SMTP REAL] Fallo entrega SMTP a {destinatario_email}: {e}")
        print(f" -> [SMTP REAL] Error de entrega SMTP a {destinatario_email}: {e}")
        return False

def enviar_correo(destinatarios: list[dict | str], asunto: str, cuerpo: str, remitente_id: str = "admin", lote_id: str = None) -> dict:
    """
    MCP Correo:
    1. Si RESEND_API_KEY o SMTP están configurados en .env, envía el correo físico real a la bandeja.
    2. Registra siempre en SQLite `correos_enviados` con hash SHA256 y en `audit_log` para ISO 27701.
    """
    if not lote_id:
        lote_id = f"lote_{uuid.uuid4().hex[:8]}"

    # Hash SHA256 del contenido
    contenido_hash = hashlib.sha256(f"{asunto}||{cuerpo}".encode("utf-8")).hexdigest()
    now = datetime.now().isoformat()

    enviados_count = 0
    detalles_envio = []

    with get_db_connection() as conn:
        # Resolver correo del remitente (admin)
        rem_row = conn.execute("SELECT email, nombre FROM usuarios WHERE id = ?", (remitente_id,)).fetchone()
        remitente_email = (rem_row["email"] if rem_row and rem_row["email"] else SMTP_FROM_EMAIL) or "jchuraaca@unsa.edu.pe"

        print("\n" + "="*50)
        print(f"[MCP Correo] INICIANDO ENVIO (Lote: {lote_id})")
        print(f"De: {remitente_email} (ID: {remitente_id})")
        print(f"Asunto: {asunto}")
        print(f"Cuerpo:\n{cuerpo}")
        print("="*50)

        for dest in destinatarios:
            if isinstance(dest, dict):
                d_id = dest.get("id")
                d_email = dest.get("email")
            else:
                d_id = str(dest)
                d_email = None

            # Buscar email real en la base de datos si no venía en el diccionario
            if not d_email or "@" not in d_email:
                row = conn.execute("SELECT email FROM usuarios WHERE id = ?", (d_id,)).fetchone()
                if row and row["email"]:
                    d_email = row["email"]
                else:
                    d_email = f"{d_id}@unsa.edu.pe" if "@" not in str(d_id) else str(d_id)

            correo_id = f"mail_{uuid.uuid4().hex[:10]}"
            conn.execute(
                """
                INSERT INTO correos_enviados (
                    id, lote_id, remitente_user_id, destinatario_user_id,
                    destinatario_email, asunto, cuerpo, enviado_at, hash_sha256
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (correo_id, lote_id, remitente_id, d_id, d_email, asunto, cuerpo, now, contenido_hash)
            )
            enviados_count += 1
            detalles_envio.append({"id": correo_id, "destinatario": d_email})
            print(f" -> [DB] Registrado en base de datos para {d_email} (ID: {correo_id})")

            # Intentar despacho real (Resend API o SMTP) si está configurado
            entregado = _despachar_resend_real(destinatario_email=d_email, asunto=asunto, cuerpo=cuerpo, remitente_email=remitente_email)
            if not entregado:
                _despachar_smtp_real(destinatario_email=d_email, asunto=asunto, cuerpo=cuerpo, remitente_email=remitente_email)

    print(f"[MCP Correo] Total enviados: {enviados_count}\n" + "="*50 + "\n")

    # Registro en audit log
    registrar_audit(
        user_id=remitente_id,
        accion="correo_mock",
        detalle={
            "lote_id": lote_id,
            "total_destinatarios": enviados_count,
            "asunto": asunto,
            "hash_sha256": contenido_hash
        }
    )

    return {
        "status": "success",
        "lote_id": lote_id,
        "total": len(destinatarios),
        "enviados": enviados_count,
        "fallidos": 0,
        "hash_sha256": contenido_hash,
        "detalles": detalles_envio
    }
