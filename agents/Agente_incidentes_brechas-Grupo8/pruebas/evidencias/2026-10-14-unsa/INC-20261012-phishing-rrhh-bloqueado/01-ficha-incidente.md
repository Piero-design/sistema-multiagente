# Ficha de triaje — INC-20261012-phishing-rrhh-bloqueado

> BORRADOR para revisión del Oficial de Datos Personales y del responsable de seguridad. Escenario simulado (UNSA).

## 1. Reloj
| Dato | Valor |
|---|---|
| Toma de conocimiento (reportada) | 2026-10-12 08:05 (detección por el filtro de correo; aviso formal 10:30) |
| Hora límite de 48 h (solo si se reclasificara como brecha) | 2026-10-14 08:05 |
| Hora actual (indicada por el usuario) | 2026-10-13 09:00 (-0500) |
| Tiempo restante | 23 h 05 min |
| Lectura alterna (aviso 10:30) | límite 2026-10-14 10:30 (se usa la más temprana) |

Nota: el reloj es solo de referencia. Con la información actual no hay obligación de notificar.

## 2. Hechos por nivel de confianza
| Nivel | Hecho | Fuente |
|---|---|---|
| Reportado | Campaña de phishing que suplantaba a "Recursos Humanos" (actualizar datos del escalafón, enlace externo) | reporte:9 |
| Reportado | ~900 correos de docentes destinatarios | reporte:9 |
| Reportado | 100 % bloqueado y puesto en cuarentena | reporte:11 |
| Reportado | Nadie abrió el mensaje ni hizo clic; sin credenciales ingresadas ni accesos extraños | reporte:11 |
| Reportado | Dominio bloqueado en el proxy | reporte:11 |
| Verificado | Correo institucional (S-07) en nube del proveedor, cifrado por el proveedor; docentes y administrativos: 3 100 titulares en S-06 | demo/unsa-base/inventario/activos-y-datos.md:15, :27 |
| Verificado | No hay logs en el contexto (solo inventario y políticas) | demo/unsa-base/README.md:5 |
| Supuesto | La cuarentena fue efectiva y no hubo clics ni accesos. No se puede contrastar con logs de correo, proxy ni autenticación | — |

## 3. Clasificación
- **Categoría:** FRA (fraude e ingeniería social / phishing).
- **Resultado del triaje:** **Evento sin incidente** (intento bloqueado). Según `taxonomia-incidentes.md` §3 y su lista de ejemplos, un phishing reportado y no abierto no es incidente.
- **¿Se vulneró un control?** No según lo reportado. El control (filtro de correo) funcionó.
- **¿Se afectó confidencialidad, integridad o disponibilidad?** No según lo reportado.
- **¿Datos personales comprometidos?** No. Solo se usaron direcciones de correo como destino, sin exposición reportada.
- **Prioridad:** P4 Baja (registro rutinario), condicionada a la verificación de la sección 4.
- **Rol del reportante:** personal de la OTI (interno). No es encargado, por lo que no aplica el art. 36.

## 4. Condiciones para mantener la clasificación (verificar antes de cerrar)
La conclusión depende de afirmaciones no contrastadas. El reporte dice "revisé los registros" pero no adjunta evidencia. Verificar:
1. En el log del filtro de correo, que los ~900 mensajes figuren como entregados a cuarentena y ninguno a bandeja de entrada ni liberado por un usuario.
2. En el log del proxy/DNS, cero solicitudes al dominio de phishing desde la red institucional **antes** del bloqueo. Hay que cubrir también acceso móvil o fuera de la red.
3. En los registros de autenticación del correo, sin inicios de sesión anómalos de los destinatarios (ubicación, IP, hora). Esto importa porque la VPN y el SRA no tienen MFA.
4. Que ningún usuario haya reportado haber abierto el correo por otra vía, como una consulta por teléfono.

**Criterio de reclasificación:** si alguno de los puntos 1 a 3 muestra clic, ingreso de credenciales o acceso anómalo, se reclasifica a incidente FRA/INT con probable brecha de confidencialidad. Se aplicaría entonces el flujo completo (severidad, art. 34) y la hora límite de 48 h ya calculada. Ante esa duda, recomendar notificar.

## 5. Decisión de flujo
Evento sin incidente: informe breve y cierre condicionado. No se generan 02, 03 ni 04 porque no hay brecha ni obligación (art. 34).
Se documenta el evento como registro interno (art. 35, buena práctica; ISO/IEC 27701 6.13.1.5).

## 6. Acciones recomendadas (no ofensivas)
- Conservar el correo original con cabeceras y la lista de destinatarios (ISO/IEC 27037, ISO/IEC 27002 5.28) y registrar el dominio e IOC.
- Enviar un aviso breve a los docentes: ignorar y reportar mensajes similares (ISO/IEC 27002 6.3).
- Revisar si hay mensajes equivalentes en otros buzones o campañas posteriores (ISO/IEC 27002 8.7, 8.23).
- Registrar el evento en el registro de eventos de la OTI (ISO/IEC 27002 6.8).
