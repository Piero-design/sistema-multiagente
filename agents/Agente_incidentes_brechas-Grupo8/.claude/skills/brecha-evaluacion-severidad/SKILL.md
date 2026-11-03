---
name: brecha-evaluacion-severidad
description: Evalúa la severidad de una brecha de datos personales para los titulares con la metodología ENISA (contexto de los datos × facilidad de identificación + circunstancias) y decide, según el art. 34 del Reglamento de la Ley 29733 (D.S. 016-2024-JUS), si hay que notificar a la ANPD, comunicar a los titulares y reportar al CNSD. Úsalo cuando se pregunte "¿qué tan grave es?", "¿tenemos que notificar?" o cuando el triaje confirme una brecha.
---

# Skill: Evaluación de severidad y decisión de notificación

Implementa la fase **Evaluar y decidir** de ISO/IEC 27035-1:2023 y el control **5.25** de ISO/IEC 27002:2022, aplicados al **riesgo para los titulares** (ISO/IEC 27701:2019, 6.13.1.5).

## Cuándo se activa
- "¿Qué tan grave es esta brecha?", "¿hay que notificar a la autoridad?", "¿debemos avisar a los afectados?"
- La ficha de `brecha-triaje` concluyó "Incidente de seguridad de datos personales".

## Entradas
Preferible: `salidas/<ID>/01-ficha-incidente.md`. Alternativa: descripción libre (en ese caso, completa primero lo mínimo del triaje: tipo, datos, titulares, momento de conocimiento).

## Pasos
1. **Leer** la ficha y `knowledge/metodologia-severidad.md`.
2. **DPC.** Puntaje base 1–4 según el dato más delicado afectado; aplica el ajuste de contexto (menores, vulnerabilidad, combinación de datos) y justifícalo.
3. **EI.** 0,25 / 0,5 / 0,75 / 1 con justificación. Si los datos estaban cifrados y la clave no se comprometió, aplícalo y dilo.
4. **CB.** Suma confidencialidad + integridad + disponibilidad + intención maliciosa, cada uno con su motivo.
5. **Calcular SE = DPC × EI + CB** y el nivel (Baja / Media / Alta / Muy alta). Muestra la operación.
6. **Consecuencias para los titulares.** Lista concreta (suplantación, fraude, discriminación, extorsión, daño reputacional, pérdida de acceso a un servicio). Nada de consecuencias para la empresa aquí: van en una nota aparte.
7. **Decisión legal**, supuesto por supuesto (tabla de la sección 5 de `metodologia-severidad.md` y `knowledge/marco-normativo-peru.md`):
   - Notificar a la **ANPD** (art. 34.1): ¿datos sensibles? ¿grandes volúmenes? ¿gran número de personas? ¿perjuicio evidente a derechos o libertades?
   - Comunicar a los **titulares** (art. 34.3) o aplicar la excepción del art. 34.4.
   - Notificar al **CNSD** (art. 34.5) si fue en entorno digital.
   - **Documentar** siempre (art. 35).
8. **Plazos.** Repite la hora límite (48 h desde la toma de conocimiento) y cuánto falta. Si ya venció, indica que la notificación debe incluir los motivos de la demora (art. 34.1).
9. **Entregar** con `plantilla-severidad.md` en `salidas/<ID>/02-evaluacion-severidad.md`.

## Reglas
- Cada valor numérico lleva su **justificación en una línea**: la puntuación debe ser reproducible por otra persona.
- La obligación legal **no depende solo del puntaje SE**: un solo supuesto del art. 34.1 basta.
- El reglamento no fija umbrales para "gran volumen" o "gran número": dilo, marca `[VERIFICAR lineamientos ANPD]` y, **ante la duda, recomienda notificar**.
- No afirmes que la organización "cumplió" o "incumplió": usa "obligación probable" / "sin obligación aparente".
- Cierra con: *"Borrador de apoyo. La decisión de notificar la toma el responsable del tratamiento con el Oficial de Datos Personales."*
