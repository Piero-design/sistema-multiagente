import os
from pathlib import Path

# Cargar variables de entorno desde .env de forma resiliente
env_path = Path(__file__).resolve().parent / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

# Rutas del sistema
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("DB_PATH", str(BASE_DIR / "agente.db"))).resolve()
CHROMA_PATH = Path(os.getenv("CHROMA_PATH", str(BASE_DIR / "chroma_db"))).resolve()
EVIDENCIAS_PATH = Path(os.getenv("EVIDENCIAS_PATH", str(BASE_DIR / "evidencias"))).resolve()
KNOWLEDGE_BASE_PATH = BASE_DIR.parent / "knowledge_base"

# JWT y Seguridad
JWT_SECRET = os.getenv("JWT_SECRET", "unsa_pims_secret_key_demo_2025_academico")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "8"))

# Proveedor de LLM (openrouter u ollama)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter").lower()

# Configuración OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
raw_model = os.getenv("OPENROUTER_MODEL", "openrouter/auto").strip()

# Limpieza defensiva en caso de duplicar el nombre de variable o comillas
if "OPENROUTER_MODEL=" in raw_model:
    raw_model = raw_model.replace("OPENROUTER_MODEL=", "").strip()
raw_model = raw_model.strip("\"' ")

OPENROUTER_MODEL = raw_model
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# Configuración Ollama
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

# Configuración SMTP para despacho real de correos (Gmail / UNSA)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "jchuraaca@unsa.edu.pe").strip()

# Despacho moderno vía Resend API (Directo a Gmail sin contraseñas de app)
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "").strip()

# Asegurar directorios esenciales
EVIDENCIAS_PATH.mkdir(parents=True, exist_ok=True)
CHROMA_PATH.mkdir(parents=True, exist_ok=True)
(KNOWLEDGE_BASE_PATH / "normas").mkdir(parents=True, exist_ok=True)
(KNOWLEDGE_BASE_PATH / "politicas").mkdir(parents=True, exist_ok=True)
