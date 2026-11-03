# Evaluación de severidad — INC-20260929-laptop-robada-financiera

- **Insumo:** `salidas/INC-20260929-laptop-robada-financiera/01-ficha-incidente.md`
- **Metodología:** ENISA (2013), SE = DPC × EI + CB. Ver `knowledge/metodologia-severidad.md`

## 1. Cálculo

| Factor | Valor | Justificación |
|---|---|---|
| DPC base | 4 | El dato más delicado afectado son los **ingresos mensuales declarados**: ingresos económicos, dato sensible en Perú (Ley 29733) |
| Ajuste de contexto | +0 (ya está en el máximo) | El contexto agrava el daño: DNI + dirección + deuda + morosidad + ingresos permiten perfilar a socios en situación financiera vulnerable. Como el máximo es 4, no se suma más |
| **DPC final** | **4** | |
| **EI** | **1** | Identificación directa (nombre completo + DNI). **No** se reduce por cifrado porque no está confirmado que BitLocker estuviera activo, y una contraseña de Windows no protege el disco extraído (inferencia técnica) |
| CB — confidencialidad | +0,5 | Datos en poder de destinatarios **desconocidos** (autor del robo y quien adquiera el equipo) |
| CB — integridad | 0 | No hay indicios de alteración. El Excel es una copia (inferencia) |
| CB — disponibilidad | 0 | Se presume que el original está en el sistema de créditos y se recupera sin dificultad (**inferencia, por confirmar**. Si el Excel tenía información que solo existía localmente, +0,25) |
| CB — intención maliciosa | +0,5 | Robo (acto deliberado). Aunque el objetivo probable fuera el equipo y no los datos, la metodología puntúa el robo como intención maliciosa |
| **CB total** | **1,0** | 0,5 + 0 + 0 + 0,5 |

**SE = 4 × 1 + 1,0 = 5,0 → Severidad MUY ALTA** (≥ 4)

**Análisis de sensibilidad (escenario alternativo, no aplicado):** si se demuestra que BitLocker estaba activo con un algoritmo robusto y la clave no estaba comprometida, quedaría EI = 0,25 y CB de confidencialidad = 0, con lo que SE = 4 × 0,25 + 0,5 = **1,5 (Baja)**. Aun así, la sesión abierta del correo sigue siendo un riesgo independiente del cifrado del disco si el equipo estaba encendido, suspendido o desbloqueado (inferencia). **Hoy no hay evidencia del cifrado: se usa el escenario de SE = 5,0.**

## 2. Consecuencias probables para los titulares
| Consecuencia | Probabilidad | Motivo |
|---|---|---|
| Fraude telefónico o por mensaje haciéndose pasar por la cooperativa (cobranzas falsas, "regularice su deuda en esta cuenta") | Alta | El atacante conoce el monto del crédito, las cuotas atrasadas y el teléfono, lo que hace el engaño muy creíble |
| Suplantación de identidad (créditos, líneas telefónicas o trámites a nombre del socio) | Media | Nombre + DNI + dirección + ingresos bastan para muchos trámites |
| Extorsión o presión a socios morosos | Media | La exposición de la morosidad puede usarse para presionar o amenazar |
| Daño reputacional o discriminación (por ejemplo, ante empleadores o en la comunidad) por la difusión de deudas e ingresos | Media | Datos de situación económica personal |
| Riesgo para la seguridad patrimonial o física (dirección + ingresos) | Baja | Posible selección de víctimas por nivel de ingresos (inferencia) |
| Exposición de otros datos de socios o terceros contenidos en el correo institucional | Desconocida (en investigación) | Sesión de correo abierta en el equipo robado |

## 3. Decisión de notificación (D.S. 016-2024-JUS)

| Obligación | Supuesto evaluado | ¿Se cumple? | Fundamento |
|---|---|---|---|
| Notificar a la ANPD (art. 34.1) | Datos sensibles | **Sí** | Ingresos económicos declarados de ~1 500 socios |
| | Grandes volúmenes (cantidad o tipo) | Duda / probable Sí | Por el **tipo** de datos (identificación + financieros + sensibles en un solo archivo). El reglamento no fija umbral `[VERIFICAR lineamientos ANPD]` |
| | Gran número de personas | Duda | ~1 500 socios. No hay umbral oficial `[VERIFICAR lineamientos ANPD]`. Ante la duda, se considera |
| | Perjuicio evidente a derechos o libertades | **Probable Sí** | SE = 5,0 (≥ 3): criterio de apoyo de la metodología. Riesgo alto de fraude dirigido |
| **Resultado ANPD** | | **NOTIFICAR (obligación probable)** | Basta un supuesto: datos sensibles |
| Comunicar a titulares (art. 34.3 / 34.4) | Afectación a otros derechos del titular | **Sí, comunicar** | SE Muy alta. La excepción del art. 34.4 **no aplica**: la laptop no se recuperó y el incidente no fue superado totalmente. Plazo: 48 h, sin dilación indebida |
| Notificar al CNSD (art. 34.5) | Entorno digital | **Duda: se recomienda notificar** | Hay datos en soporte digital y una sesión de correo en la nube expuesta (posible acceso mediante el entorno digital). Ante la duda, notificar `[VERIFICAR alcance con asesoría legal]` |
| Documentar (art. 35) | Siempre | **Sí** | Ver `04-respuesta-y-cierre.md`, sección 5 |

## 4. Plazos
- **Toma de conocimiento:** 2026-09-29 ~21:00. Es el momento del robo, conocido por el propio trabajador (criterio "¿Desde cuándo corren las 48 horas?" de `knowledge/marco-normativo-peru.md`: cuenta el primer momento en que cualquier persona de la organización lo supo; se aplica la lectura más temprana).
- **Hora límite (48 h):** **2026-10-01 21:00 (HOY).** Tiempo restante: menos de 24 h. El agente no conoce la hora actual: restar la hora actual de las 21:00.
- **Referencia (lectura alternativa):** conocimiento del ODP el 2026-09-30 09:10, con límite el 2026-10-02 09:10. **No se recomienda usarla** para planificar.
- Si la notificación sale después de las 21:00 de hoy, debe incluir los **motivos de la demora** (art. 34.1). La sección H de `03-notificacion-anpd.md` ya trae un texto de contingencia.

## 5. Nota aparte: impacto para la organización
- No notificar cuando corresponde es una **infracción grave** (art. 133 num. 12). Rango de multa: `[VERIFICAR art. 39 de la Ley 29733]`.
- Hay riesgo reputacional y de confianza de los socios, y un posible interés de un supervisor sectorial (SBS) `[VERIFICAR: fuera de knowledge/]`.
- Se evidencian brechas de control: no hay política de descarga de datos a portátiles, no se sabe si el cifrado es uniforme y el reporte se hizo por un canal no institucional (art. 46.4).

## 6. Supuestos e información pendiente
- Supuesto: el disco **no** estaba cifrado (peor caso razonable mientras no haya evidencia).
- Supuesto: los socios afectados son mayores de edad (inferencia, NO INDICADO).
- Supuesto: los datos originales existen en el sistema de créditos (disponibilidad recuperable).
- Pendiente: el estado de BitLocker, los accesos al correo después del robo, el número exacto de socios y el contenido del buzón.

---
*Borrador de apoyo. La decisión de notificar la toma el responsable del tratamiento con el Oficial de Datos Personales.*
