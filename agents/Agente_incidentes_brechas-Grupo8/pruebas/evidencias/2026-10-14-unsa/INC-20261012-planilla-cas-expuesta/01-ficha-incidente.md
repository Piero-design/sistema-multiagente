# 01 — Ficha de triaje · INC-20261012-planilla-cas-expuesta

> BORRADOR para revisión del Oficial de Datos Personales y del responsable de seguridad. ESCENARIO SIMULADO (UNSA). Sin datos personales reales: solo categorías y cantidades.

## Reloj
| Concepto | Valor |
|---|---|
| Toma de conocimiento (lectura más temprana) | 2026-10-12, hora exacta NO INDICADA: el docente escribió "hoy" a RR. HH. antes del correo de las 15:45 `[VERIFICAR hora del mensaje del docente]` |
| Referencia de cálculo | 2026-10-12 15:45 (correo del Jefe de RR. HH. al ODP; reportado) |
| **Hora límite 48 h (referencia)** | **2026-10-14 15:45 (-0500)**; puede ser más temprana si el docente avisó antes |
| Hora actual indicada por el comando | 2026-10-13 09:00 |
| **Tiempo restante** | **≈ 30 h 45 min** respecto a la referencia (menos si el aviso del docente fue antes de las 15:45) |
| Aviso | El contexto del sistema indica fecha 2026-10-14; si es la real, quedan ≤ 6 h 45 min. **Verificar el reloj real ya.** |

El ODP recibió el aviso a las 15:45, pero la toma de conocimiento cuenta desde que cualquier persona de la organización lo supo (`knowledge/marco-normativo-peru.md` §2). Se usa la lectura más temprana.

## Clasificación
- **Incidente de seguridad de datos personales (brecha)**, confirmado por el reporte. Dato verificado: ninguno, porque el contexto no trae logs ni el archivo.
- **Tipo:** Confidencialidad (exposición no autorizada, art. III num. 16).
- **Categoría:** FUG, archivo público por error. Podría tener un componente INT si hubo accesos de terceros `[sin evidencia]`.
- **Prioridad: P1 Crítica.** Hay datos financieros y de remuneración expuestos públicamente, indexados en un buscador, y la contención aún no está verificada. Si no se considera P1, es P2 como mínimo.
- **Entorno digital:** sí (nube), así que aplica CNSD (art. 34.5).
- **Rol de la UNSA:** responsable del tratamiento. La analista es personal interno, no encargada. El proveedor de la nube gratuita sería un tercero sin contrato `[VERIFICAR]`.

## Hechos por nivel
| Nivel | Hecho | Fuente |
|---|---|---|
| Reportado | Hoja de cálculo en la nube con la planilla CAS, compartida como "cualquier persona con el enlace", hallada vía buscador por un docente | `_entradas/job1791983369011.md:9` |
| Reportado | ~5 semanas de exposición según el historial (inicio aprox. 2026-09-07) | ídem:9 |
| Reportado | ~320 trabajadores; nombres, DNI, cargo, dependencia, cuenta bancaria, remuneración, descuentos | ídem:11 |
| Reportado | Subida por una analista para compartirla con contabilidad | ídem:11 |
| Reportado | RR. HH. la puso en privado (hora NO INDICADA) | ídem:11 |
| Reportado | No se sabe cuántas veces se abrió; la plataforma gratuita no da ese detalle | ídem:11 |
| Verificado | Existen 320 trabajadores CAS dentro de 3 100 de personal; planillas en hojas de cálculo y sistema, sin cifrado, respaldo parcial | `demo/unsa-base/inventario/activos-y-datos.md:14`, `:27` |
| Verificado | Los archivos con datos personales se comparten por enlace en la nube sin política aprobada | `activos-y-datos.md:35`; `politicas/documento-seguridad-extracto.md:26` |
| Verificado | No hay procedimiento ni plazos de notificación a la ANPD, ni responsable definido | `documento-seguridad-extracto.md:19` |
| Verificado | Los incidentes se reportan a la OTI, que decide si escala al ODP | `documento-seguridad-extracto.md:17-18` |
| Supuesto | Que el enlace sigue indexado o con copias en caché del buscador | — |
| Supuesto | Que alguien además del docente accedió o descargó el archivo | — |
| Supuesto | Que el "privado" funciona y no hay otras copias o enlaces | — |

No hay carpeta `logs/` en el contexto, así que no se puede verificar accesos ni exfiltración.

## Observaciones del triaje
- El docente halló el archivo buscando su propio nombre. Eso indica indexación pública, y una indexación abierta amplía la probabilidad de acceso por desconocidos.
- Duda sobre datos personales: ninguna; hay DNI y nombres completos.
- Los "descuentos" pueden revelar datos adicionales (retenciones judiciales, afiliación sindical, préstamos) `[VERIFICAR columnas reales]`.

## Siguiente paso
Brecha de datos personales, así que pasa a evaluación de severidad (`02-evaluacion-severidad.md`).
