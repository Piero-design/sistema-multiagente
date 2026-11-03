import uuid
import logging
from datetime import datetime
from db import get_db_connection, registrar_audit

logger = logging.getLogger("mcp_lms")

def matricular(user_id: str, curso_id: str) -> dict:
    """
    MCP LMS (Mock persistente):
    Inserta en `matriculas_lms_mock`, imprime payload en consola
    y registra en `audit_log` con accion='lms_matricular_mock'.
    """
    matricula_id = f"mat_{uuid.uuid4().hex[:10]}"
    now = datetime.now().isoformat()

    print("\n" + "-"*40)
    print(f"[MCP LMS Mock] Matriculando en LMS Moodle UNSA:")
    print(f"Usuario ID: {user_id} | Curso ID: {curso_id} | Matrícula ID: {matricula_id}")
    print("-"*40 + "\n")

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO matriculas_lms_mock (id, user_id, curso_id, matriculado_at, estado)
            VALUES (?, ?, ?, ?, ?)
            """,
            (matricula_id, user_id, curso_id, now, "inscrito")
        )

    registrar_audit(
        user_id=user_id,
        accion="lms_matricular_mock",
        detalle={"matricula_id": matricula_id, "curso_id": curso_id, "estado": "inscrito"}
    )

    return {
        "status": "success",
        "matricula_id": matricula_id,
        "user_id": user_id,
        "curso_id": curso_id,
        "estado": "inscrito",
        "timestamp": now
    }
