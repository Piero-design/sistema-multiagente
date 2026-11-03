import logging
from db import registrar_audit

logger = logging.getLogger("mcp_postgres")

# Datos sintéticos representativos del sistema legado de la UNSA
DATOS_LEGADOS_PII = [
    {"codigo_unsa": "20201234", "tipo_titular": "estudiante", "categoria_datos": "académico, biométrico", "medidas_seguridad": "cifrado en reposo"},
    {"codigo_unsa": "DOC-9921", "tipo_titular": "docente", "categoria_datos": "bancario, antecedentes, contrato", "medidas_seguridad": "control de acceso estricto"},
    {"codigo_unsa": "ADM-4432", "tipo_titular": "administrativo", "categoria_datos": "legajo personal, planillas", "medidas_seguridad": "backup diario cifrado"},
]

def consultar_pii(query: str) -> dict:
    """
    MCP PostgreSQL Org. (Mock persistente de lectura):
    Devuelve datos mock predefinidos sobre categorías de datos personales (PII)
    en las bases de datos de la UNSA y registra la consulta en audit_log.
    """
    print(f"\n🔍 [MCP PostgreSQL Org. Mock] Consulta de inventario PII: '{query}'")

    resultado = [
        item for item in DATOS_LEGADOS_PII
        if query.lower() in item["tipo_titular"] or query.lower() in item["categoria_datos"]
    ]
    if not resultado:
        resultado = DATOS_LEGADOS_PII

    registrar_audit(
        user_id="sistema",
        accion="postgres_consultar_pii_mock",
        detalle={"query": query, "registros_retornados": len(resultado)}
    )

    return {
        "status": "success",
        "query": query,
        "registros": resultado,
        "fuente": "Base de Datos Organizacional UNSA (Mock Legado)"
    }
