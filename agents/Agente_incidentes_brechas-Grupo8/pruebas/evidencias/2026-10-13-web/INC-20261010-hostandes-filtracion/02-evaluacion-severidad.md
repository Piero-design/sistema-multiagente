# 02 · Evaluación de severidad — INC-20261010-hostandes-filtracion

> BORRADOR para revisión humana. Metodología: ENISA 2013 (`knowledge/metodologia-severidad.md`).

## Puntuación: SE = DPC × EI + CB
| Componente | Valor | Justificación |
|---|---|---|
| DPC | **2** | Datos simples (base 1: identificación, contacto, datos académicos, estado de pagos). **+1** por ser mayoritariamente menores de edad y porque el conjunto (DNI + fecha de nacimiento + dirección + apoderado) permite suplantación y perfilado. No hay datos sensibles ni de tarjetas (reportado). |
| EI | **1** | Identificación directa: nombre completo + DNI + dirección + contacto. |
| CB | **1,0** | Confidencialidad +0,5 (destinatario desconocido, copia posiblemente en poder de un tercero no autorizado). Intención maliciosa +0,5 (acceso no autorizado deliberado). Integridad y disponibilidad: 0 (sin indicios; `[VERIFICAR]` con HostAndes). |

**SE = 2 × 1 + 1,0 = 3,0 → ALTA** (3 a < 4).

Sensibilidad: si las contraseñas estuvieran sin cifrar o con hash débil, aumenta el riesgo de acceso a cuentas y de reutilización en otros servicios. Es un factor agravante pendiente. No cambia el nivel calculado, pero refuerza la urgencia.

## Decisión (art. 34, `metodologia-severidad.md` §5)
| Pregunta | Respuesta | Consecuencia |
|---|---|---|
| ¿Datos sensibles? | No (reportado). Atención: datos de menores, pero no son "sensibles" en la lista del proyecto | — |
| ¿Gran volumen / gran número? | Probable: ~2 400 titulares, muchos menores. No hay umbral oficial `[VERIFICAR lineamientos ANPD]` | **Notificar a la ANPD** (34.1) |
| ¿Perjuicio evidente a otros derechos o libertades? | Probable: SE ≥ 3, riesgo de suplantación, fraude y contacto indebido a menores | **Notificar a la ANPD** y **comunicar a titulares** (34.1, 34.3) |
| ¿Entorno digital? | Sí | **Notificar al CNSD** (34.5) |
| ¿Superado totalmente? | No. No se puede descartar la descarga | No aplica la excepción del 34.4 |

**Conclusión:** notificar a la ANPD (art. 34.1/34.2) dentro de las 48 h, comunicar a los titulares (apoderados, en el caso de menores) (34.3), avisar al CNSD (34.5) y documentar (art. 35). Aunque la descarga no está confirmada, la duda favorece notificar. Se puede indicar en la notificación que la información es preliminar y que se ampliará.

## Dudas que no frenan la notificación
- Cantidad exacta de titulares, tablas afectadas y cifrado de contraseñas. Se declaran como "por confirmar".
- Si las contraseñas estaban en claro, ampliar la comunicación a los titulares con la recomendación de cambiarlas.
