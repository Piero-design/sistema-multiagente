# 01 · Ficha de triaje — INC-20261012-dos-portal-matricula

> BORRADOR para revisión del Oficial de Datos Personales y del responsable de seguridad. Escenario simulado (UNSA).

## 1. Reloj (primero)
| Dato | Valor |
|---|---|
| Inicio del evento / primera toma de conocimiento (lectura más temprana) | 2026-10-12 09:10 (caída del portal) |
| Confirmación del ataque DoS (fin) | 2026-10-12 11:40 |
| Reporte a la ODP (referencia, lectura más tardía) | 2026-10-12 14:00 (correo) |
| **Hora límite 48 h (más temprana)** | **2026-10-14 09:10** |
| Hora límite de referencia (desde el correo) | 2026-10-14 14:00 |
| Hora actual indicada | 2026-10-13 09:00 (-0500) |
| **Tiempo restante** | **24 h 10 min** (hasta 09:10 del 14/10) |

Nota: el entorno también indica "hoy = 2026-10-14". Si esa fecha fuera la real, la hora límite estaría vencida o a punto de vencer: **confirmar la hora actual**. Se usa la hora indicada en el comando. Se aplica la lectura más temprana (art. 34.1, criterio del proyecto `[VERIFICAR]`). Las 48 h solo rigen si se confirma una brecha de datos personales.

## 2. Hechos (tres niveles)
| Nivel | Hecho | Fuente |
|---|---|---|
| Reportado | Ataque DoS (tráfico masivo, miles de IP) al portal de matrícula, 09:10–11:40 del 12/10 | `salidas/_entradas` reporte, l. 9 |
| Reportado | El proveedor de internet filtró el tráfico y el servicio volvió | reporte, l. 9 |
| Reportado | "No hay accesos no autorizados, ni modificaciones, ni exportaciones" | reporte, l. 9 |
| Reportado | ~1 200 estudiantes no pudieron matricularse; plazo ampliado | reporte, l. 11 |
| Verificado | El portal de matrícula (S-08) existe en SRV-WEB-MAT, **sin cifrado en reposo y sin respaldo** | `demo/unsa-base/inventario/activos-y-datos.md:16` |
| Verificado | Banco de estudiantes: 28 000 activos, ~900 menores; datos: nombres, DNI, domicilio, correo, teléfono, notas | `activos-y-datos.md:22` |
| Verificado | NetAndes Perú es el proveedor de internet (contacto NOC) | `inventario/contactos.md:10` |
| Verificado | Registros de auditoría solo 60 días (art. 46.3 exige 2 años); alertas sin guardia fuera de horario | `activos-y-datos.md:32-33` |
| **No verificable** | La ausencia de acceso/exfiltración: **el contexto no incluye logs** de S-08 ni de la BD | `demo/unsa-base/README.md:5` |
| Supuesto | Que el DoS no sirvió de cortina para una intrusión paralela | — |

## 3. Clasificación
- **¿Evento o incidente?** Incidente de seguridad de la información: se afectó la **disponibilidad** (servicio caído 2 h 30 min, impacto operativo en ~1 200 estudiantes).
- **Categoría:** DIS (indisponibilidad / DoS). Tipo: Disponibilidad. Intención maliciosa: sí (ataque deliberado).
- **¿Datos personales?** El portal trata datos personales de estudiantes, pero según lo reportado **no hubo destrucción, pérdida, alteración ilícita ni exposición** (art. III num. 16). La indisponibilidad temporal del servicio no es en sí pérdida de los datos.
- **Resultado:** **Incidente de seguridad de la información; brecha de datos personales NO confirmada.** Queda pendiente la verificación técnica de la afirmación "sin accesos". Si no se puede verificar, se trata como brecha probable (regla "ante la duda").
- **Prioridad:** P3 (media) mientras no se verifique; sube a P2 si hay indicios de acceso o exportación.
- **Rol del reportante:** Centro de Cómputo, personal interno del responsable (no es encargado).

## 4. Siguiente paso
Evaluar severidad de forma precautoria (02) y documentar (art. 35). Puerta de decisión antes de las 09:10 del 14/10: revisión de logs de S-08 y la BD.
