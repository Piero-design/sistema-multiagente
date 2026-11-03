# Etapa 4 — Diseño del agente

**Objetivo:** definir el objetivo, los datos, el contexto y las herramientas del agente. La definición está en `.claude/agents/agente-incidentes-brechas.md`.

## Ficha del agente

| Elemento | Definición |
|---|---|
| **Nombre** | `agente-incidentes-brechas` |
| **Objetivo** | Convertir el reporte de un incidente en un expediente trazable (ficha, severidad, notificaciones, respuesta y cierre) sin perder el plazo de 48 h |
| **Usuarios** | Oficial de Datos Personales, responsable de seguridad de la información, equipo de respuesta a incidentes |
| **Entradas** | Reporte del incidente (texto o archivo) |
| **Datos / conocimiento** | `knowledge/` (D.S. 016-2024-JUS, ISO/IEC 27035/27002/27701, NIST, ENISA), `examples/entradas/` |
| **Contexto** | Organización peruana sujeta a la Ley 29733 que gestiona su seguridad con ISO/IEC 27001 (NTP) y su privacidad con ISO/IEC 27701 |
| **Herramientas** | `Read`, `Glob`, `Grep` (leer); `Write` (solo en `salidas/`). Sin red, sin comandos, sin envío de correos |
| **Skills** | `brecha-triaje`, `brecha-evaluacion-severidad`, `brecha-notificacion`, `brecha-respuesta-cierre` |
| **Salidas** | `salidas/<ID>/00-informe.md` a `04-respuesta-y-cierre.md` |

## Diferencia entre skill y agente

| | Skill | Agente |
|---|---|---|
| Alcance | Una fase del ciclo | El ciclo completo del incidente |
| Decisión | Sigue pasos fijos | **Decide** el camino: cierra un evento, omite la notificación si no corresponde o la prioriza si el plazo vence |
| Estado | Lee y escribe un archivo | Mantiene el expediente y el reloj a lo largo de todo el flujo |

## Autonomía y límites

| Puede hacer solo | Requiere un humano |
|---|---|
| Clasificar y puntuar el incidente | Confirmar los hechos y la hora de conocimiento |
| Calcular plazos | Decidir si se notifica |
| Redactar borradores de notificación | **Enviar** cualquier notificación o comunicación |
| Proponer contención y controles | Ejecutar acciones técnicas sobre los sistemas |
| Escribir el expediente en `salidas/` | Aprobar el cierre del incidente |

## Riesgos del propio agente y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Inventar plazos o artículos | Citas literales en `knowledge/`; regla de no inventar; `[VERIFICAR]` |
| Concluir "no es brecha" por error | Regla "ante la duda, brecha probable"; caso de control 4 para probar lo contrario |
| Recomendar acciones que destruyan evidencia | Columna "¿afecta evidencia?" obligatoria en la contención |
| Exponer datos de los afectados | Trabaja con categorías y cantidades; aviso si la entrada trae datos reales |
| Que se envíe un borrador sin revisión | Cierre obligatorio "No enviar sin aprobación"; el agente no tiene herramientas de envío |
