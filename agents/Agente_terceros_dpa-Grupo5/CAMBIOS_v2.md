# Cambios v1.1 → v2.0 (Etapas 1 a 4 e informe)

**Objetivo:** que la skill funcione para **cualquier organización y cualquier país** sin tocar sus reglas. Lo específico pasa a piezas intercambiables. La v1.1 queda intacta en `versiones/v1.1/`, porque es la que documenta la primera entrega del TIF (`informe_TIF.tex`).

## 1. Arquitectura en tres capas

| Capa | Dónde | ¿Cambia por…? |
|---|---|---|
| **Norma (ISO/IEC 27701:2025)**: 26 controles (24 hasta la sección 13c), criterios, puntaje | `pims-dpa-auditor/references/`, `scripts/` | Nada: es general |
| **Jurisdicción (país)**: ley, autoridad, plazos legales | `pims-dpa-auditor/jurisdicciones/<id>/` | País |
| **Organización**: política interna, aprobadores, perfil | `organizaciones/<id>/` | Organización |

## 2. Qué cambió en la skill `pims-dpa-auditor`

| Archivo | Cambio |
|---|---|
| `SKILL.md` | Nueva sección "Contexto de ejecución". El Paso 1 usa el perfil si existe; el Paso 2 aplica el nivel de riesgo más alto entre contrato y perfil; el Paso 5 lee la jurisdicción configurada. Regla 7 extendida a todos los documentos (contrato, perfil, documentos institucionales). **Regla 9 nueva: asimetría del contexto.** La descripción ya no está atada a Perú (958 caracteres, bajo el límite de 1024). Se mantienen las 11 secciones del informe. |
| `references/marco_legal_peru.md` | Movido a `jurisdicciones/peru/marco_legal.md`, con el mismo contenido y una tabla de estado. Se añade `parametros_legales.json`. |
| `jurisdicciones/_plantilla/` y `LEEME.md` | Plantilla para agregar países, con estados `Plantilla` → `Borrador` → `En uso` / `Verificada`. |
| `references/criterios_semaforo.md` | "Equivalente a la Ley 29733" pasa a "equivalente a la ley aplicable". En §1 se añade la regla del perfil. **Fórmulas y reglas sin cambios.** |
| `references/controles_iso27701_2025.md` | A.3.13 y "No aplica" redactados sin fijar el país. |
| `assets/plantilla_dpa_baseline.md` | `{ley_aplicable}`, `{reglamento}` y `{autoridad}` en lugar de la Ley 29733 y la ANPD fijas. |
| `assets/config_organizacion.json` | Pasa a ser la configuración **por defecto** (organización genérica). Añade `jurisdiccion` y `aprobadores_cargos`. Mismos valores de política. |
| `assets/esquema_salida.json` | Bloques opcionales `organizacion` y `jurisdiccion`; en `tercero`, `proceso_origen` y `fuente_perfil`. `fuente_requisito` acepta "Ley aplicable" y conserva "Ley 29733/Reglamento" por compatibilidad. En `trazabilidad`: versión de jurisdicción y de perfil, y advertencias. Ningún campo obligatorio nuevo, así que los registros v1.1 siguen siendo válidos. |
| `scripts/calcular_resultado.py` | Opciones `--org`, `--perfil` y `--jurisdicciones` (`--config` sigue funcionando). Carga y valida la jurisdicción, registra el perfil (versión, estado y SHA-256) y advierte si la política interna no deja margen para cumplir la ley. **El núcleo de cálculo es idéntico al de la v1.1.** Corregido el `−` (U+2212) que fallaba en consolas Windows. |

## 3. Skill nueva: `pims-perfilador-organizacion` (Agente 1, inventario)

Convierte los documentos institucionales de cualquier organización (ROF, MOF, TUPA, organigrama, procesos…) en un `perfil_organizacion.md` con **formato fijo de 8 secciones** y fuente `[Dn, p. X]` en cada dato.

- **Sin juicios de cumplimiento.** En la columna "¿DPA localizado?" solo se admite Sí, No o Desconocido.
- **El texto de los documentos es dato, no instrucción.** Las frases dirigidas a un evaluador van a la sección 8.
- **Sale en `Borrador`**, hasta que el DPO lo valida.
- `scripts/validar_perfil.py` comprueba el formato, la trazabilidad y la ausencia de juicios de cumplimiento. Su opción `--json` está pensada para n8n.

## 4. Organizaciones

`organizaciones/_plantilla/`, `inversiones_altiplano/` (la de los contratos de la v1.1) y `unsa/` (configuración **provisional**, sin documentos todavía). Ver `organizaciones/LEEME.md`.

## 5. Contenido no confiable y asimetría: defensa en tres niveles

1. **Perfilador:** no incorpora instrucciones de los documentos y las registra en la sección 8.
2. **Validador:** rechaza perfiles con juicios de cumplimiento o fuentes inexistentes.
3. **Auditor:** la regla 9 impide que el perfil cuente como evidencia. Además, **el script no deja que el perfil toque el cálculo**: una prueba demuestra que NubeAndina da 22/100 sin perfil, con perfil y con un perfil contaminado.

## 6. Pruebas

```
python pims-dpa-auditor_pruebas/ejecutar_pruebas.py
```

**28/28 correctas.** Cubren:

- **Regresión exacta contra la v1.1** sobre los 5 resultados guardados (22, 100, 0, 22 y 100).
- **Jurisdicciones:** estados, errores y selección de otro país.
- **Coherencia** de la política interna con la ley.
- **Perfil:** hash e inmunidad del cálculo.
- **Validador:** referencia válida; contaminado, plantilla, `D9` inexistente y fila sin fuente rechazados.
- **Compatibilidad:** config v1.1, consola cp1252 y entradas inválidas.
- **Rutas** de `casos_de_prueba.json`.

`casos_de_prueba.json` tiene las rutas corregidas y 4 casos nuevos (6–9) para probar con el modelo el perfil, la asimetría hacia arriba y hacia abajo, y el perfilador. **Esos 4 casos requieren ejecutar el modelo** y no forman parte de la suite automática.

## 7. Otros

- `demo/build_embed.py` lee la jurisdicción desde su nueva ubicación. `corpus.js` está regenerado, así que la demo actual sigue funcionando con la v2.0.
- Ambas skills pasan `skillkit lint --strict` con 100/100.

## 8. Etapa 2 — n8n como motor central

Detalle completo e instalación en **`n8n/INSTALACION_N8N.md`**.

| Pieza | Qué es |
|---|---|
| `n8n/construir_flujos.py` | Genera los **11 flujos** (162 nodos) desde una sola fuente, con la ruta del proyecto y las librerías JS embebidas. |
| `n8n/instalar_flujos.py` | Construye, importa y publica en n8n. Genera `iniciar_n8n.bat` / `.sh` con las variables que exige n8n 2.x. |
| `n8n/lib/calcular.js` | Port del cálculo de `calcular_resultado.py`. **Idéntico en 5 012 casos**, incluidos 476 empates de redondeo: Python redondea 22,5 → 22 y JavaScript con `Math.round` daría 23. |
| `n8n/lib/perfil.js` | Port de `validar_perfil.py`. **Idéntico en 1 503 perfiles.** |
| `n8n/lib/prompts.js` | Armado de prompts e inserción de las cifras calculadas en el informe (secciones 1, 6, 7, 10 y 11). |
| `n8n/pruebas/` | Modelo simulado (Ollama, Anthropic, OpenAI y `claude`), equivalencia JS = Python y 21 pruebas de extremo a extremo. |
| `datos/` | Registro de DPAs, trabajos en curso, configuración del modelo, alertas de renovación. |

Flujos: Auditar contrato · Perfilar organización · Aprobaciones (DPO → Legal) · Renovaciones (cada lunes) · Consultas · Administración · Modelo de IA (selector) · Leer y Guardar archivos · Claude Code y Crear carpetas (los únicos que usan *Execute Command*, aislados).

**Verificado en n8n 2.43.4 real** con el modelo simulado: **21/21 pruebas**, también en una segunda corrida sobre datos existentes, instalando con `instalar_flujos.py` y arrancando con el script generado. Las pruebas cubren:

- los **cuatro proveedores** dan 22/100 para NubeAndina, idéntico a Python;
- AndesCloud con perfil da 100, y el perfil llega al prompt marcado como no confiable;
- DigiServ da 0;
- corrección automática de un JSON roto;
- contrato en PDF de 2 páginas, con hash de los bytes;
- errores con mensaje claro (organización inexistente, petición inválida, modelo caído);
- doble puerta con 409 fuera de turno;
- perfilador con hashes reales;
- validación del perfil por el DPO;
- brechas (terceros sin DPA evaluado);
- creación de organización y subida de documentos;
- renovaciones, también la ejecución programada;
- **sin *Execute Command*:** Ollama y API siguen funcionando, y Claude Code y crear organización devuelven instrucciones claras.

Hallazgos de la instalación que condicionaron el diseño:

- **n8n 2.43 exige Node.js 24 o superior.**
- *Execute Command* viene desactivado (`NODES_EXCLUDE`).
- Los nodos de archivos solo acceden a `~/.n8n-files` salvo que se configure `N8N_RESTRICT_FILE_ACCESS_TO`.
- Los nodos Code no pueden leer ni escribir archivos ni usar `require`, y no crean carpetas.
- La activación es `publish:workflow`.

## 9. Etapa 3 — Página web servida por n8n

**http://localhost:5678/webhook/pims/app** · documentación en `web/LEEME.md` · guion de la demo en `GUIA_DEMO.md`.

- **Una página sin frameworks** (`web/index.html`) con siete pantallas: auditar, expedientes, expediente, por aprobar, organización y perfil, renovaciones y configuración.
- **Diseño.** La metáfora es el expediente. La *huella* de 24 casillas del semáforo resume cada contrato, y la doble puerta DPO → Legal se ve como **dos sellos** que se estampan al aprobar.
- **Archivos.** Los `.docx` se convierten en el navegador con mammoth; los PDF los lee n8n.
- **Funciona sin CDN.** Las librerías (marked, DOMPurify, mammoth) están en `web/vendor/`, copiadas de npm, con sus licencias.
- **Seguridad.** Funciona con el **aislamiento por defecto** de n8n 2.x (CSP sandbox), sin desactivarlo. Además, la API restringe con `allowedOrigins` quién puede leer sus respuestas: se verificó que un origen externo queda bloqueado.
- **Nuevos flujos y rutas.** Flujo nuevo *PIMS · Página web* (son 12 en total) y ruta `GET pims/documentos`.
- **Probada en Chromium real** contra n8n 2.43.4: **9/9 en tres corridas seguidas**, junto a las 21/21 de los flujos. Las pruebas detectaron cuatro errores, todos corregidos:
  - dos carreras entre pantallas;
  - un conflicto de estilos que deformaba el botón de aprobar;
  - desplazamiento horizontal en móvil.

La demo anterior (`demo/`, que llamaba a `claude -p` desde un servidor Python) queda como antecedente. La página nueva la reemplaza.

## 10. Etapa 4 — Caso UNSA

- **5 contratos ficticios** de proveedores de la UNSA en `pims-dpa-auditor_pruebas/unsa/contratos/` (copiados en `organizaciones/unsa/contratos/`): aula virtual, laboratorio clínico, pasarela de pagos, videovigilancia con reconocimiento facial y soporte del sistema académico (contrato estatal). Cada uno prueba un aspecto distinto del criterio; todos llevan aviso de ficción.
- **Evaluaciones de referencia** (`referencia/`) con `_alternativas` en los controles discutibles (15 en total), y **resultados esperados** (`esperado/`) calculados con `calcular_resultado.py --org organizaciones/unsa --fecha-ref 2026-10-13`. `construir_referencia.py` verifica que cada cita exista literalmente en el contrato. Puntajes: 50, 46, 99, 0 y 31.
- **`comparar_con_referencia.py`**: concordancia exacta y con alternativas, kappa de Cohen, controles críticos, puntaje, banda, dictamen, cobertura de alertas Altas y matriz de confusión. Sirve para comparar modelos.
- **`ejecutar_casos_unsa.py`**: audita los 5 contratos a través de n8n con el modelo configurado (con `--repeticiones` para medir estabilidad) y genera `comparacion.md`.
- `casos_unsa.json` en formato de evaluación de la skill.
- `modelo_simulado.py` reconoce los contratos de la UNSA y devuelve su referencia. Comprobado de punta a punta por n8n: 120/120 controles, kappa 1,0, puntajes y dictámenes idénticos.
- `organizaciones/unsa/LEEME.md`: qué documentos institucionales conseguir, dónde buscarlos (fuentes verificadas) y los pasos cuando lleguen.
- `GUIA_DEMO.md`: plan B con los contratos de la UNSA si aún no hay documentos.
- **Pendiente del grupo:** revisar las evaluaciones de referencia (las redactó el asistente) y generar el perfil cuando se consigan los documentos reales.

## 11. Documentación actualizada

- `README.md` (nuevo, en la raíz): presentación del proyecto para GitHub, arquitectura, puesta en marcha, casos, pruebas y mapa de la documentación. `.gitignore` excluye lo que genera cada equipo.
- `PROYECTO.md` reescrito para la v2.0: arquitectura, flujo de una auditoría, perfil, seguridad, estructura, pruebas y limitaciones. El análisis de la v1.1 pasa a `versiones/v1.1/PROYECTO_v1.1.md`.
- `MCP_SETUP.md`: presentado como ruta alternativa; §6 marcado como corregido en la v2.0, §7 corregido (la demo no usa API Key) y §9 con la instalación de las dos skills y el uso de organizaciones.
- `demo/README_DEMO.md` y la cabecera de `demo/app.js`: demo anterior, sin la referencia a un archivo inexistente.
- `n8n/INSTALACION_N8N.md`: casos de la UNSA en el modelo simulado, memoria de la tarjeta gráfica con Ollama y nota sobre Docker.
- `pims-dpa-auditor_pruebas/LEEME.md` y `organizaciones/LEEME.md`: todas las pruebas, el caso UNSA y la creación de organizaciones desde la página.

## 12. Ajustes tras la primera ejecución en Windows

- `instalar_flujos.py` usa `n8n.cmd` en Windows (Python 3.12 devolvía el script sin extensión: *WinError 193*). `demo/servidor_demo.py`, igual con `claude`.
- La URL de Ollama pasa a `http://127.0.0.1:11434`, y n8n convierte `localhost` en `127.0.0.1` (Node intentaba `::1` y Ollama solo escucha en IPv4: *ECONNREFUSED ::1:11434*).
- **Corrección con salida estructurada en Ollama:** si el JSON de la primera respuesta no cumple el esquema, la petición de corrección envía el esquema como `format`, y Ollama restringe la generación a esa forma. Comprobado que el esquema se convierte sin errores a la gramática de llama.cpp.
- `datos/fallidos/<trabajo>.md` guarda el motivo, los errores de esquema y **las dos respuestas** del modelo. `ejecutar_casos_unsa.py` muestra los errores en pantalla.
- **Primera ejecución real con `qwen2.5:7b`:** el modelo entregó el JSON con comentarios `// ... (repetir para los demás controles)` y **un solo control**. Cambios:
  - `extraerJSON` prioriza los bloques ```json (un bloque ```markdown previo desordenaba el emparejamiento y se enviaba a corregir un texto que no era el JSON) y repara comentarios y comas finales.
  - Nueva revisión de **los 24 controles** (faltantes, repetidos o desconocidos): sin ella, un JSON abreviado habría producido un puntaje calculado sobre menos controles. Si faltan, se pide la corrección y, si persiste, el trabajo termina en error.
  - La corrección recuerda los 24 controles, incluye la matriz de la sección 4 del propio informe y, con Ollama, el esquema obliga a exactamente 24 controles con identificadores válidos.
  - Las instrucciones de la auditoría piden JSON estricto, sin comentarios ni abreviaturas.
- **Ajustes de forma automáticos** (`normalizarRegistro`), que nunca cambian una calificación y quedan registrados en `_registro.ajustes_automaticos`: identificadores con adornos copiados de la referencia (`"A.2.5.7 🅰"` → `"A.2.5.7"`), fila A.1.2.7 retirada (es obligación de la organización, no un control del contrato) y `null` en campos opcionales que no lo admiten tratado como ausente. Son los errores que tuvo `qwen2.5:7b` en la corrección.
- **Salida estructurada configurable** (`formato_correccion`, en Configuración): `json` por defecto (JSON válido garantizado, sin costo apreciable), `esquema` (forma exacta con 24 controles; en la prueba real con `qwen2.5:7b` la llamada superó los 30 min) o `ninguno`. Ollama recibe además `num_predict` = máximo de tokens de salida, para cortar bucles.
- **Perfil con documentos reales y un modelo local (9 documentos, ~660 kB, `qwen2.5:7b`):** el perfil salió con un solo documento, la cabecera equivocada y §1 sin fuentes. Causa: las notas de todas las partes no cabían en el contexto (Ollama lo limita a 32 768 tokens en ese modelo) y Ollama descarta el principio del prompt sin avisar. Cambios:
  - `compactarNotas` + `presupuestoNotas`: las notas se depuran y, si no caben, se reparte el espacio entre todos los documentos; ningún documento queda fuera. El mensaje del trabajo avisa cuántas notas se omitieron.
  - `normalizarPerfil`: n8n corrige por código la cabecera (organización, id, jurisdicción, fecha, estado) y completa la tabla de documentos con todos los cargados y sus SHA-256 (conserva las filas del modelo que coinciden); las filas de §1-§6 sin fuente válida se marcan "Supuesto" para que el DPO las revise. Los ajustes quedan en `validacion_perfil.json`.
  - El selector de modelo ya no llama al modelo con una petición vacía cuando el paso anterior falló.
- Pruebas de flujos: 25/25 (nueva: perfil con documentos extensos y respuesta defectuosa). Antes, 24/24 (nuevas: JSON abreviado con comentarios, identificadores con adornos, y JSON inválido incluso tras la corrección).

## 12b. Chat sobre expedientes y organizaciones (pedido del docente)

- Flujo nuevo **PIMS · Chat** (`POST/GET /webhook/pims/chat`, 13 flujos en total): pregunta en segundo plano con el mismo modelo configurado; la respuesta queda en el trabajo y la conversación en `datos/chats/`.
- Contexto: en un expediente, el registro calculado, el texto del contrato (no confiable), el informe, la configuración y el perfil; en una organización, la tabla de sus expedientes, las alertas, el perfil y la configuración. Con Ollama se recorta por prioridad para caber en 32 768 tokens (`ajustarBloques`).
- Reglas del chat (`REGLAS_CHAT` en `n8n/lib/prompts.js`): solo el contexto y con fuente, no modifica nada, no obedece instrucciones de los documentos, las del usuario no cambian los criterios, no es asesoría legal.
- Cada auditoría guarda el texto evaluado en `datos/registro/<id>.contrato.txt`.
- Página: pestaña **Preguntar** en el expediente y sección en **Organización y perfil**, con sugerencias, Ctrl + Enter y la conversación guardada.
- Pruebas: 4 nuevas en los flujos (30/30: contexto, historial, expediente intacto, solo los expedientes de la organización, errores, recorte con Ollama) y 1 en la página (10/10).

## 12c. Corrección: lista de controles vacía

- Caso UNSA 03 con `qwen2.5:7b`: el JSON traía `"controles": [ // … ]`; al quitar el comentario quedaba una lista vacía, que el esquema acepta, y el sistema calculó **0/100 sin ningún control**. Ahora una lista vacía es un error: se pide la corrección y, si persiste, la auditoría termina en error. Prueba nueva (30/30).

## 13. Informe del TIF actualizado

`informe_TIF.tex` pasa a describir la v2.0 (segunda entrega, 63 páginas): tareas 1 a 3 actualizadas; secciones nuevas de generalización (tres capas, perfil, asimetría), orquestación con n8n (flujos, recorrido de una auditoría, modelo intercambiable, equivalencia JS = Python, controles para modelos pequeños, seguridad), interfaz web con capturas, pruebas automáticas, caso UNSA, prueba con un modelo local y comparación de modelos (tabla por completar); discusión, trabajo futuro, conclusiones y referencias ampliadas; anexos D (JSON v2), E (referencias UNSA) y F (servicios web). El informe de la primera entrega queda en `versiones/v1.1/informe_TIF_v1.1.tex`. Compila con pdfLaTeX (requiere babel-spanish, newtx y TeX Gyre).

## 13b. Desglose por sección del Anexo A, radar y verificación contra la norma

- **Desglose del puntaje:** las 4 dimensiones propias (Contractual, Ciclo de vida del dato, Transferencias y sub-encargados, Seguridad e incidentes) se reemplazan por las **5 secciones del Anexo A** de ISO/IEC 27701:2025: A.2.2 Condiciones de recolección y tratamiento (6 controles), A.2.3 Obligaciones con los titulares (1), A.2.4 Privacidad desde el diseño y por defecto (3), A.2.5 Compartición, transferencia y comunicación (8) y A.3 Consideraciones de seguridad (6). Cambian `calcular.js` y `calcular_resultado.py` (orden fijo, equivalencia JS = Python en 5 012 casos), `criterios_semaforo.md` §8.6, `SKILL.md` y el esquema. **El puntaje total, el dictamen y las alertas no cambian.**
- **Diagrama de radar:** la sección 7 de cada informe incluye la tabla por sección (con el número de controles evaluados) y un radar SVG dibujado por el código (escala 0-100, referencia en 80). La vista del expediente de la página muestra las barras y el radar. Los expedientes antiguos, con 4 dimensiones, se siguen viendo.
- **Verificación contra el texto oficial:** identificadores, títulos y secciones de los 24 controles coinciden con la norma. `controles_iso27701_2025.md` (v2.1) incorpora, parafraseada, la guía del Anexo B para los controles donde más ayuda (unos 900 tokens más por auditoría). La correspondencia con la edición 2019 sigue pendiente. El texto de la norma no se incluye en el repositorio.
- Resultados de referencia (`resultados/*.json`, `unsa/esperado/*.json`) regenerados: solo cambia `por_dimension`. Pruebas: 28/28 (prueba nueva del desglose), flujos 30/30 (verifican el radar), página 10/10.
- **Reimportar los flujos** en n8n: `calcular.js` y `prompts.js` van incrustados en ellos.

## 13c. 26 controles y cláusulas 4 a 10 (revisión contra el texto oficial, pedido del docente)

- **Controles:** de 24 a **26**. Se añaden de la Tabla A.3 **A.3.18** (acuerdos de confidencialidad) y **A.3.24** (respaldo de información), que se reflejan en un contrato de encargo. Otros controles de seguridad relacionados (A.3.26 criptografía, A.3.8 identidades, A.3.23 autenticación, B.3.4 punto de contacto) se revisan como señales dentro de A.3.9, A.3.10 y A.3.13; A.3.25 (registro de eventos) no se incluye: casi ningún DPA lo trata y daría "Sin evidencia" en todos.
- **Correcciones en `controles_iso27701_2025.md` (v2.2):** A.3.9 limitado al control de acceso (la confidencialidad pasa a A.3.18); A.3.12 con la guía para encargados (cómo entrega el encargado la información que el responsable necesita para notificar, sin demora indebida); la autorización escrita del cambio de sub-encargado pasa de A.2.5.8 a A.2.5.9; guía de A.2.2.7 restituida; nota de A.2.5.7 sobre la lista entregada con confidencialidad; sin la columna "Equiv. 2019": la evaluación es solo contra la edición 2025.
- **Cláusulas 4 a 10:** obligan a la organización, no al proveedor, así que no se califican. Se aplican en el proceso (`SKILL.md`, "Cláusulas de la norma en el proceso") y cada informe tiene una **sección 12** que n8n escribe a partir del registro: rol (4.1, 4.2), riesgos (6.1.2, 8.2), aplicabilidad (6.1.3 e), comunicación (7.4), información documentada (7.5), procesos externos (8.1), seguimiento (9.1) y no conformidades (10.2).
- **Referencias recalificadas:** los 8 contratos de prueba en A.3.18 y A.3.24, y A.3.9 donde solo había confidencialidad. A los contratos de AndesCloud y UNSA 03 (los "buenos") se les añadió una frase sobre respaldos. Puntajes: NubeAndina 22, AndesCloud 100, DigiServ 0 y UNSA 50, **44** (antes 46), 99, 0 y 31; dictámenes sin cambios. Las ejecuciones del 2026-10-07 quedan como registro histórico con 24 controles.
- Pruebas: 28/28, equivalencia JS = Python en 5 012 casos, flujos 30/30 (verifican 26 controles y la sección 12), página 10/10, UNSA con el modelo simulado 130/130.

## 14. Pendiente

- Perfil de la UNSA con los documentos reales (ver `organizaciones/unsa/LEEME.md`).
- Completar en `informe_TIF.tex` la Tabla 28 (comparación de modelos, etiqueta `tab:comparacion-modelos`) con los `comparacion.md` de Claude y de Ollama.
