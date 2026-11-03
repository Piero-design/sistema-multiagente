# Evaluación de severidad — INC-20260929-laptop-robada-cooperativa

- **Insumo:** `salidas/INC-20260929-laptop-robada-cooperativa/01-ficha-incidente.md`
- **Metodología:** ENISA (2013), SE = DPC × EI + CB (ver `knowledge/metodologia-severidad.md`)
- **Supuesto de trabajo:** el disco **no** estaba cifrado, porque no se ha confirmado el cifrado. Se incluye abajo el escenario alternativo.

## 1. Cálculo (escenario base: sin cifrado confirmado)

| Factor | Valor | Justificación |
|---|---|---|
| DPC base | 4 | Dato más delicado afectado: ingresos mensuales declarados (ingresos económicos, dato sensible en Perú según la Ley 29733) |
| Ajuste de contexto | +0 (ya en el máximo de 4) | El conjunto (DNI + dirección + teléfono + deuda + cuotas atrasadas + ingresos) permite perfilar y extorsionar. Agravaría el puntaje, pero DPC no puede pasar de 4 |
| **DPC final** | **4** | |
| **EI** | **1** | Máxima: nombre completo + DNI permiten identificación directa |
| CB — confidencialidad | +0,5 | Datos en poder de un tercero desconocido (ladrón), con posible reventa o difusión |
| CB — integridad | 0 | Sin evidencia de alteración. Se vigila el correo con la sesión abierta (inferencia) |
| CB — disponibilidad | 0 | El Excel sería una copia y el original seguiría en el sistema de créditos (inferencia, `[VERIFICAR]`) |
| CB — intención maliciosa | +0,5 | Robo (acto deliberado), aunque el objetivo probable era el equipo y no los datos (inferencia) |
| **CB total** | **1,0** | 0,5 + 0 + 0 + 0,5 |

**SE = 4 × 1 + 1,0 = 5,0 → Severidad Muy alta** (SE ≥ 4)

### Escenario alternativo (solo si se confirma BitLocker activo, equipo apagado o bloqueado y clave no comprometida)
EI = 0,25; CB confidencialidad = 0; se mantiene la intención maliciosa = +0,5.
SE = 4 × 0,25 + 0,5 = **1,5 → Baja**. Aun así, quedaría por resolver el riesgo de la **sesión de correo abierta**: si el equipo estaba suspendido con la sesión desbloqueada, el cifrado del disco no protege lo que está en uso. Mientras no haya evidencia, **se mantiene el escenario base**.

## 2. Consecuencias probables para los titulares
| Consecuencia | Probabilidad | Motivo |
|---|---|---|
| Fraude por suplantación de la cooperativa ("cobranza" o "refinanciamiento" falsos) | Alta | El atacante sabe el monto del crédito, las cuotas atrasadas y el teléfono de cada socio. Puede hacer llamadas creíbles |
| Extorsión o presión indebida a socios con deudas atrasadas | Media | La deuda, la dirección y el teléfono permiten amenazar o avergonzar |
| Suplantación de identidad (créditos o líneas a nombre del socio) | Media | Nombre + DNI + dirección + ingresos bastan para solicitudes fraudulentas |
| Riesgo para la seguridad física o patrimonial (robo, secuestro al paso) | Baja-Media | Se conocen la dirección y el nivel de ingresos (perfilamiento de víctimas) |
| Phishing desde el correo institucional real | Media (si la sesión siguió activa) | Un correo legítimo de la cooperativa sería muy creíble para los socios |
| Daño reputacional o discriminación (exposición de morosidad e ingresos) | Media | La información de deudas e ingresos afecta la vida privada |

## 3. Decisión de notificación (D.S. 016-2024-JUS)

| Obligación | Supuesto evaluado | ¿Se cumple? | Fundamento |
|---|---|---|---|
| Notificar a la ANPD (art. 34.1) | Datos sensibles | **Sí** | Ingresos mensuales declarados de unos 1 500 socios |
| | Grandes volúmenes (cantidad o tipo) | Duda → probable Sí por **tipo** | Combinación identificativa + financiera + sensible. Sin umbral oficial `[VERIFICAR lineamientos ANPD]` |
| | Gran número de personas | Duda | ~1 500 personas; el reglamento no fija umbral `[VERIFICAR lineamientos ANPD]` |
| | Perjuicio evidente a derechos o libertades | **Sí (probable)** | SE Muy alta (5,0); hay riesgo concreto de fraude y extorsión |
| **Resultado ANPD** | | **Notificar (obligación probable)** | Basta un supuesto; aquí se cumplen al menos dos |
| Comunicar a titulares (art. 34.3 / 34.4) | Afectación a otros derechos del titular | **Sí, comunicar** | La excepción del art. 34.4 no aplica: la laptop no se recuperó y el incidente **no** está superado totalmente |
| Notificar al CNSD (art. 34.5) | Entorno digital | **Duda → recomendar notificar** | Datos digitales y posible acceso al correo institucional; robo físico como origen `[VERIFICAR]` |
| Documentar (art. 35) | Siempre | **Sí** | Registro en `04-respuesta-y-cierre.md` |

## 4. Plazos
- **Toma de conocimiento:** 2026-09-29, ~21:00 (criterio conservador: el analista es personal del responsable).
- **Hora límite (48 h):** **2026-10-01, 21:00**. Hoy es 2026-10-01; la hora actual no está disponible para el agente. **Quedan menos de 24 h; el plazo vence hoy.**
- Si se adopta el criterio del reenvío al ODP (30/09 09:10), el límite sería el 02/10 09:10. **No se recomienda** apoyarse en él.
- Si la notificación sale después de las 21:00 de hoy, debe incluir los **motivos de la demora** (art. 34.1). Ya se dejó preparada esa sección en el borrador.
- Comunicación a titulares: también dentro de las 48 h y sin dilación indebida (art. 34.3).

## 5. Nota aparte: impacto para la organización
- No notificar cuando corresponde es una **infracción grave** (art. 133, num. 12); multa según el art. 39 de la Ley 29733 `[VERIFICAR rango en UIT]`.
- La obligación de notificar se mantiene aunque la cooperativa considere el incidente resuelto (art. 34.1).
- Hay riesgo reputacional y de confianza de los socios, y posible interés del supervisor sectorial `[VERIFICAR obligaciones sectoriales de cooperativas: fuera de knowledge/]`.
- La falta de política sobre descargas a portátiles y la falta de inventario de cifrado son debilidades de control que la ANPD podría revisar (arts. 46.4 y 48.1).

## 6. Supuestos e información pendiente
- Supuesto: disco sin cifrar hasta prueba en contrario (determina el SE de 5,0 frente a 1,5).
- Supuesto: el Excel es copia del sistema de créditos (disponibilidad = 0).
- Pendiente: hora del aviso al jefe; estado de BitLocker; actividad en el correo; n.° exacto de socios y de socios con cuotas atrasadas; si hay menores entre los titulares (en principio no).

---
*Borrador de apoyo. La decisión de notificar la toma el responsable del tratamiento con el Oficial de Datos Personales.*
