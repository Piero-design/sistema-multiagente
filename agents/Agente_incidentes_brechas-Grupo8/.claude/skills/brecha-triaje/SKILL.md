---
name: brecha-triaje
description: Recibe el reporte de un evento o posible incidente de seguridad (correo enviado por error, ransomware, laptop robada, acceso indebido, phishing, aviso de un proveedor) y determina si es un evento, un incidente de seguridad o una brecha de datos personales. Lo clasifica, prioriza, inicia el reloj de 48 horas y abre la ficha del incidente. Úsalo cuando alguien reporte algo que "pasó" con información o sistemas, aunque no diga "incidente" ni "brecha".
---

# Skill: Triaje de incidentes y brechas

Implementa las fases **Detectar y reportar** y **Evaluar y decidir** de ISO/IEC 27035-1:2023, los controles **6.8** y **5.25** de ISO/IEC 27002:2022 y el requisito 6.13.1.5 de ISO/IEC 27701:2019 (determinar si un incidente es una brecha de datos personales).

## Cuándo se activa
- "Nos llegó este reporte / correo / alerta, ¿qué hacemos?"
- "Se perdió una laptop", "enviamos un Excel al destinatario equivocado", "nos cifraron los archivos".
- "¿Esto es una brecha de datos personales?"
- El agente `agente-incidentes-brechas` lo invoca como primer paso.

## Entradas
Texto del reporte o ruta a un archivo (`examples/entradas/...`). Datos clave que debes buscar:
qué pasó, cuándo ocurrió, **cuándo se tomó conocimiento**, quién reporta (¿es un encargado/proveedor?), sistemas y datos involucrados, número aproximado de titulares, medidas ya tomadas.
Lo que no esté: `NO INDICADO`. No inventes fechas, horas ni cantidades.

## Pasos
1. **Registrar.** Asigna el ID `INC-<AAAAMMDD>-<slug>` (fecha de toma de conocimiento; si no se conoce, la fecha de hoy y márcalo). Crea la carpeta `salidas/<ID>/`.
2. **Línea de tiempo.** Separa: fecha/hora de ocurrencia, de **toma de conocimiento** y de reporte. La toma de conocimiento inicia el plazo de **48 horas** (art. 34.1, D.S. 016-2024-JUS). Calcula y escribe la **hora límite** con el criterio de "¿Desde cuándo corren las 48 horas?" de `knowledge/marco-normativo-peru.md` (la lectura más temprana; la otra, como referencia). Si falta la hora de conocimiento, ponlo como primera pregunta pendiente y avisa que el plazo ya podría estar corriendo.
3. **¿Evento, incidente o brecha?** Aplica el árbol de `knowledge/taxonomia-incidentes.md` (sección 3) y la definición del art. III num. 16 del reglamento (`knowledge/marco-normativo-peru.md`). Justifica en 1–2 líneas.
   - Si es **evento sin incidente**: registra, recomienda cierre y termina (no pasa a severidad).
   - Si es **incidente sin datos personales**: sigue el flujo ISO 27035 pero sin obligaciones de la Ley 29733.
4. **Clasificar.** Tipo de brecha (confidencialidad / integridad / disponibilidad, puede ser más de uno) y categoría (`MAL`, `INT`, `FUG`, etc.) de `knowledge/taxonomia-incidentes.md`.
5. **Datos y titulares afectados.** Categorías de datos (marca **sensibles** según la Ley 29733 y datos de **menores**), categorías de titulares, número aproximado. Distingue hecho de estimación.
6. **Rol del reportante.** Si quien reporta es un **encargado del tratamiento**, recuerda que debía avisar de inmediato (art. 36) y que la obligación de notificar recae en el responsable.
7. **¿Entorno digital?** Sí/No. Si es sí, anticipa la notificación adicional al CNSD (art. 34.5).
8. **Prioridad** P1–P4 con la tabla de `knowledge/taxonomia-incidentes.md` (sección 4).
9. **Acciones inmediatas sugeridas** (máx. 5), orientadas a **contener sin destruir evidencia** (ej. aislar el equipo de la red, no apagarlo ni formatearlo; pedir al destinatario que elimine el correo y lo confirme por escrito; bloquear la cuenta).
10. **Entregar** con `plantilla-ficha.md` (en esta carpeta) en `salidas/<ID>/01-ficha-incidente.md`.

## Reglas
- Distingue **hecho** (lo reportado), **inferencia** (lo que deduces, márcala) y **NO INDICADO**.
- Nunca concluyas "no es brecha" solo porque el reportante lo dice; contrástalo con la definición legal.
- No pidas ni copies datos personales reales de los afectados: trabaja con categorías y cantidades. Si la entrada trae datos reales, avisa y sugiere anonimizar.
- Si la entrada es ambigua sobre si hubo datos personales, trátalo como brecha probable hasta confirmar.
- Cierra con: *"Borrador de apoyo. Debe validarlo el Oficial de Datos Personales / responsable de seguridad."*
