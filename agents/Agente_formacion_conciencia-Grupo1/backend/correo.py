import logging
from typing import List, Dict, Any, Optional
from mcp_externos.correo_mock import enviar_correo

logger = logging.getLogger("correo")

def despachar_correo(
    destinatarios: List[Dict[str, Any] | str],
    asunto: str,
    cuerpo: str,
    remitente_id: str = "admin",
    lote_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Despacha correos utilizando el conector MCP Correo (con persistencia en SQLite).
    """
    logger.info(f"Despachando correo para {len(destinatarios)} destinatarios con asunto '{asunto}'")
    resultado = enviar_correo(
        destinatarios=destinatarios,
        asunto=asunto,
        cuerpo=cuerpo,
        remitente_id=remitente_id,
        lote_id=lote_id
    )
    return resultado
