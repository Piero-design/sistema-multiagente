# Ficha de incidente — INC-20260929-laptop-robada-cooperativa

> Fuente: `examples/entradas/caso-03-laptop-robada-financiera.md` (caso ficticio). La entrada no trae datos personales reales de socios; se trabaja solo con categorías y cantidades.
> Convención: **(hecho)** = lo reportado; **(inferencia)** = deducción del agente; **NO INDICADO** = no consta.

- **Organización (responsable del tratamiento):** Cooperativa Misti Ahorro — RUC: NO INDICADO
- **Reportado por:** Analista de créditos (personal propio) → su jefe → Oficial de Datos Personales. ¿Es encargado del tratamiento? **No** (es trabajador del responsable; el art. 36 no aplica, la obligación de notificar es de la cooperativa).
- **Canal de reporte:** WhatsApp del analista al jefe; reenvío del jefe al Oficial de Datos Personales.

## 1. Línea de tiempo

| Hito | Fecha y hora | Fuente / certeza |
|---|---|---|
| Ocurrencia del incidente (robo de la mochila con la laptop en un bus) | 2026-09-29, ~21:00 | Estimado: "anoche como a las 21:00"; la fecha 29/09 es inferencia a partir del reenvío del 30/09 |
| **Toma de conocimiento** (inicia el plazo) | **2026-09-29, ~21:00** (criterio conservador) | Inferencia: el analista, trabajador de la cooperativa, supo del robo en ese momento. Ver nota |
| Aviso del analista al jefe (WhatsApp) | NO INDICADO (entre la noche del 29/09 y las 09:10 del 30/09) | NO INDICADO |
| Reporte al Oficial de Datos Personales | 2026-09-30, 09:10 | Hecho |
| **Hora límite de notificación (48 h, art. 34.1)** | **2026-10-01, 21:00** (criterio conservador) | Calculada: 29/09 21:00 + 48 h |
| Hora límite alternativa (si se cuenta desde el reenvío al ODP) | 2026-10-02, 09:10 | Calculada: 30/09 09:10 + 48 h. **No se recomienda usarla** |

**Nota sobre el reloj:** el reglamento cuenta 48 h "desde que se tomó conocimiento". El analista es personal de la cooperativa, por lo que su conocimiento puede considerarse conocimiento del responsable (inferencia, `[VERIFICAR criterio con asesoría legal]`). **Hoy es 2026-10-01: según el criterio conservador, el plazo vence hoy a las 21:00.** Hay que notificar antes de esa hora.

## 2. Descripción de lo ocurrido
La noche del 29/09/2026 (aprox. 21:00) le robaron a un analista de créditos, en un bus, la mochila con una laptop de la cooperativa (hecho). El analista ya puso la denuncia en una comisaría (hecho; no se adjunta constancia). En la laptop había un Excel descargado con la cartera de sus clientes, unos 1 500 socios (hecho, cantidad aproximada). No se sabe si el disco estaba cifrado con BitLocker (hecho: soporte responde "algunas sí, otras no"). El navegador tenía abierta la sesión del correo institucional (hecho), por lo que quien tenga la laptop podría leer y enviar correos de la cooperativa si logra pasar la contraseña de Windows o si el equipo estaba suspendido sin bloqueo (inferencia). No hay política escrita sobre descargar bases de clientes a equipos portátiles (hecho).

## 3. Decisión de triaje
- **Resultado:** ☐ Evento sin incidente ☐ Incidente de seguridad (sin datos personales) ☒ **Incidente de seguridad de datos personales (brecha)**
- **Fundamento** (art. III num. 16, D.S. 016-2024-JUS; ISO/IEC 27035-1, fase "Evaluar y decidir"): hay **pérdida** del soporte y posible **exposición no autorizada** de datos personales de unos 1 500 socios a un tercero desconocido (el ladrón). Mientras no se confirme el cifrado del disco, se trata como **exposición probable**. Una contraseña de Windows sin cifrado no protege el contenido del disco (inferencia técnica).

## 4. Clasificación
- **Tipo:** ☒ Confidencialidad ☐ Integridad ☒ Disponibilidad (pérdida del equipo; se presume que el Excel es una copia y el original sigue en el sistema de créditos: inferencia, `[VERIFICAR]`). Integridad: sin evidencia, pero posible vía el correo con la sesión abierta (vigilar).
- **Categoría:** **FIS**, pérdida o robo físico. Riesgo secundario **INT**: acceso no autorizado al correo institucional por la sesión abierta.
- **Entorno digital:** **Dudoso.** El robo es físico, pero los datos son digitales y el correo institucional podría usarse desde el equipo robado. → Notificación adicional al CNSD (art. 34.5): **se recomienda notificar** ante la duda (`[VERIFICAR alcance de "entorno digital" con el CNSD]`).
- **Prioridad:** **P1 Crítica**, subida desde P2 (brecha confirmada con datos personales) por tres motivos: (a) hay datos sensibles (ingresos económicos); (b) la sesión de correo abierta es un vector de acceso que podría seguir activo; (c) el plazo de 48 h vence hoy según el criterio conservador. La subida es una inferencia del agente.

## 5. Datos y titulares afectados

| Categoría de datos | ¿Sensible? | Categoría de titulares | ¿Menores? | N.° aprox. de titulares | Certeza |
|---|---|---|---|---|---|
| Identificación: nombre, DNI | No | Socios con crédito (cartera del analista) | NO INDICADO (en principio no, porque son titulares de crédito: inferencia) | ~1 500 | Hecho (aprox.) |
| Contacto: dirección, teléfono | No | Ídem | — | ~1 500 | Hecho (aprox.) |
| Financieros: monto del crédito, cuotas atrasadas | No (financiero; agrava el riesgo de fraude y extorsión) | Ídem | — | ~1 500 (cuotas atrasadas: solo una parte; cantidad NO INDICADA) | Hecho |
| **Ingresos mensuales declarados** | **Sí** (ingresos económicos: dato sensible, Ley 29733) | Ídem | — | ~1 500 | Hecho |
| Contenido del correo institucional (adjuntos, conversaciones con socios) | NO INDICADO | Socios, personal, terceros | NO INDICADO | NO INDICADO | Inferencia: posible exposición adicional |

## 6. Sistemas, activos y terceros involucrados
- Laptop institucional (modelo, n.° de serie y n.° de activo: NO INDICADO); estado de BitLocker: **desconocido**.
- Archivo Excel con la cartera de clientes, exportado del sistema de créditos (sistema de origen: NO INDICADO).
- Cuenta de correo institucional del analista (sesión abierta en el navegador; proveedor de correo: NO INDICADO).
- Credenciales que el navegador pudiera tener guardadas (VPN, sistema de créditos, otros): NO INDICADO (inferencia de riesgo).
- Terceros: Policía Nacional (denuncia). Sin encargados del tratamiento involucrados según el reporte.

## 7. Medidas ya adoptadas (según el reporte)
- Denuncia policial presentada por el analista (hecho; constancia no adjunta).
- Reporte al jefe y reenvío al Oficial de Datos Personales (hecho).
- No consta ninguna medida técnica: no se cerró la sesión de correo, no se cambiaron credenciales, no se hizo bloqueo ni borrado remoto (NO INDICADO).

## 8. Acciones inmediatas sugeridas
| # | Acción | Objetivo | Responsable sugerido |
|---|---|---|---|
| 1 | **Cerrar todas las sesiones** de la cuenta de correo del analista, cambiar su contraseña y la de todo servicio que pudiera estar guardado en el navegador; activar o exigir MFA. Revisar reglas de reenvío y enviados recientes | Contener (vector INT) | TI / administrador de correo |
| 2 | **Antes de cerrar sesiones, exportar los registros de inicio de sesión y de actividad** de la cuenta de correo (y del sistema de créditos para la exportación del Excel), con fecha y hora y hash | Preservar evidencia (art. 46.3; ISO/IEC 27002 5.28) | TI / seguridad |
| 3 | **Confirmar en la consola** (AD/Intune/MDM u otra) si la laptop tenía BitLocker activo y si la clave de recuperación está custodiada; guardar una captura como evidencia | Informar (cambia la severidad) | Soporte / TI |
| 4 | Si existe gestión remota: **bloquear** el equipo y, tras registrar su estado (cifrado, última conexión), ordenar el **borrado remoto**. Revocar el equipo en el dominio/VPN | Contener | TI, con aprobación del responsable de seguridad |
| 5 | Obtener la **constancia de la denuncia policial** y una declaración escrita del analista (hora del robo, contenido de la laptop, otros archivos descargados) | Preservar evidencia / informar | Jefe del área + Oficial de Datos Personales |

## 9. Preguntas pendientes
1. **(Crítica)** Hora exacta en que el jefe recibió el WhatsApp, y confirmación del criterio para contar el plazo. Mientras tanto, el plazo vence el **01/10/2026 a las 21:00**.
2. **(Crítica)** ¿La laptop tenía BitLocker activo? ¿Se comprometió la clave (por ejemplo, la clave anotada junto al equipo)? ¿El equipo estaba apagado, suspendido o bloqueado al momento del robo?
3. ¿Hay actividad anómala en el correo institucional después de las 21:00 del 29/09?
4. ¿Qué otros archivos o credenciales había en la laptop o en el navegador?
5. Número exacto de socios del Excel y cuántos tienen cuotas atrasadas.
6. Nombre y datos de contacto del Oficial de Datos Personales y RUC de la cooperativa (necesarios para la notificación).
7. Banco de datos afectado y su código de inscripción, si existe.

## 10. Siguiente paso
☐ Cerrar como evento ☒ Pasar a `brecha-evaluacion-severidad`

---
*Borrador de apoyo. Debe validarlo el Oficial de Datos Personales / responsable de seguridad.*
