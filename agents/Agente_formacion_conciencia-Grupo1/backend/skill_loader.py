import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("skill_loader")

# Ruta al archivo SKILL.md en .agents/skills/formacion-conciencia-iso27701/SKILL.md
BASE_DIR = Path(__file__).resolve().parent
SKILL_PATH = BASE_DIR.parent / ".agents" / "skills" / "formacion-conciencia-iso27701" / "SKILL.md"

def cargar_skill_definicion(ruta: Optional[Path] = None) -> str:
    """
    Lee físicamente en tiempo de ejecución el archivo SKILL.md
    y lo retorna como string para inyectarlo en el pipeline del Agente LangGraph.
    """
    target = ruta or SKILL_PATH
    if not target.exists():
        logger.warning(f"Archivo de Skill no encontrado en: {target}")
        return ""

    try:
        with open(target, "r", encoding="utf-8") as f:
            contenido = f.read()
        logger.info(f"[SKILL LOADER] Skill cargado exitosamente desde: {target.name} ({len(contenido)} bytes)")
        print(f"\n[SKILL LOADER] -> Leyendo Skill activo: {target}")
        return contenido
    except Exception as e:
        logger.error(f"Error leyendo SKILL.md en {target}: {e}")
        return ""

# Carga inicial disponible para módulos del sistema
SKILL_CONTENT = cargar_skill_definicion()
