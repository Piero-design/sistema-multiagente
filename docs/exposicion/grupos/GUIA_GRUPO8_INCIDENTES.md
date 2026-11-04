# Guía Grupo 8 — Agente de Incidentes y Brechas

Tiempo sugerido: **7–8 min**.

## 1–2. Objetivo y responsabilidad
Recibir el reporte de un evento, clasificarlo (evento / incidente / brecha de datos personales), evaluar su severidad para los titulares (ENISA), decidir si hay que notificar (art. 34 del Reglamento de la Ley 29733), controlar el plazo de **48 horas** y redactar borradores. **No envía notificaciones ni ejecuta contención.**

## 3. Arquitectura original
Servidor Node + interfaz React (puerto 3100, `web/`), motor de autonomía (`web/autonomia/`), conectores de solo lectura, `Dockerfile` y `docker-compose.yml` propios. Skills en `.claude/skills/`: `brecha-triaje`, `brecha-evaluacion-severidad`, `brecha-notificacion`, `brecha-respuesta-cierre`, más el comando `/gestionar-incidente`.

## 4. Skills y herramientas
Servidor MCP interno con `BuscarConocimiento`, `ListarSistemas`, `ConsultarSistema` (solo lectura), `BuscarQuejas` y `ProponerAccion` (registra una acción **propuesta** que debe aprobar una persona).

## 5–6. Flujo
`POST /api/analizar` → devuelve un `job` → el agente recorre triaje, severidad, notificación y respuesta/cierre → expediente con ficha, severidad, borradores (ANPD, titulares, CNSD), plan y cierre. Reglas: el reloj de 48 h inicia en el triaje y no se reinicia; no se incluyen datos personales de titulares; ante la duda una queja se analiza.

## 7. Demostración
`/agentes/incidentes` con un reporte ficticio: correo masivo enviado por error con DNI y notas de 300 estudiantes. Resultado real: **expediente `INC-…-envio-erroneo-datos-estudiantes`, clasificado como brecha de datos personales (fuga accidental por error humano), severidad Media (puntaje 2,5)**, con resumen de gestión. Es un caso simulado (UNSA).

## 8. Ejemplo
Entrada: `{reporte: "…", contexto?}` (mínimo 20 caracteres). Salida: estado del job (`running` → `done`), eventos de avance y `resultado` en Markdown.

## 9. Original frente a integrada
La interfaz original (React, aprobación de acciones propuestas, buzón, modo autónomo) sigue en `web/`. La integrada lanza análisis y muestra el expediente; las acciones propuestas se aprueban o rechazan en `/revision` (sesión de DPO); el agente solo registra la decisión y no ejecuta nada.

## 10. Gateway LLM
El código usa los SDK de Gemini y Groq sin URL configurable en su código. Se resolvió por entorno: sin clave de Gemini ni Anthropic, `GROQ_API_KEY=gateway-managed` y `GROQ_BASE_URL` = gateway (el SDK de Groq lo lee). Se usó su propio `Dockerfile`. La interfaz del agente muestra «Groq (modelo)», aunque en realidad sale por el gateway.

## 11. PostgreSQL
Guarda expedientes como archivos en `salidas/` (volumen). No usa Gestitel; `core_incident*` sería el destino opcional.

## 12. Otros agentes
Su guía describe entregas a G3 (titulares notificados), G4 (cadena de custodia), G5 (incidentes en un proveedor), G6 (activos afectados), G2 (causa raíz), G7 (controles propuestos) y G1 (lecciones). **No hay conexión automática** hoy.

## 13. Problemas y soluciones
- Sin URL base configurable para Gemini → se eligió el proveedor Groq, cuyo SDK sí la lee por variable.
- El agente pide una credencial al arrancar → se inyecta una marca de posición.

## Base normativa
- **Reglamento de la Ley 29733 (D.S. 016-2024-JUS)**, vigente desde el 30/03/2025: definición de incidente (art. III, num. 16), **art. 34.1** (notificar a la ANPD en máximo **48 horas** si se cumple alguno de sus supuestos; también comunicar a los titulares) y art. 34.7.
- **Metodología ENISA (2013)** de severidad: **SE = DPC × EI + CB** (contexto de los datos, facilidad de identificación y circunstancias de la brecha), medida sobre los titulares.
- Estándares sobre incidentes y taxonomía en `knowledge/` (`estandares-incidentes.md`, `taxonomia-incidentes.md`) y controles ISO/IEC 27002 propuestos en el cierre.
- *Cuidado:* el propio marco marca puntos como `[VERIFICAR]` (por ejemplo, si la ANPD ya publicó lineamientos sobre «grandes volúmenes»). Sus resultados son borradores de apoyo, no asesoría legal.

## 14. Guion
"Cuando ocurre una brecha el tiempo corre: 48 horas. Nuestro agente clasifica, evalúa severidad y deja los borradores listos, pero no envía nada. Aquí vemos un correo enviado por error: lo clasifica como brecha y propone el plan; la decisión final es de la persona responsable."

## 15. Preguntas probables
- *¿Notifica a la autoridad automáticamente?* No; solo borradores y acciones propuestas.
- *¿Con qué modelo?* El del gateway; no depende de Groq real.
- *¿Los casos son reales?* No, son simulados.

## 16. Conclusiones
Integración sin tocar su código: solo variables de entorno y su Dockerfile; las reglas de aprobación humana quedaron intactas.
