# Reparto del equipo

| Persona | Qué hace |
|---|---|
| **Ryan** | Construcción: los 4 skills, el agente, el comando, la orquestación, la integración y las pruebas técnicas |
| **Integrante 2** | **Investigación normativa:** Ley 29733, D.S. 016-2024-JUS, D.U. 007-2020 (CNSD), lineamientos de la ANPD. Redacta el **marco teórico** (parte legal) |
| **Integrante 3** | **Investigación de estándares:** ISO/IEC 27035, 27001/27002, 27701, 27037, NIST SP 800-61r3, metodología ENISA. Redacta el marco teórico (parte de estándares) y las **conclusiones** |
| **Integrante 4** | **Pruebas y presentación:** ejecuta los 4 casos y casos nuevos, registra evidencias, arma las **diapositivas**, el **guion de demo** y el formato del informe |

## Tareas concretas

### Integrante 2 — Normativa peruana
- [ ] Validar `knowledge/marco-normativo-peru.md` contra el texto oficial y resolver cada `[VERIFICAR]` (multas en UIT del art. 39 de la Ley, enlace del formulario, normas conexas).
- [ ] Averiguar si la ANPD ya publicó lineamientos sobre la notificación (art. 34.7) o umbrales de "gran volumen".
- [ ] Redactar `docs/informe/01-marco-teorico.md`, sección legal.
- [ ] Redactar `docs/informe/05-referencias.md` (normas legales).

### Integrante 3 — Estándares
- [ ] Validar `knowledge/estandares-incidentes.md`: numeración de controles ISO/IEC 27002:2022, cláusulas de ISO/IEC 27701 (ediciones 2019 y 2025) y fases de ISO/IEC 27035-1:2023.
- [ ] Validar `knowledge/metodologia-severidad.md` con el documento de ENISA (2013).
- [ ] Redactar `docs/informe/01-marco-teorico.md`, sección de estándares y de agentes/skills de IA.
- [ ] Redactar `docs/informe/04-conclusiones.md` cuando el proyecto esté probado.
- [ ] Proponer 2 casos ficticios adicionales (ej. proveedor de nube que avisa tarde, empleado que extrae datos) en `examples/entradas/`.

### Integrante 4 — Pruebas y presentación
- [ ] Leer `pruebas/README.md` y ejecutar los casos.
- [ ] Llenar `pruebas/registro-pruebas.md` y guardar las evidencias en `pruebas/evidencias/`.
- [ ] Reportar fallos a Ryan (issues en el repositorio).
- [ ] Armar las diapositivas y el guion de demo en `presentacion/`.
- [ ] Dar el formato final al informe (`docs/informe/`).

### Ryan — Construcción
- [x] Reorientar el proyecto a incidentes y brechas: skills, agente, comando, conocimiento y casos.
- [x] Documentación de las etapas del TIF.
- [x] Pruebas PR-01 a PR-10 y ajustes.
- [ ] Integrar el conocimiento validado por los integrantes 2 y 3.
- [ ] Escribir `docs/informe/02-desarrollo.md` y `03-resultados.md`.
- [ ] Sesión de 30 min para explicar el proyecto al equipo.

## Reglas de trabajo en el repositorio
- Cada quien trabaja en su rama (`ryan/...`, `int2/...`, `int3/...`, `int4/...`) y se une a `main` con un Pull Request.
- No subir datos personales reales; solo casos ficticios.
- Mensajes de commit claros: `docs: agrega marco teórico`, `test: registra pruebas del caso 2`.

## Reunión de sincronización
Semanal, 20 minutos: qué hice, qué haré, qué me bloquea.

## Mensaje para el grupo (copiar y pegar)
> Equipo, ya reorienté el TIF a nuestro tema, **Agente de incidentes y brechas**, en el repositorio **[enlace]**. Tiene 4 skills (triaje, severidad, notificación, respuesta y cierre) y un agente que sigue ISO/IEC 27035 y el D.S. 016-2024-JUS (notificación en 48 h). Necesito:
> - **[Integrante 2]:** validar la parte legal en `knowledge/marco-normativo-peru.md` y el marco teórico legal. Fecha: **[X]**
> - **[Integrante 3]:** validar las ISO/NIST en `knowledge/estandares-incidentes.md` y `metodologia-severidad.md`, el marco teórico de estándares y las conclusiones. Fecha: **[Y]**
> - **[Integrante 4]:** probar los 4 casos con evidencias, las diapositivas y el guion de demo. Fecha: **[Z]**
>
> Lean el `README.md` y nos reunimos el **[día/hora]** para explicarles cómo funciona.
