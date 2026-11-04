# Guía Grupo 7 — Agente de Controles y SoA

Tiempo sugerido: **6–8 min**.

## 1–2. Objetivo y responsabilidad
Generar la Declaración de Aplicabilidad (SoA) y verificar controles del Anexo A de ISO/IEC 27701 según el rol de la organización (responsable, encargada o ambos).

## 3. Arquitectura original
Aplicación Flask (`tif-pims-controles/app.py`), motor `agents/controles.py` (reglas deterministas), `rag.py` (FAISS con embeddings por `/api/embed`), `ollama_client.py`, base `knowledge/`, exportación a Word (`exportar_soa_docx.py`) e interfaz estática en `static/`.

## 4. Skills
`generar-soa` y `verificar-controles`. API: `GET /api/controles/catalogo`, `POST /api/controles/ejecutar` (operaciones `generar_soa`, `verificar_control`, `consultar`), `POST /api/controles/exportar-docx`.

## 5–6. Flujo
Entrada con perfil (rol, organización), riesgos y evidencias → motor de reglas: los controles `A.3` aplican a todos; `A.1` solo si es responsable; `A.2` solo si es encargada → estado de implementación según evidencias → el modelo redacta un **análisis ejecutivo** (la parte de reglas no depende del modelo).

## 7. Demostración
`/agentes/controles` → "Generar SoA" con rol *responsable* para UNSA (datos de demostración). Resultado real: **9 controles aplicables, 0 % implementados**, nivel de madurez «inicial o inexistente», con análisis ejecutivo generado por el gateway. También "Ver catálogo de controles".

## 8. Ejemplo
Entrada: `{operacion: generar_soa, perfil: {rol, organizacion}, riesgos: [], evidencias: []}`. Salida: `datos`, `estado`, `confianza`, `requiere_revision_humana`, `fuentes`, `respuesta`.

## 9. Original frente a integrada
La interfaz original de `static/` y la exportación a Word siguen en su carpeta. La integrada ejecuta generar SoA y muestra el catálogo; el `.docx` sigue en la original.

## 10. Gateway LLM
Por las variables que el agente ya lee: `OLLAMA_URL`, `OLLAMA_MODEL`, `OLLAMA_EMBED_MODEL`, `OLLAMA_TIMEOUT`, apuntando al gateway. El gateway traduce `/api/generate` y `/api/embed` a la nube, **con lo que se conserva su RAG**. Con Ollama real habrá que revisar el tamaño de los vectores.

## 11. PostgreSQL
Sin uso de Gestitel. `core_annexacontrol` y `core_riskcontrol*` serían el destino natural; queda como paso opcional.

## 12. Otros agentes
Cada control del catálogo nombra un agente responsable (por ejemplo A.1.2.2 → Inventario, A.1.2.7 → Terceros, A.1.3.7 → Derechos). G8 le sugeriría controles tras un incidente; G4 le comparte la SoA. Transporte automático: no implementado.

## 13. Problemas y soluciones
- `exportar_soa_docx.py` importa `python-docx` sin declararlo en `requirements.txt` → se instala en la imagen.
- Su tiempo límite por defecto (20 s) es corto para la nube → se pasa `OLLAMA_TIMEOUT` por entorno.
- Flask arranca en modo `debug`: aceptable en demo, no en producción.

## 14. Guion
"Nuestro agente decide qué controles aplican con reglas explícitas y deja al modelo la redacción del análisis. Para una universidad como responsable del tratamiento aplican nueve controles; sin evidencias, la madurez es inicial."

## 15. Preguntas probables
- *¿El modelo decide la aplicabilidad?* No; son reglas deterministas.
- *¿Qué cambia con Ollama?* El modelo y los embeddings; el RAG requiere los mismos vectores en indexación y consulta.
- *¿Dónde queda la SoA?* En la respuesta y en el `.docx` de su interfaz original.

## 16. Conclusiones
Integración por variables de entorno únicamente; reglas y conocimiento intactos.
