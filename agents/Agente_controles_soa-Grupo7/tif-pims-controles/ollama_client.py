"""
Cliente local de Ollama para el Agente de Controles PIMS.

Se comunica con la API REST de Ollama (http://localhost:11434)
para generar respuestas enriquecidas con IA generativa local.
"""

import json
import os
import time
import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "20"))

# Prompt del sistema para el agente de controles con blindaje normativo
SYSTEM_PROMPT = """\
Eres un auditor y consultor experto en sistemas de gestión de privacidad \
de la información (PIMS) según la norma ISO/IEC 27701:2025 y la Ley N° 29733 (Perú) \
para la Universidad Nacional de San Agustín de Arequipa (UNSA).

GLOSARIO NORMATIVO CRÍTICO (REGLAS CONCEPTUALES ESTRICTAS):
1. SoA (Statement of Applicability): Es exclusivamente la "Declaración de Aplicabilidad" \
(Cláusula 6.1.3 d de ISO/IEC 27701:2025). Es el documento oficial que identifica los controles del \
Anexo A aplicables a la organización, justifica su inclusión o exclusión por rol (Responsable A.1 / \
Encargado A.2) y refleja su estado de implementación. BAJO NINGUNA CIRCUNSTANCIA confundas SoA \
con DSAR, ni con solicitudes de acceso, ni con derechos de los titulares.
2. DSAR (Data Subject Access Request) / Derechos ARCO: Son las solicitudes individuales que presentan los \
titulares de datos (acceso, rectificación, cancelación, oposición) ante la UNSA (odp@unsa.edu.pe).
3. DPIA: Evaluación de Impacto en la Privacidad (Privacy Impact Assessment, control A.1.2.6).
4. RAT: Registro de Actividades de Tratamiento de datos personales (control A.1.2.9).
5. Rol PII Controller: Responsable del tratamiento (UNSA respecto a estudiantes, docentes, notas).
6. Rol PII Processor: Encargado del tratamiento (procesa datos por encargo de terceros).

INSTRUCCIONES DE RESPUESTA:
- Responde siempre con precisión técnica y apego riguroso al estándar ISO/IEC 27701:2025.
- Si el usuario consulta sobre el SoA, define con claridad la Declaración de Aplicabilidad de controles.
- Cita las directivas y controles pertinentes sin inventar términos ni atribuir derechos al SoA.
- Responde en español formal, estructurado y conciso.\
"""


def _disponible():
    """Verifica si el servidor Ollama está activo."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def generar(prompt, system=None, temperature=0.3, max_tokens=1024, retornar_metricas=False):
    """
    Genera una respuesta usando Ollama.

    Devuelve el texto generado (o dict con métricas si retornar_metricas=True)
    o None si Ollama no está disponible.
    """
    if not _disponible():
        return None

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system or SYSTEM_PROMPT,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }

    t0 = time.time()
    print(f"\033[96m[OLLAMA {OLLAMA_MODEL}]\033[0m 🚀 Inferencia local iniciada (max_tokens={max_tokens})...")
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=OLLAMA_TIMEOUT,
        )
        if resp.status_code == 200:
            data = resp.json()
            texto = data.get("response", "").strip()
            eval_count = data.get("eval_count", 0)
            eval_dur_ns = data.get("eval_duration", 1)
            t_seg = round(time.time() - t0, 2)
            tps = round(eval_count / (eval_dur_ns / 1e9), 1) if eval_dur_ns > 0 else 0
            print(f"\033[92m[OLLAMA {OLLAMA_MODEL}]\033[0m ✅ Inferencia completada en {t_seg}s ({eval_count} tokens a {tps} tok/s).")
            if retornar_metricas:
                return {
                    "texto": texto,
                    "prompt": prompt,
                    "modelo": OLLAMA_MODEL,
                    "tokens": eval_count,
                    "velocidad_tps": tps,
                    "tiempo_seg": t_seg
                }
            return texto
    except Exception as e:
        print(f"\033[91m[OLLAMA ERROR]\033[0m Error durante inferencia: {e}")

    return None


def enriquecer_consulta_rag(consulta, fragmentos_rag):
    """
    Dado una consulta del usuario y los fragmentos recuperados por FAISS,
    genera una respuesta elaborada en lenguaje natural usando la IA.
    """
    if not fragmentos_rag:
        return None

    contexto = "\n\n---\n\n".join(
        f"[Fuente: {h['meta']}]\n{h['texto']}" for h in fragmentos_rag
    )

    prompt = f"""\
Contexto normativo recuperado de la base de conocimiento institucional:

{contexto}

---

Consulta del auditor: {consulta}

Instrucciones:
- Responde la consulta directamente en 1 o 2 párrafos concisos y bien estructurados.
- Basa tu respuesta en el contexto normativo proporcionado y menciona las directivas aplicables.
- Si no hay información suficiente en el contexto, indícalo de forma clara.
"""
    return generar(prompt, max_tokens=250)


def enriquecer_soa(soa_filas, resumen, organizacion, rol):
    """
    Genera un análisis ejecutivo de la SoA usando IA.
    """
    # Preparar resumen de brechas para el prompt
    brechas = [f for f in soa_filas if f["aplica"] and f["estado"] != "implementado"]
    brechas_texto = "\n".join(
        f"- {b['control']} ({b['nombre']}): estado '{b['estado']}'"
        for b in brechas
    ) or "No se identificaron brechas."

    implementados_texto = "\n".join(
        f"- {f['control']} ({f['nombre']})"
        for f in soa_filas if f["estado"] == "implementado"
    ) or "Ningún control implementado."

    prompt = f"""\
Se ha generado la Declaración de Aplicabilidad (SoA) ISO/IEC 27701:2025 para:
- Organización: {organizacion}
- Rol: {rol}

Resumen cuantitativo:
- Controles evaluados: {resumen['controles_evaluados']}
- Controles aplicables: {resumen['aplican']}
- Implementados: {resumen['implementados']}
- Parciales: {resumen['parciales']}
- No implementados (brechas): {resumen['no_implementados']}
- Excluidos: {resumen['excluidos']}

Controles implementados:
{implementados_texto}

Brechas identificadas:
{brechas_texto}

Genera un ANÁLISIS EJECUTIVO breve (máx. 150 palabras) que:
1. Resuma el nivel de madurez de privacidad de la organización.
2. Destaque las brechas más críticas y su impacto potencial.
3. Proponga las 2-3 acciones prioritarias inmediatas.
Responde en español profesional.
"""
    return generar(prompt, max_tokens=512, retornar_metricas=True)


def enriquecer_verificacion(fila_control):
    """
    Genera una recomendación detallada para un control individual usando IA.
    """
    evidencias_texto = "\n".join(
        f"  - {e}" for e in fila_control.get("evidencias", [])
    ) or "  (Sin evidencias registradas)"

    prompt = f"""\
Control auditado: {fila_control['control']} - {fila_control['nombre']}
¿Aplica?: {'Sí' if fila_control['aplica'] else 'No'}
Justificación: {fila_control['justificacion']}
Estado actual: {fila_control['estado']}
Evidencias presentadas:
{evidencias_texto}
Política relacionada: {fila_control.get('politica_relacionada', 'No identificada')}
Agente responsable: {fila_control['responsable']}

Genera una RECOMENDACIÓN TÉCNICA DETALLADA (máx. 100 palabras) que:
1. Evalúe la suficiencia de las evidencias presentadas.
2. Indique acciones concretas para alcanzar el cumplimiento pleno.
3. Cite las cláusulas relevantes de ISO/IEC 27701:2025.
Responde en español profesional.
"""
    return generar(prompt, max_tokens=300)


def esta_disponible():
    """Interfaz pública para verificar disponibilidad de Ollama."""
    return _disponible()
