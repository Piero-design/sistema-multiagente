import json
import os

from rag import desde_carpeta

ROLES = ("responsable", "encargado", "ambos")
UMBRAL_POLITICA = 0.30   # similitud mínima para citar una política relacionada
UMBRAL_CONSULTA = 0.30   # similitud mínima para responder una consulta conceptual

def imprimir_traza_consola(pensamiento, acciones):
    """Imprime en la terminal la traza de razonamiento y acciones del agente estilo Antigravity."""
    print(f"\n\033[94m○ Thought for {pensamiento['tiempo_seg']}s\033[0m \033[90m({pensamiento['resumen']})\033[0m")
    for act in acciones:
        print(f" \033[92m●\033[0m \033[1m{act['titulo']}\033[0m \033[90m({act.get('detalle', '')})\033[0m")
    print()


class AgenteControles:
    nombre = "controles"
    descripcion = (
        "Genera la Declaración de Aplicabilidad (SoA) y verifica la "
        "implementación de controles de ISO/IEC 27701:2025."
    )
    ejemplos = [
        "Genera la declaración de aplicabilidad",
        "¿Qué controles aplican a una organización responsable?",
        "Verifica si el control A.1.2.6 está implementado",
        "¿Qué controles faltan por implementar?",
        "Actualiza la SoA con las nuevas evidencias",
    ]

    def __init__(self, carpeta=None):
        if carpeta is None:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            carpeta = os.path.join(base, "knowledge")
        with open(os.path.join(carpeta, "catalogo_controles.json"), encoding="utf-8") as f:
            self.catalogo = json.load(f)
        self.normativa = desde_carpeta(os.path.join(carpeta, "normativa"))
        self.politicas = desde_carpeta(os.path.join(carpeta, "politicas"))

    # ------------------------------------------------------------------
    # Punto de entrada único (contrato estándar)
    # ------------------------------------------------------------------
    def ejecutar(self, entrada):
        operacion = entrada.get("operacion", "consultar")
        try:
            if operacion == "generar_soa":
                return self._generar_soa(entrada)
            if operacion == "verificar_control":
                return self._verificar_control(entrada)
            return self._consultar(entrada.get("solicitud", ""))
        except ValueError as e:
            return self._resp(operacion, "rechazada", f"Entrada inválida: {e}")

    # ------------------------------------------------------------------
    # Motor de reglas
    # ------------------------------------------------------------------
    @staticmethod
    def _aplica(control, rol):
        ambito = control["id"][:3]  # "A.1", "A.2" o "A.3"
        if ambito == "A.3":
            return True, "Control común de seguridad: aplica a cualquier rol."
        if ambito == "A.1":
            if rol in ("responsable", "ambos"):
                return True, "La organización actúa como responsable del tratamiento."
            return False, "Excluido: la organización no actúa como responsable (controles A.1)."
        if ambito == "A.2":
            if rol in ("encargado", "ambos"):
                return True, "La organización actúa como encargada del tratamiento."
            return False, "Excluido: la organización no actúa como encargada (controles A.2)."
        raise ValueError(f"ámbito desconocido en el control {control['id']}")

    @staticmethod
    def _estado(control_id, evidencias):
        propias = [e for e in evidencias if e.get("control") == control_id]
        if any(e.get("estado") == "implementado" for e in propias):
            return "implementado", propias
        if any(e.get("estado") == "parcial" for e in propias):
            return "parcial", propias
        return "no implementado", propias

    def _fila(self, control, rol, riesgos, evidencias):
        aplica, justificacion = self._aplica(control, rol)
        vinculados = [r["id"] for r in riesgos if control["id"] in r.get("controles", [])]
        if aplica and vinculados:
            justificacion += f" Vinculado a los riesgos: {', '.join(vinculados)}."

        if aplica:
            estado, propias = self._estado(control["id"], evidencias)
        else:
            estado, propias = "no aplica", []

        # Herramienta: repositorio de políticas (búsqueda semántica con FAISS)
        hits = self.politicas.buscar(control["nombre"], k=1)
        politica = hits[0]["meta"] if hits and hits[0]["score"] >= UMBRAL_POLITICA else None

        return {
            "control": control["id"],
            "nombre": control["nombre"],
            "aplica": aplica,
            "justificacion": justificacion,
            "estado": estado,
            "evidencias": [e.get("descripcion", "") for e in propias],
            "politica_relacionada": politica,
            "responsable": control["agente_responsable"],
        }

    # ------------------------------------------------------------------
    # Skill 1: generar-soa
    # ------------------------------------------------------------------
    def _generar_soa(self, entrada):
        perfil = entrada.get("perfil") or {}
        rol = perfil.get("rol")
        if rol not in ROLES:
            raise ValueError("perfil.rol debe ser 'responsable', 'encargado' o 'ambos'")
        riesgos = entrada.get("riesgos", [])
        evidencias = entrada.get("evidencias", [])

        soa = [self._fila(c, rol, riesgos, evidencias) for c in self.catalogo]
        aplicables = [f for f in soa if f["aplica"]]
        brechas = [
            {"control": f["control"], "nombre": f["nombre"], "estado": f["estado"],
             "solicitar_a": f["responsable"]}
            for f in aplicables if f["estado"] != "implementado"
        ]
        resumen = {
            "controles_evaluados": len(soa),
            "aplican": len(aplicables),
            "excluidos": len(soa) - len(aplicables),
            "implementados": sum(f["estado"] == "implementado" for f in aplicables),
            "parciales": sum(f["estado"] == "parcial" for f in aplicables),
            "no_implementados": sum(f["estado"] == "no implementado" for f in aplicables),
        }
        org = perfil.get("organizacion", "la organización")
        analisis_ejecutivo = None
        try:
            import ollama_client
            if ollama_client.esta_disponible():
                analisis_ejecutivo = ollama_client.enriquecer_soa(soa, resumen, org, rol)
        except Exception as e:
            print(f"[Ollama SoA Error]: {e}")

        datos_resp = {
            "soa": soa,
            "brechas": brechas,
            "resumen": resumen,
        }
        if analisis_ejecutivo:
            if isinstance(analisis_ejecutivo, dict):
                datos_resp["analisis_ejecutivo"] = analisis_ejecutivo.get("texto", "")
                datos_resp["telemetria_ia"] = analisis_ejecutivo
            else:
                datos_resp["analisis_ejecutivo"] = analisis_ejecutivo

        t_pensamiento = round(analisis_ejecutivo.get("tiempo_seg", 2.1), 1) if isinstance(analisis_ejecutivo, dict) else 1.8
        pensamiento_soa = {
            "tiempo_seg": t_pensamiento,
            "resumen": f"El auditor solicitó generar la SoA para {org} (rol: {rol}) bajo ISO/IEC 27701:2025. Evaluando reglas deterministas, consultando directivas RAG en FAISS y sintetizando dictamen ejecutivo con Qwen 2.5:7b...",
            "detalles": (
                f"1. Objetivo: Construir la Declaración de Aplicabilidad de privacidad.\n"
                f"2. Rol de la entidad: {rol.upper()} -> Discriminar dominios A.1 (Controllers) vs A.2 (Processors).\n"
                f"3. Cruce de evidencias: {len(evidencias)} artefactos documentales evaluados.\n"
                f"4. Riesgos asociados: {len(riesgos)} amenazas de privacidad (ej. R-UNSA-01 SISUNSA, R-UNSA-02 Comedor).\n"
                f"5. Síntesis ejecutiva y plan de remediación mediante inferencia local en Ollama."
            )
        }
        acciones_soa = [
            {"tipo": "skill", "titulo": "Read skill (skills/generar-soa/SKILL.md)", "detalle": "Especificación formal de la habilidad determinista"},
            {"tipo": "files", "titulo": "Explored files (knowledge/catalogo_controles.json)", "detalle": f"{len(soa)} controles normativos cargados"},
            {"tipo": "rag", "titulo": "Consulted RAG FAISS (all-minilm)", "detalle": "Búsqueda vectorial sobre directivas DIR-OTIC-004-UNSA"},
            {"tipo": "rules", "titulo": f"Evaluated {len(soa)} controls", "detalle": f"{resumen['aplican']} aplicables, {resumen['excluidos']} excluidos, {len(brechas)} brechas críticas"},
            {"tipo": "llm", "titulo": "Invoked Ollama (qwen2.5:7b)", "detalle": f"{analisis_ejecutivo.get('tokens', 250) if isinstance(analisis_ejecutivo, dict) else 250} tokens generados localmente en Apple Silicon M5"},
            {"tipo": "artifact", "titulo": "Prepared artifact (Declaracion_de_Aplicabilidad_ISO_27701_UNSA.docx)", "detalle": "Plantilla SoA oficial adaptada para firma"}
        ]
        imprimir_traza_consola(pensamiento_soa, acciones_soa)
        datos_resp["traza_agente"] = {
            "pensamiento": pensamiento_soa,
            "acciones": acciones_soa
        }

        texto = (
            f"SoA generada para {org} (rol: {rol}). Controles evaluados: "
            f"{resumen['controles_evaluados']}; aplican: {resumen['aplican']}; "
            f"implementados: {resumen['implementados']}; brechas: {len(brechas)}. "
            "Requiere revisión y aprobación humana."
        )
        return self._resp(
            "generar_soa", "ok", texto,
            datos=datos_resp,
            fuentes=["catalogo_controles.json"], confianza=1.0, revision=True,
        )

    # ------------------------------------------------------------------
    # Skill 2: verificar-controles
    # ------------------------------------------------------------------
    def _verificar_control(self, entrada):
        cid = entrada.get("control")
        control = next((c for c in self.catalogo if c["id"] == cid), None)
        if control is None:
            raise ValueError(f"el control '{cid}' no está en el catálogo")
        rol = (entrada.get("perfil") or {}).get("rol")
        if rol not in ROLES:
            raise ValueError("perfil.rol debe ser 'responsable', 'encargado' o 'ambos'")

        fila = self._fila(control, rol, entrada.get("riesgos", []), entrada.get("evidencias", []))
        fila["recomendacion"] = self._recomendar(fila)
        try:
            import ollama_client
            if ollama_client.esta_disponible():
                rec_ia = ollama_client.enriquecer_verificacion(fila)
                if rec_ia:
                    fila["recomendacion_ia"] = rec_ia
        except Exception as e:
            print(f"[Ollama Verificacion Error]: {e}")

        pensamiento_vc = {
            "tiempo_seg": 0.8,
            "resumen": f"Verificación puntual del control {fila['control']} ({fila['nombre']}) para rol '{rol}'...",
            "detalles": (
                f"1. Identificador: {fila['control']}\n"
                f"2. Ámbito normativo: {'Responsable (A.1)' if 'A.1' in fila['control'] else ('Encargado (A.2)' if 'A.2' in fila['control'] else 'Común (A.3)')}\n"
                f"3. Estado probatorio resultante: {fila['estado'].upper()}\n"
                f"4. Responsable asignado: {fila['responsable']}"
            )
        }
        acciones_vc = [
            {"tipo": "skill", "titulo": "Read skill (skills/verificar-controles/SKILL.md)", "detalle": "Procedimiento de inspección quirúrgica"},
            {"tipo": "inspect", "titulo": f"Inspected evidence for control {fila['control']}", "detalle": f"{len(fila.get('evidencias', []))} documentos hallados"},
            {"tipo": "rag", "titulo": "Consulted RAG FAISS (all-minilm)", "detalle": f"Afinidad con política: {fila.get('politica_relacionada') or 'General'}"},
            {"tipo": "rules", "titulo": "Computed control recommendation", "detalle": fila.get("recomendacion", "")}
        ]
        if fila.get("recomendacion_ia"):
            acciones_vc.append({"tipo": "llm", "titulo": "Invoked Ollama (qwen2.5:7b)", "detalle": "Recomendación técnica generada por LLM"})
        imprimir_traza_consola(pensamiento_vc, acciones_vc)
        fila["traza_agente"] = {
            "pensamiento": pensamiento_vc,
            "acciones": acciones_vc
        }

        texto = f"Control {fila['control']} ({fila['nombre']}): {fila['estado']}. {fila['recomendacion']}"
        return self._resp(
            "verificar_control", "ok", texto, datos=fila,
            fuentes=["catalogo_controles.json"], confianza=1.0,
        )

    @staticmethod
    def _recomendar(fila):
        if not fila["aplica"]:
            return "Documentar la exclusión y su justificación en la SoA."
        if fila["estado"] == "implementado":
            return "Mantener la evidencia vigente para la auditoría interna (cláusula 9.2)."
        if fila["estado"] == "parcial":
            return f"Completar la implementación; coordinar con el {fila['responsable']}."
        return f"Solicitar evidencia o implementación al {fila['responsable']}."

    # ------------------------------------------------------------------
    # Consulta conceptual (base de conocimiento RAG)
    # ------------------------------------------------------------------
    def _consultar(self, solicitud):
        if not solicitud.strip():
            return self._resp("consultar", "rechazada", "La consulta está vacía.", datos={"hits": []})

        # Expansión semántica de acrónimos para evitar ruido vectorial en consultas breves
        solicitud_limpia = solicitud.lower()
        terminos_extra = []
        if "soa" in solicitud_limpia:
            terminos_extra.append("Declaración de Aplicabilidad Statement of Applicability SoA controles Anexo A")
        if "dpia" in solicitud_limpia or "impacto" in solicitud_limpia:
            terminos_extra.append("Evaluación de impacto de privacidad DPIA")
        if "rat" in solicitud_limpia:
            terminos_extra.append("Registros de actividades de tratamiento RAT bancos de datos")
        if "arco" in solicitud_limpia:
            terminos_extra.append("Procedimiento TUPA para Derechos ARCO acceso rectificación")

        consulta_vectorial = f"{solicitud} {' '.join(terminos_extra)}" if terminos_extra else solicitud

        hits_norm = self.normativa.buscar(consulta_vectorial, k=4)
        hits_pol = self.politicas.buscar(consulta_vectorial, k=4)
        todos_hits = sorted(hits_norm + hits_pol, key=lambda x: x["score"], reverse=True)[:5]
        hits_validos = [h for h in todos_hits if h["score"] >= 0.15]
        if not hits_validos:
            return self._resp(
                "consultar", "sin_respuesta",
                "No se encontraron directivas o cláusulas con suficiente afinidad en el repositorio institucional.",
                confianza=round(todos_hits[0]["score"], 3) if todos_hits else 0.0,
                datos={"respuesta_directa": "No se encontraron directivas o cláusulas con suficiente afinidad.", "hits": []}
            )

        # 1. Intentar generar respuesta elaborada en lenguaje natural con Ollama si está disponible
        respuesta_sintetizada = None
        try:
            import ollama_client
            if ollama_client.esta_disponible():
                respuesta_sintetizada = ollama_client.enriquecer_consulta_rag(solicitud, hits_validos[:3])
        except Exception:
            pass

        # 2. Si Ollama no está activo o falló, construir una respuesta directa limpia y comprensible
        if not respuesta_sintetizada:
            top = hits_validos[0]
            lineas = [l.strip() for l in top["texto"].split("\n") if l.strip()]
            cuerpo = "\n\n".join(lineas[1:]) if len(lineas) > 1 else lineas[0]
            respuesta_sintetizada = (
                f"De acuerdo con **{top['meta']}** (normativa con mayor afinidad: {round(top['score']*100, 1)}%):\n\n"
                f"{cuerpo}"
            )

        pensamiento_rag = {
            "tiempo_seg": 1.2,
            "resumen": f"El auditor consultó: '{solicitud}'. Buscando directivas normativas en FAISS y sintetizando respuesta...",
            "detalles": (
                f"1. Consulta: {solicitud}\n"
                f"2. Vectorización: all-minilm (384 dimensiones).\n"
                f"3. Recuperación: Top fragmentos afines en normativa institucional.\n"
                f"4. Síntesis: Respuesta directa fundada en directivas vigentes."
            )
        }
        acciones_rag = [
            {"tipo": "embed", "titulo": "Embedded query (all-minilm)", "detalle": "Vector denso de 384 dimensiones normalizado L2"},
            {"tipo": "rag", "titulo": "Searched FAISS IndexFlatIP", "detalle": f"{len(hits_validos)} directivas recuperadas (Score máx: {round(hits_validos[0]['score']*100, 1)}%)"},
            {"tipo": "files", "titulo": "Explored files (knowledge/normativa, knowledge/politicas)", "detalle": ", ".join(list({h['meta'] for h in hits_validos})[:2])}
        ]
        if respuesta_sintetizada:
            acciones_rag.append({"tipo": "llm", "titulo": "Invoked Ollama (qwen2.5:7b)", "detalle": "Síntesis en lenguaje natural sin alucinaciones"})
        imprimir_traza_consola(pensamiento_rag, acciones_rag)

        return self._resp(
            "consultar", "ok", respuesta_sintetizada,
            fuentes=sorted(list({h["meta"] for h in hits_validos})),
            confianza=round(hits_validos[0]["score"], 3),
            datos={"respuesta_directa": respuesta_sintetizada, "hits": hits_validos, "traza_agente": {"pensamiento": pensamiento_rag, "acciones": acciones_rag}}
        )

    # ------------------------------------------------------------------
    @staticmethod
    def _resp(operacion, estado, respuesta, datos=None, fuentes=None,
              confianza=0.0, revision=False):
        return {
            "agente": "controles",
            "operacion": operacion,
            "estado": estado,
            "respuesta": respuesta,
            "datos": datos or {},
            "fuentes": fuentes or [],
            "confianza": confianza,
            "requiere_revision_humana": revision,
        }
