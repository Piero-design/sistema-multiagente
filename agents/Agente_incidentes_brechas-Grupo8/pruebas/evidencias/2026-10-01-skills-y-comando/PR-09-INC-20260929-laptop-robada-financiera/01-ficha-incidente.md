# Ficha de incidente — INC-20260929-laptop-robada-financiera

> Caso ficticio de prueba (`examples/entradas/caso-03-laptop-robada-financiera.md`). El reporte no trae datos personales de socios concretos: aquí solo se usan categorías y cantidades.

- **Organización (responsable del tratamiento):** Cooperativa Misti Ahorro (RUC: NO INDICADO)
- **Reportado por:** analista de créditos (trabajador de la cooperativa). Su jefe inmediato lo reenvió al Oficial de Datos Personales (ODP). ¿Es encargado del tratamiento? **No.** Es personal propio del responsable, así que no aplica el art. 36. La obligación de notificar es de la cooperativa (art. 34.1).
- **Canal de reporte:** WhatsApp del trabajador a su jefe (canal no institucional) y luego reenvío del jefe al ODP.

## 1. Línea de tiempo

| Hito | Fecha y hora | Fuente / certeza |
|---|---|---|
| Ocurrencia del incidente (robo de la mochila con la laptop en un bus) | **2026-09-29 ~21:00** | Hecho reportado ("anoche como a las 21:00"). La fecha es **inferencia**: "anoche" se toma respecto del mensaje reenviado el 30/09. La hora es aproximada |
| Denuncia policial | NO INDICADO (entre el robo y el 30/09 09:10) | Hecho reportado sin hora |
| Mensaje del trabajador a su jefe (WhatsApp) | NO INDICADO | Pendiente: obtener la captura con la hora |
| **Toma de conocimiento** (inicia el plazo) | **2026-09-29 ~21:00** (el trabajador víctima del robo) | Criterio prudente de `knowledge/marco-normativo-peru.md`, sección "¿Desde cuándo corren las 48 horas?": cuenta el primer momento en que **cualquier persona de la organización** supo con certeza razonable del incidente. El trabajador sabía que le robaron la laptop y que tenía el Excel de la cartera |
| Reporte al responsable / ODP | 2026-09-30 09:10 | Hecho (hora del reenvío) |
| **Hora límite de notificación (48 h, art. 34.1)** | **2026-10-01 21:00 (HOY)** | Calculada con la lectura más temprana |
| Hora límite de referencia (lectura alternativa: conocimiento del ODP) | 2026-10-02 09:10 | Solo como referencia. **No se usa para planificar** `[VERIFICAR con lineamientos ANPD o asesoría legal]` |

> **Alerta de reloj:** a la fecha de este borrador (2026-10-01) quedan **menos de 24 h** y el plazo vence **hoy a las 21:00**. El agente no conoce la hora actual. Tiempo restante = 21:00 menos la hora actual.

## 2. Descripción de lo ocurrido
El 29/09/2026, a eso de las 21:00, le robaron a un analista de créditos la mochila con su laptop institucional mientras viajaba en bus. El analista presentó la denuncia en una comisaría. La laptop tenía guardado localmente un archivo Excel con la cartera de sus clientes, unos **1 500 socios**: nombre, DNI, dirección, teléfono, monto del crédito, cuotas atrasadas e **ingresos mensuales declarados**. El equipo tiene contraseña de Windows, pero **no se sabe si el disco estaba cifrado** (BitLocker). La laptop tenía la **sesión del correo institucional abierta en el navegador**, así que existe un riesgo de acceso no autorizado al buzón y a los datos que contenga (inferencia). No hay una política escrita sobre descargar bases de clientes a equipos portátiles.

## 3. Decisión de triaje
- **Resultado:** ☐ Evento sin incidente ☐ Incidente de seguridad (sin datos personales) ☒ **Incidente de seguridad de datos personales (brecha)**
- **Fundamento** (art. III num. 16, D.S. 016-2024-JUS; ISO/IEC 27035-1, fase "Evaluar y decidir"; ISO/IEC 27701:2019 6.13.1.5): hubo una vulneración de la seguridad (robo del equipo) que causa la **pérdida** de un soporte con datos personales y una **exposición no autorizada** probable a terceros desconocidos. No hay evidencia de cifrado, y una contraseña de Windows por sí sola no protege el contenido del disco si este se extrae (inferencia técnica). Mientras no se demuestre el cifrado, se trata como brecha.

## 4. Clasificación
- **Tipo:** ☒ Confidencialidad ☐ Integridad ☒ Disponibilidad (pérdida del soporte. Se presume que los datos originales siguen en el sistema de créditos: **inferencia**, por confirmar)
- **Categoría:** **FIS**, pérdida o robo físico. Riesgo asociado de **INT** (acceso no autorizado) por la sesión abierta del correo institucional.
- **Entorno digital:** **Duda razonable / probable Sí**. Los datos están en soporte digital y hay una sesión de correo en la nube expuesta a quien tenga la laptop. Notificación adicional al CNSD (art. 34.5): **se recomienda notificar** (ante la duda) `[VERIFICAR alcance de "entorno digital" con asesoría legal]`.
- **Prioridad:** **P1 Crítica**. Hay datos sensibles (ingresos económicos) expuestos a terceros desconocidos, una sesión de correo posiblemente activa en manos de terceros (riesgo en curso) y el plazo de 48 h vence hoy. (Por la tabla sería al menos P2. Se sube a P1 por el riesgo en curso del correo y por el reloj, que es **inferencia** del analista.)

## 5. Datos y titulares afectados

| Categoría de datos | ¿Sensible? | Categoría de titulares | ¿Menores? | N.° aprox. de titulares | Certeza |
|---|---|---|---|---|---|
| Identificación: nombre, DNI | No | Socios con crédito vigente de la cartera del analista | NO INDICADO (presumiblemente no, por tratarse de créditos: inferencia) | ~1 500 | Estimado por el jefe |
| Contacto: dirección, teléfono | No | Mismos | Mismo | ~1 500 | Estimado |
| Financieros: monto del crédito, cuotas atrasadas (morosidad) | No (financiero; dato delicado) | Mismos (un subconjunto con morosidad, cantidad NO INDICADA) | Mismo | ≤ 1 500 | Estimado |
| **Ingresos mensuales declarados** | **Sí** (ingresos económicos: dato sensible según la Ley 29733) | Mismos | Mismo | ~1 500 | Estimado |
| Contenido del buzón de correo institucional (posible información de socios, de terceros y de la propia cooperativa) | NO INDICADO | NO INDICADO | NO INDICADO | NO INDICADO, **en investigación** | Desconocido |

## 6. Sistemas, activos y terceros involucrados
- Laptop institucional asignada al analista (marca, serie, ID de inventario: NO INDICADO).
- Archivo Excel con la cartera de clientes, descargado del sistema de créditos (nombre del sistema: NO INDICADO).
- Cuenta de correo institucional del analista, con la sesión abierta en el navegador (proveedor: NO INDICADO).
- Otras credenciales posiblemente guardadas en el navegador o el equipo (VPN, sistema de créditos): NO INDICADO.
- Terceros: autor del robo (desconocido) y Policía Nacional (denuncia).

## 7. Medidas ya adoptadas (según el reporte)
- Denuncia policial presentada por el trabajador (número y hora: NO INDICADO).
- Reenvío del reporte al ODP (30/09 09:10).
- No se reporta ninguna medida técnica: ni cierre de sesiones, ni cambio de contraseña, ni bloqueo o borrado remoto.

## 8. Acciones inmediatas sugeridas
| # | Acción | Objetivo | Responsable sugerido |
|---|---|---|---|
| 1 | **Cerrar todas las sesiones y revocar los tokens** de la cuenta de correo del analista, cambiar su contraseña y activar MFA. Hacer lo mismo con cualquier credencial que pueda estar guardada en el navegador (sistema de créditos, VPN). **Antes**, exportar los registros de acceso al correo desde el 29/09 21:00 | Contener (riesgo en curso) y preservar evidencia | TI / Seguridad |
| 2 | Revisar los **registros de acceso del correo** desde el 29/09 ~21:00 (IP, dispositivo, reenvíos, reglas nuevas en el buzón, correos enviados) para detectar uso indebido | Preservar evidencia / investigar | Seguridad |
| 3 | **Confirmar el estado de BitLocker** de esa laptop (consola de gestión, clave de recuperación custodiada en AD/Entra/MDM) y, si hay MDM, ordenar el **bloqueo y borrado remoto** después de registrar el estado del equipo (último contacto, cifrado) | Contener / determinar la exposición real | TI |
| 4 | Identificar en los **logs de exportación** del sistema de créditos (art. 46.3) el archivo exacto descargado: fecha, campos y número exacto de socios | Precisar el alcance para la notificación | TI / Riesgos |
| 5 | Obtener la **copia de la denuncia policial** y la captura del WhatsApp con su hora. Convocar hoy al ODP y a la gerencia para aprobar la notificación a la ANPD **antes de las 21:00** | Informar / evidencia / plazo | ODP / Jefatura |

## 9. Preguntas pendientes
1. **PENDIENTE CRÍTICA:** ¿la hora del robo (~21:00 del 29/09) es correcta? ¿A qué hora envió el trabajador el WhatsApp a su jefe? Esto define la toma de conocimiento.
2. ¿El disco de la laptop estaba cifrado con BitLocker? ¿Hay evidencia en la consola de gestión?
3. ¿Hubo accesos al correo institucional después del robo?
4. ¿Número exacto de socios y campos del Excel? ¿Hay otros archivos con datos personales en la laptop (descargas, caché del correo)?
5. ¿Hay MDM o herramienta de borrado remoto?
6. Nombre, correo y teléfono del ODP (punto de contacto, art. 34.2 num. 2); razón social y RUC; código de inscripción del banco de datos de socios/créditos.
7. ¿La cooperativa tiene obligaciones de reporte ante su supervisor sectorial (SBS)? `[VERIFICAR: fuera de knowledge/]`

## 10. Siguiente paso
☐ Cerrar como evento ☒ Pasar a `brecha-evaluacion-severidad`

---
*Borrador de apoyo. Debe validarlo el Oficial de Datos Personales / responsable de seguridad.*
