# 01 · Ficha de triaje — INC-20261010-hostandes-filtracion

> BORRADOR para revisión del Oficial de Datos Personales (ODP) y del responsable de seguridad. No contiene datos personales de afectados, solo categorías y cantidades.

## Reloj
| Dato | Valor |
|---|---|
| Fecha de la intrusión (según proveedor) | 2026-10-10 (hora no informada) |
| Aviso de HostAndes recibido por la Academia | **2026-10-12 15:50 (-05:00)** (reportado) |
| Reporte interno al ODP | 2026-10-12 16:20 |
| **Toma de conocimiento adoptada** | 2026-10-12 15:50 |
| **Hora límite 48 h (art. 34.1)** | **2026-10-14 15:50 (-05:00)** |
| Hora actual | 2026-10-13 10:00 |
| **Tiempo restante** | **29 h 50 min** |

Lectura alternativa más estricta `[VERIFICAR con asesoría legal]`: HostAndes (encargado) detectó el hecho el 10/10. Si se considerara su conocimiento, el plazo ya habría vencido. Según art. 36 el encargado debía avisar "de forma inmediata"; su aviso tardío es un hecho a documentar y reclamar. Si se notifica tras la hora límite, justificar la demora (art. 34.1). Se usa 15:50 del 12/10 porque la regla del proyecto es contar desde el conocimiento de cualquier persona **de la organización** `[VERIFICAR]`.

## Clasificación
- **Estado:** Incidente de seguridad de datos personales (**brecha probable**, art. III num. 16). Ante la duda sobre la descarga real, se trata como brecha (confidencialidad).
- **Tipo:** Confidencialidad.
- **Categoría:** PRV (incidente en encargado/proveedor) + INT (acceso no autorizado a servidor compartido).
- **Prioridad:** P2 Alta (brecha con datos personales, reloj de 48 h corriendo).
- **Roles:** la Academia es **responsable** (titular del banco de datos); HostAndes es **encargado**. La obligación de notificar es de la Academia (arts. 34 y 36).

## Niveles de información
| Hecho | Nivel | Fuente |
|---|---|---|
| Acceso no autorizado a servidor compartido de HostAndes, detectado el 10/10 | Reportado (por el proveedor, sin evidencia propia) | correo de HostAndes (no adjunto) |
| Una copia de la BD "podría haber sido descargada" | Reportado, **no confirmado** | ídem |
| ~2 400 alumnos, muchos menores de 18 | Reportado | reporte, líneas 11 |
| Datos: nombres, DNI, fecha de nacimiento, colegio, dirección, teléfono y correo de apoderados, estado de pagos | Reportado | reporte, línea 11 |
| Sin datos de tarjetas | Reportado | reporte, línea 11 |
| Cifrado de contraseñas de usuarios | **Desconocido** | reporte, línea 11 |
| Cambio de clave de la administradora | Reportado (acción ya tomada) | reporte, línea 13 |
| No se avisó a nadie más | Reportado | reporte, línea 13 |
| Alcance exacto, vector, tablas accedidas | Supuesto / pendiente | — |

No se indicó carpeta de contexto: no hay inventario ni logs verificados.

## Respuesta a la consulta de la coordinadora
- **¿Es culpa nuestra?** Aún no se puede afirmar. El origen está en el proveedor, pero la Academia sigue siendo responsable frente a la ANPD y los titulares (art. 34). La responsabilidad por la elección y supervisión del proveedor se evalúa luego, en el cierre.
- **¿Hay que notificar?** Sí, se recomienda (ver `02-evaluacion-severidad.md`).

## Acciones inmediatas (contención)
1. Cambiar **todas** las contraseñas de la plataforma (administradores, personal y usuarios/apoderados), activar MFA si existe y revocar sesiones y claves de API.
2. Solicitar a HostAndes por escrito, con plazo corto, la información listada en `04-respuesta-y-cierre.md`.
3. Preservar evidencia: guardar el correo original de HostAndes con cabeceras, sin reenviarlo ni borrarlo.
4. Registrar el incidente (art. 35).
