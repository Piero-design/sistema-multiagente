---
name: brecha-respuesta-cierre
description: Elabora el plan de respuesta a un incidente o brecha de seguridad (contención, preservación de evidencia y cadena de custodia, erradicación y recuperación) y el informe de cierre con causa raíz, lecciones aprendidas y controles ISO/IEC 27002 propuestos, dejando el registro que exige el art. 35 del Reglamento de la Ley 29733. Úsalo cuando se pida "cómo contenemos esto", "plan de respuesta", "informe post-incidente", "lecciones aprendidas" o "cerrar el incidente".
---

# Skill: Respuesta, evidencia y cierre del incidente

Implementa las fases **Responder** y **Aprender lecciones** de ISO/IEC 27035-1:2023 (con el detalle operativo de ISO/IEC 27035-3:2020), los controles **5.26, 5.27, 5.28 y 5.29** de ISO/IEC 27002:2022, la preservación de evidencia de **ISO/IEC 27037:2012** y las funciones Respond/Recover de **NIST SP 800-61 Rev. 3**. Produce la documentación del **art. 35 del D.S. 016-2024-JUS**.

## Cuándo se activa
- "¿Cómo contenemos el ataque?", "arma el plan de respuesta".
- "Haz el informe post-incidente / lecciones aprendidas", "cerremos el incidente".
- El agente lo invoca después de la notificación (o después de la severidad si no hay que notificar).

## Entradas
Archivos previos de `salidas/<ID>/`. Información de la investigación si existe (logs, hallazgos técnicos). Lo que falte: `NO INDICADO`.

## Pasos
1. **Contención** (corto plazo y largo plazo). Acciones específicas al tipo de incidente (ver tabla abajo). Cada acción con responsable sugerido y si **afecta la evidencia**.
2. **Preservación de evidencia** (ISO/IEC 27037; control 5.28). Qué evidencia recolectar (logs del art. 46.3 del reglamento, imágenes de disco, correos con cabeceras, capturas), cómo preservarla (copia, hash, almacenamiento de solo lectura) y registro de **cadena de custodia**. Primero preservar y luego erradicar.
3. **Erradicación.** Eliminar la causa (malware, cuenta comprometida, vulnerabilidad, permiso excesivo).
4. **Recuperación.** Restaurar desde respaldos verificados (control 8.13; art. 48 del reglamento), monitoreo reforzado y criterio para volver a operación normal.
5. **Causa raíz.** Usa la técnica de los **5 porqués**; separa la causa técnica, la de proceso y la humana. Si no hay datos suficientes, deja la hipótesis marcada como inferencia.
6. **Lecciones aprendidas** (control 5.27): qué funcionó, qué no, qué cambiar. Propón controles de `knowledge/estandares-incidentes.md` (sección 2) con su número.
7. **Registro del incidente** (art. 35; ISO/IEC 27701 6.13.1.5): hechos, efectos, medidas, notificaciones realizadas y fechas.
8. **Criterios de cierre**: contenido, erradicado, recuperado, notificaciones hechas o descartadas con fundamento, acciones correctivas asignadas.
9. **Entregar** con `plantilla-informe-cierre.md` en `salidas/<ID>/04-respuesta-y-cierre.md`.

## Acciones de contención típicas
| Categoría | Contención | Cuidado con la evidencia |
|---|---|---|
| MAL (ransomware) | Aislar equipos de la red, desactivar cuentas comprometidas, proteger respaldos fuera de línea | No apagar ni formatear sin capturar memoria y disco; no pagar el rescate sin decisión de la alta dirección y asesoría |
| INT / FRA | Restablecer credenciales, cerrar sesiones, activar MFA, bloquear IP/dominio | Exportar logs de acceso antes de que roten |
| FUG (envío por error) | Solicitar al destinatario eliminación y **confirmación escrita**; revocar enlaces compartidos | Guardar el correo original con cabeceras |
| FIS (robo/pérdida) | Bloqueo y borrado remoto, revocar sesiones del equipo, denuncia policial | Registrar la constancia de la denuncia y el estado del cifrado |
| INS (uso indebido interno) | Suspender accesos, revisar privilegios | Coordinar con RR. HH. y legal; conservar logs |
| PRV (proveedor) | Exigir informe al encargado (art. 36), revisar contrato e interfaces | Solicitar evidencias del proveedor |

## Reglas
- No indiques acciones ofensivas (contraataque, "hack back") ni que alteren evidencia sin advertirlo.
- Las acciones técnicas son **recomendaciones** para el equipo de TI; el agente no ejecuta nada.
- Cada control propuesto lleva su número ISO/IEC 27002:2022 y el riesgo que cubre.
- Cierra con: *"Borrador de apoyo. El cierre formal lo aprueban el responsable de seguridad y el Oficial de Datos Personales."*
