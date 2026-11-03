import os
import uuid
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from config import EVIDENCIAS_PATH
from db import get_db_connection, registrar_audit

logger = logging.getLogger("mcp_evidencias")

def guardar_evidencia(user_id: str, archivo: str, control_iso: str, contenido: str | bytes = None) -> dict:
    """
    MCP Evidencias (Mock persistente):
    Calcula hash SHA256, guarda archivo en ./evidencias/ e inserta registro en la tabla `evidencias`.
    """
    evidencia_id = f"evi_{uuid.uuid4().hex[:10]}"
    now = datetime.now().isoformat()

    if contenido is None:
        contenido_bytes = f"EVIDENCIA DE CONFORMIDAD PIMS UNSA\nControl: {control_iso}\nUsuario: {user_id}\nArchivo: {archivo}\nFecha: {now}".encode("utf-8")
    elif isinstance(contenido, str):
        contenido_bytes = contenido.encode("utf-8")
    else:
        contenido_bytes = contenido

    hash_sha256 = hashlib.sha256(contenido_bytes).hexdigest()

    # Guardar archivo físico en ./evidencias/
    nombre_limpio = Path(archivo).name
    file_path = EVIDENCIAS_PATH / f"{evidencia_id}_{nombre_limpio}"
    file_path.write_bytes(contenido_bytes)

    print("\n" + "-"*40)
    print(f"📦 [MCP Evidencias Mock - S3/Storage] Evidencia almacenada:")
    print(f"ID: {evidencia_id} | Control: {control_iso} | Path: {file_path}")
    print(f"SHA-256: {hash_sha256}")
    print("-"*40 + "\n")

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO evidencias (id, user_id, tipo, control_iso, archivo_url, hash_sha256, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (evidencia_id, user_id, "certificado_pdf" if "pdf" in archivo.lower() else "documento", control_iso, str(file_path), hash_sha256, now)
        )

    registrar_audit(
        user_id=user_id,
        accion="evidencia_guardar_mock",
        detalle={"evidencia_id": evidencia_id, "control_iso": control_iso, "hash": hash_sha256}
    )

    return {
        "status": "success",
        "evidencia_id": evidencia_id,
        "archivo_url": str(file_path),
        "hash_sha256": hash_sha256,
        "timestamp": now
    }
