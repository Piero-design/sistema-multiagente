from typing import TypedDict, Optional, List, Dict, Any
from langchain_core.messages import BaseMessage

class PIMSState(TypedDict):
    """
    Estado del grafo LangGraph para el Agente #8 PIMS UNSA.
    """
    messages: List[BaseMessage]
    user_id: str
    user_rol: str
    user_facultad: Optional[str]
    conversacion_id: Optional[str]
    intent: str  # consulta_estado, consulta_normativa, consulta_usuarios, accion_individual, accion_masiva, fuera_de_alcance
    rag_context: List[str]
    tool_name: Optional[str]
    tool_args: Optional[Dict[str, Any]]
    tool_result: Optional[Dict[str, Any]]
    pending_action: Optional[Dict[str, Any]]   # Acción preparada esperando confirmación
    requires_approval: bool
    approved: Optional[bool]
    skill_content: Optional[str]               # Especificación activa leída dinámicamente de SKILL.md
