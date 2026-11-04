# Guía Grupo 5 — Agente de Terceros y DPA

Tiempo sugerido: **7–8 min**. Aclarar el nombre: en su código el agente se llama «Agente 7» (numeración original); **no tiene relación con el Grupo 7**.

## 1–2. Objetivo y responsabilidad
Auditar contratos de encargo de tratamiento (DPA) con proveedores contra ISO/IEC 27701:2025 y la Ley 29733 («PIMS Privacy Guard»).

## 3. Arquitectura original
Motor **n8n** (puerto 5678) que sirve la API y la página web (14 flujos), más Node y Python. Skills `pims-dpa-auditor/` (26 controles) y `pims-perfilador-organizacion/` (perfil de la organización). Datos en archivos (`datos/registro/`) y scripts SQL para extender Gestitel (`bd/`, desactivado por defecto).

## 4. Skills y funcionalidad
Auditar contrato, perfilar organización, aprobaciones con doble puerta (DPO → Legal), renovaciones, consultas y chat sobre expedientes. API: `pims/auditar`, `pims/trabajo`, `pims/registro`, `pims/organizaciones`, `pims/aprobar`, etc.

## 5–6. Flujo
`POST pims/auditar` → responde `202 {trabajo}` → el modelo califica cada uno de los 26 controles → **el puntaje, la banda y el dictamen los calcula el código** (`n8n/lib/calcular.js`), no el modelo → el expediente nace «Pendiente DPO». El texto del contrato no es confiable: si trae instrucciones se reportan como alerta.

## 7. Demostración
`/agentes/terceros` → "Auditar contrato" con un contrato incompleto (datos de demostración). Resultado real: **terminado en ~29 s, puntaje 2, banda "Riesgo alto", dictamen "No recomendable sin enmiendas"**, con advertencia de que el perfil de la organización no está validado. Con un modelo local puede tardar 2–5 min.

## 8. Entradas y salidas
Entrada: `{organizacion, contrato_texto}`. Salida: `id_registro`, `puntaje`, `banda`, `dictamen`, `advertencias`. Estados reales del trabajo: `en_cola → evaluando → terminado`.

## 9. Original frente a integrada
La página web de n8n (`/webhook/pims/app`) conserva todo, incluidas las aprobaciones. La integrada audita y consulta; **no ofrece aprobar**: `pims/aprobar` es una decisión humana (DPO primero, luego Legal) y no se expone a modelos.

## 10. Gateway LLM
Por configuración del propio agente: `datos/config_modelo.json` con proveedor `openai` y `url_openai` = gateway (se parchea al iniciar el contenedor). Sin editar flujos ni skills.

## 11. PostgreSQL
Trae un patrón ejemplar: `agente7_terceros_dpa.sql` (6 tablas, 5 vistas, funciones) y `roles_agente7.sql` (rol que lee todo el PIMS y escribe solo en sus tablas). Sirvió de modelo para los roles de los demás agentes. **En la plataforma está activa:** al auditar, el expediente se guarda en Gestitel (evaluación, 26 controles, contrato y tercero) además de los archivos del agente; verificado con una auditoría real. Las consultas, renovaciones y el chat todavía leen de archivos, como indica el propio grupo.

## 12. Otros agentes
G3 le enviaría `notificar_destinatarios`, pero **este agente aún no recibe handoffs**. `pims/organizaciones` entrega terceros sin DPA evaluado (útil para G6). Cada expediente guarda el hash del contrato (útil para G4).

## 13. Problemas y soluciones
- Rutas absolutas dentro de los flujos → se regeneran con su `instalar_flujos.py --importar` dentro del contenedor.
- Execute Command habilitado (lo requiere el agente) → está aislado en su contenedor.
- Pendiente del grupo: el caso del laboratorio clínico da 44 o 46 según el documento.

## 14. Guion
"Nuestro agente audita contratos con proveedores. Un detalle de diseño: el modelo solo califica los controles; el puntaje lo calcula el código, así que el resultado es reproducible. Además, nada se aprueba solo: todo expediente espera la decisión del DPO y luego de Legal."

## 15. Preguntas probables
- *¿Por qué tarda?* Evalúa 26 controles; con modelo local son minutos.
- *¿Y si el contrato trae instrucciones maliciosas?* Se reportan como alerta y no se obedecen.
- *¿Dónde se aprueba?* En la interfaz original del grupo.

## 16. Conclusiones
Se integró sin editar flujos ni skills; su diseño de roles en PostgreSQL es el patrón que usaron los demás agentes.
