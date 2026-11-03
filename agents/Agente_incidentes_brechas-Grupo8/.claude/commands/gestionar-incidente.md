---
description: Gestiona un incidente o brecha de datos personales de punta a punta (triaje, severidad, notificación, respuesta y cierre)
argument-hint: <ruta-del-reporte | texto del reporte> [contexto: <carpeta>]
allowed-tools: Bash(date:*)
---

Fecha y hora actual del sistema: !`date "+%Y-%m-%d %H:%M (%z)"`

Usa el agente `agente-incidentes-brechas` para gestionar este reporte de incidente:

$ARGUMENTS

Si el argumento incluye `contexto: <carpeta>`, pásale esa carpeta al agente para que verifique el reporte con su inventario, logs y políticas.

Si es una ruta, léela primero. Pásale al agente la fecha y hora actual de arriba para que calcule el **tiempo restante** hasta la hora límite (o cuánto lleva vencida). Sigue el flujo del agente (ciclo ISO/IEC 27035), guarda todo en `salidas/<ID>/` y termina mostrando: clasificación, severidad, **hora límite de notificación (48 h) y tiempo restante**, decisiones humanas pendientes y las rutas de los archivos generados.
