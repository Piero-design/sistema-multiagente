# Etapa 3 — Construcción del asistente

**Objetivo:** dar al asistente identidad, instrucciones y conocimiento propios. **Resultado: un skill funcional especializado en incidentes y brechas.**

## Los tres ingredientes

| Ingrediente | Cómo se implementó |
|---|---|
| **Identidad** | Analista de respuesta a incidentes de privacidad que apoya al Oficial de Datos Personales y al responsable de seguridad. Tono calmado y metódico con el equipo interno, claro y empático con los titulares afectados. Prioriza a las personas afectadas y el plazo legal |
| **Instrucciones** | Pasos, reglas y plantillas en cada `SKILL.md`; reglas globales en el agente (primero el reloj, ante la duda notificar, no destruir evidencia, nunca enviar) |
| **Conocimiento** | Carpeta `knowledge/` (abajo) |

## Base de conocimiento

| Archivo | Contenido | Fuente |
|---|---|---|
| `marco-normativo-peru.md` | Definición legal, arts. 34 a 36, contenido mínimo, CNSD, medidas de seguridad, sanción | D.S. 016-2024-JUS (texto oficial, El Peruano 30/11/2024) |
| `estandares-incidentes.md` | Fases ISO/IEC 27035, controles ISO/IEC 27002:2022, ISO/IEC 27701, NIST SP 800-61r3, ISO/IEC 27037, tabla de correspondencia | Normas ISO y NIST |
| `metodologia-severidad.md` | Fórmula SE = DPC × EI + CB y regla de decisión peruana | ENISA (2013) + art. 34.1 |
| `taxonomia-incidentes.md` | Tipos CID, categorías, evento vs. incidente vs. brecha, prioridades | Taxonomía de referencia ENISA/CSIRT, ISO/IEC 27035 |

## Conocimiento por skill

| Skill | Usa |
|---|---|
| `brecha-triaje` | `taxonomia-incidentes.md`, `marco-normativo-peru.md` (definición, art. 36) |
| `brecha-evaluacion-severidad` | `metodologia-severidad.md`, `marco-normativo-peru.md` (art. 34) |
| `brecha-notificacion` | `marco-normativo-peru.md` (arts. 34.2 a 34.5) |
| `brecha-respuesta-cierre` | `estandares-incidentes.md` (controles 5.26 a 5.29, 8.13; ISO/IEC 27037), `marco-normativo-peru.md` (arts. 35, 46, 48) |

## Especialización lograda
- Distingue **evento / incidente / brecha** con la definición legal.
- Calcula la **hora límite** antes de analizar.
- Puntúa la severidad con una fórmula justificada factor por factor.
- Decide la notificación **supuesto por supuesto** del art. 34.1, no por intuición.
- Redacta para dos audiencias: la autoridad (técnico y completo) y los titulares (claro y accionable).
- Propone controles con su número ISO/IEC 27002.

## Criterios de "skill funcional"
- [ ] Se activa con las frases previstas, aunque no se digan "incidente" ni "brecha".
- [ ] Produce todas las secciones de la plantilla.
- [ ] No inventa plazos, artículos ni controles.
- [ ] Marca `NO INDICADO` y `[VERIFICAR]`.
- [ ] El caso 4 (phishing bloqueado) **no** termina en notificación.
- [ ] Funciona con los 4 casos de `examples/entradas/` (ver `pruebas/`).
